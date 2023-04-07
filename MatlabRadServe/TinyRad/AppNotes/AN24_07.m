% AN24_07 -- Calculate DBF with two TX antenna
%
% (1) Connect to TinyRad: Check if Brd exists: Problem with USB driver
% (3) Configure RX
% (4) Configure TX
% (5) Start Measurements and configure MIMO mode with switching between TX
% (6) Configure calculation of range profile and DBF
% (7) Measure and eveluate cost function

clear all;
close all;

% Configure script
Disp_FrmNr          =   1;
Disp_TimSig         =   1;      % display time signals
Disp_JOpt           =   1;      % display cost function for DBF

%--------------------------------------------------------------------------
% Include all necessary directories
%--------------------------------------------------------------------------
CurPath = pwd();
addpath([CurPath,'/../../UsbMex']);
addpath([CurPath,'/../../Class']);

%--------------------------------------------------------------------------
% Define Constants
%--------------------------------------------------------------------------
c0 = 299792458; 

%--------------------------------------------------------------------------
% Configure Script
%--------------------------------------------------------------------------
% ConSel = 0; Use USB Mex file to communicate directly with TinyRad
% ConSel > 0; Use RadServe to communicate with TinyRad; 
ConSel = 1;

%--------------------------------------------------------------------------
% Setup Connection: open board object
%--------------------------------------------------------------------------
if ConSel > 0
    Brd     =   TinyRad('RadServe', '127.0.0.1');
else
    Brd     =   TinyRad();
end

%--------------------------------------------------------------------------
% Reset Board and Enable Power Supply
%--------------------------------------------------------------------------
Brd.BrdRst();

%--------------------------------------------------------------------------
% Software Version
%--------------------------------------------------------------------------
Brd.BrdDispSwVers();

%--------------------------------------------------------------------------
% Read calibration data
% Generate cal data for Tx1 and Tx2
%--------------------------------------------------------------------------
CalData     =   Brd.BrdGetCalDat();

%--------------------------------------------------------------------------
% Enable Receive Chips
%--------------------------------------------------------------------------
Brd.RfRxEna();

%--------------------------------------------------------------------------
% Configure Transmitter (Antenna 0 - 2, Pwr 0 - 100)
%--------------------------------------------------------------------------
Brd.RfTxEna(1, 100);


%--------------------------------------------------------------------------
% Configure Up-Chirp and timing for the measurements
%--------------------------------------------------------------------------
% Activate anatenna 1 and then antenna 2 and collect the IF data 
% Measurement is repeated with TInt = Cfg.Perd*numel(Cfg.Seq)*Cfg.FrmSiz
% The frame size can be used to control the interval for repeating the measurement

Cfg.fStrt       =   24.00e9;                    %   Start frequency   
Cfg.fStop       =   24.25e9;                    %   Stop frequency
Cfg.TRampUp     =   512e-6;                     %   UpChirp duration
Cfg.Perd        =   0.6e-3;                     %   Period between measurements
Cfg.N           =   512;                        %   Number of samples taken at start of chirp 
Cfg.Seq         =   [1, 2];                     %   Antenna transmit sequence
Cfg.CycSiz      =   2;                          %   Number of buffers in the acquisition framework 2
Cfg.FrmSiz      =   100;                        %   Number of chirp sequences for one measurement cycle
Cfg.FrmMeasSiz  =   1;                          %   Number of chirps sequences for collecting IF data

Brd.RfMeas(Cfg);

%--------------------------------------------------------------------------
% Read actual configuration
%--------------------------------------------------------------------------
NrChn           =   Brd.Get('NrChn');
N               =   Brd.Get('N');
fs              =   Brd.Get('fs');

%--------------------------------------------------------------------------
% Configure Signal Processing
%--------------------------------------------------------------------------
% Processing of range profile
NFFT                =   2^12;
Win2D               =   Brd.hanning(N-1,2*NrChn-1);
ScaWin              =   sum(Win2D(:,1));
kf                  =   Brd.RfGet('kf');
vRange              =   [0:NFFT-1].'./NFFT.*fs.*c0/(2.*kf);

% Configure range interval to be displayed
RMin                =   0.5;
RMax                =   10;

[Val RMinIdx]       =   min(abs(vRange - RMin));
[Val RMaxIdx]       =   min(abs(vRange - RMax));
vRangeExt           =   vRange(RMinIdx:RMaxIdx);

% Window function for receive channels
NFFTAnt         =   256;
WinAnt          =   Brd.hanning(2*NrChn-1);
ScaWinAnt       =   sum(WinAnt);
WinAnt2D        =   repmat(WinAnt.',numel(vRangeExt),1);
vAngDeg         =   asin(2*[-NFFTAnt./2:NFFTAnt./2-1].'./NFFTAnt)./pi.*180;


% Select virtual channels for processing
% Remove the overlapping channel
AntIdx          =   [1:4,6:8].';

% Calibration data for the selected channesl
CalData         =   CalData(AntIdx);
mCalData        =   repmat(CalData.',N-1,1);

% Positions for polar plot of cost function
vU              =   linspace(-1,1,NFFTAnt);
[mRange , mU]   =   ndgrid(vRangeExt,vU);
mX              =   mRange.*mU;
mY              =   mRange.*cos(asin(mU));


for Idx = 1:1000
    
    % Record data for Tx1 and Tx2
    Data            =   Brd.BrdGetData(); 

    if Disp_FrmNr > 0
        % Framenumber is used to check measurement sequence.
        % Odd Framenumbers are for TX1 and even frame numbers for TX2
        % If a frame is missing: DBF processing will fail!!
        FrmCntr         =   Data(1,:);
        disp(['Cyc: ', num2str(FrmCntr)]);
    end
    % Format data for virtual array and remove overlapping element
    DataA           =   [Data(1:N,:), Data(N+1:2*N,:)];
    DataV           =   DataA(2:end,AntIdx);
    
    % Calculate range profile including calibration
    RP          =   fft(DataV.*Win2D.*mCalData,NFFT,1).*Brd.FuSca/ScaWin;
    RPExt       =   RP(RMinIdx:RMaxIdx,:); 
    
    if Disp_TimSig > 0      
        % Display time signals
        figure(1)
        plot(DataA(2:end,:));
        grid on;
        xlabel('n ( )');
        ylabel('u (LSB)');   
    end
    
    if Disp_JOpt > 0
        % calculate fourier transform over receive channels
        JOpt        =   fftshift(fft(RPExt.*WinAnt2D,NFFTAnt,2)/ScaWinAnt,2);

        % normalize cost function
        JdB         =   20.*log10(abs(JOpt));
        JMax        =   max(JdB(:));
        JNorm       =   JdB - JMax;
        JNorm(JNorm < -35)  =   -35;    



        figure(2);
        surf(mX,mY, JNorm); 
        shading flat;
        view(0,90);
        axis equal
        xlabel('x (m)');
        ylabel('y (m)');
        colormap('jet');
    end

    
    drawnow;  
end

Brd.BrdRst();
Brd.BrdPwrDi();
