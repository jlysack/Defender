% AN24_06 -- Range-Doppler basics
% Evaluate the range-Doppler map for a single channel
clear all;
close all;

% (1) Connect to DemoRad: Check if Brd exists: Problem with USB driver
% (3) Configure RX
% (4) Configure TX
% (5) Start Measurements
% (6) Configure calculation of range profile and range doppler map for
% channel 1

% Configure script
Disp_FrmNr          =   1;
Disp_TimSig         =   1;      % display time signals
Disp_RP             =   0;      % display range profile
Disp_RD             =   1;      % display range-Doppler map
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
TxPwr           =   80;

%--------------------------------------------------------------------------
% Configure Transmitter (Antenna 0 - 2, Pwr 0 - 100)
%--------------------------------------------------------------------------
Brd.RfTxEna(1, TxPwr);

%--------------------------------------------------------------------------
% Configure Up-Chirp and timing for the measurements
%--------------------------------------------------------------------------
Cfg.fStrt       =   24.00e9;                    %   Start frequency   
Cfg.fStop       =   24.25e9;                    %   Stop frequency
Cfg.TRampUp     =   512e-6;                     %   UpChirp duration
Cfg.Perd        =   0.6e-3;                     %   Period between measurements
Cfg.N           =   512;                        %   Number of samples taken at start of chirp 
Cfg.Seq         =   [1];                        %   Antenna transmit sequence
Cfg.CycSiz      =   2;                          %   Number of buffers in the acquisition framework 2
Cfg.FrmSiz      =   400;                       %   Number of chirp sequences for one measurement cycle
Cfg.FrmMeasSiz  =   64;                         %   Number of chirps sequences for collecting IF data


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
Win2D           =   Brd.hanning(Cfg.N-1,Cfg.FrmMeasSiz);
ScaWin          =   sum(Win2D(:,1));
NFFT            =   2^12;
NFFTVel         =   2^12;
kf              =   (Cfg.fStop - Cfg.fStrt)/Cfg.TRampUp;
vRange          =   [0:NFFT-1].'./NFFT.*fs.*c0/(2.*kf);
fc              =   (Cfg.fStop + Cfg.fStrt)/2;

RMin            =   0;
RMax            =   100;

[Val RMinIdx]   =   min(abs(vRange - RMin));
[Val RMaxIdx]   =   min(abs(vRange - RMax));
vRangeExt       =   vRange(RMinIdx:RMaxIdx);

WinVel          =   Brd.hanning(Cfg.FrmMeasSiz);
ScaWinVel       =   sum(WinVel);
WinVel2D        =   repmat(WinVel.',numel(vRangeExt),1);

vFreqVel        =   [-NFFTVel./2:NFFTVel./2-1].'./NFFTVel.*(1/Cfg.Perd);
vVel            =   vFreqVel*c0/(2.*fc); 

%--------------------------------------------------------------------------
% Measure and calculate range-Doppler Map
%--------------------------------------------------------------------------
% Select channel to be processed. ChnSel <= NrChn
ChnSel          =   1;

for MeasIdx     =   1:100
    
    Data        =   Brd.BrdGetData();
    if Disp_FrmNr  > 0
        disp(num2str(Data(1,:)))
    end
    % Reshape measurement data for range doppler processing
    % 2D array with [N, NLoop]
    MeasChn   =     reshape(Data(:,ChnSel),Cfg.N, Cfg.FrmMeasSiz);
    
    % Calculate range profile including calibration
    RP          =   fft(MeasChn(2:end,:).*Win2D,NFFT,1).*Brd.FuSca/ScaWin;
    RPExt       =   RP(RMinIdx:RMaxIdx,:);    

    RD          =   fft(RPExt.*WinVel2D, NFFTVel, 2)./ScaWinVel;
    RD          =   fftshift(RD, 2);
    
    if Disp_TimSig > 0
        % Display time signals
        figure(1)
        plot(MeasChn(2:end,:));
        grid on;
        xlabel('n ( )');
        ylabel('u (LSB)');     
    end
    
    if Disp_RP > 0
        % Display range profile
        figure(2)
        plot(vRangeExt, 20.*log10(abs(RPExt)));
        grid on;
        xlabel('R (m)');
        ylabel('X (dBV)');
        axis([vRangeExt(1) vRangeExt(end) -120 -40])
    end
    
    if Disp_RD > 0
        % Display range doppler map
        figure(3)
        imagesc(vVel, vRangeExt, 20.*log10(abs(RD)));
        grid on;
        xlabel('v (m/s)');
        ylabel('R (m)');
        colormap('jet')
    end

    drawnow()

end

clear Brd