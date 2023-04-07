% AN24_05 -- Calculate DBF with one TX antenna
clear all;
close all;

% (1) Connect to TinyRad: Check if Brd exists: Problem with USB driver
% (3) Configure RX
% (4) Configure TX
% (5) Start Measurements
% (6) Configure calculation of range profile and DBF
% (7) Measure and eveluate cost function

% Configure script
Disp_FrmNr          =   1;
Disp_TimSig         =   1;      % display time signals
Disp_RP             =   1;      % display range profile
Disp_JOpt           =   1;      % display cost function for DBF

c0 = 299792458;
%--------------------------------------------------------------------------
% Include all necessary directories
%--------------------------------------------------------------------------
CurPath = pwd();
addpath([CurPath,'/../../UsbMex']);
addpath([CurPath,'/../../Class']);

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

Brd.BrdRst();

%--------------------------------------------------------------------------
% Software Version
%--------------------------------------------------------------------------
Brd.BrdDispSwVers();

%--------------------------------------------------------------------------
% Configure Receiver
%--------------------------------------------------------------------------
Brd.RfRxEna();
TxPwr           =   100;
%--------------------------------------------------------------------------
% Configure Transmitter (Antenna 0 - 2, Pwr 0 - 100)
%--------------------------------------------------------------------------
Brd.RfTxEna(1, TxPwr);

%--------------------------------------------------------------------------
% Read calibration data from the EEPROM
% The TinyRad board Revision > R 1.3.0 use equal length and calibration
% data can be replaced with ones
%--------------------------------------------------------------------------
CalDat          =   Brd.BrdGetCalDat();
CalDat          =   CalDat(1:4);

%--------------------------------------------------------------------------
% Configure Up-Chirp and timing for the measurements
%--------------------------------------------------------------------------
Cfg.fStrt       =   24.00e9;                    %   Start frequency   
Cfg.fStop       =   24.25e9;                    %   Stop frequency
Cfg.TRampUp     =   256e-6;                     %   UpChirp duration
Cfg.Perd        =   1e-3;                       %   Period between measurements
Cfg.N           =   256;                        %   Number of samples taken at start of chirp 
Cfg.Seq         =   [1];                        %   Antenna transmit sequence
Cfg.CycSiz      =   2;                          %   Number of buffers in the acquisition framework 2
Cfg.FrmSiz      =   200;                        %   Number of chirp sequences for one measurement cycle
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
Win2D           =   Brd.hanning(N-1,NrChn);
ScaWin          =   sum(Win2D(:,1));
NFFT            =   2^12;
kf              =   (Cfg.fStop - Cfg.fStrt)/Cfg.TRampUp;
vRange          =   [0:NFFT-1].'./NFFT.*fs.*c0/(2.*kf);

RMin            =   1;
RMax            =   10;

[Val RMinIdx]   =   min(abs(vRange - RMin));
[Val RMaxIdx]   =   min(abs(vRange - RMax));
vRangeExt       =   vRange(RMinIdx:RMaxIdx);

% Window function for receive channels
NFFTAnt         =   256;
WinAnt          =   Brd.hanning(NrChn);
ScaWinAnt       =   sum(WinAnt);
WinAnt2D        =   repmat(WinAnt.',numel(vRangeExt),1);
vAngDeg         =   asin(2*[-NFFTAnt./2:NFFTAnt./2-1].'./NFFTAnt)./pi*180;

% Calibration data
mCalData        =   repmat(CalDat.',N-1,1);

% Positions for polar plot of cost function
vU              =   linspace(-1,1,NFFTAnt);
[mRange , mU]   =   ndgrid(vRangeExt,vU);
mX              =   mRange.*mU;
mY              =   mRange.*cos(asin(mU));

FrmNrOld = 0;

%--------------------------------------------------------------------------
% Measure and calculate DBF
%--------------------------------------------------------------------------
for MeasIdx     =   1:1000

    Data        =   Brd.BrdGetData();

    if Disp_FrmNr > 0
        disp(num2str(Data(1,:)))
    end     
    
    % Remove Framenumber from processing
    Data = Data(2:end,:);
    
    if Disp_TimSig > 0      
        % Display time signals
        figure(1)
        plot(Data(:,:));
        grid on;
        xlabel('n ( )');
        ylabel('u (LSB)');   
    end    
    
    % Calculate range profile including calibration
    RP          =   fft(Data.*Win2D.*mCalData,NFFT,1).*Brd.FuSca/ScaWin;
    RPExt       =   RP(RMinIdx:RMaxIdx,:);    
    
    if Disp_RP> 0 
        %Display range profile
        figure(2)
        plot(vRangeExt, 20.*log10(abs(RPExt)));
        grid on;
        xlabel('R (m)');
        ylabel('X (dBV)');
        axis([vRangeExt(1) vRangeExt(end) -120 -40])
    end
    

    
    if Disp_JOpt > 0
        % calculate fourier transform over receive channels
        JOpt        =   fftshift(fft(RPExt.*WinAnt2D,NFFTAnt,2)/ScaWinAnt,2);

        % normalize cost function
        JdB         =   20.*log10(abs(JOpt));
        JMax        =   max(JdB(:));
        JNorm       =   JdB - JMax;
        JNorm(JNorm < -25)  =   -25;    

        figure(3);
        surf(mX,mY, JNorm); 
        shading flat;
        view(0,90);
        axis equal
        xlabel('x (m)');
        ylabel('y (m)');
        colormap('jet');
    end
    
    drawnow();
    
end


clear Brd;