% AN24_06 -- Range-Doppler basics
% Evaluate the range-Doppler map for a single channel
clear;
close all;

% (1) Connect to DemoRad: Check if Brd exists: Problem with USB driver
% (3) Configure RX
% (4) Configure TX
% (5) Start Measurements
% (6) Configure calculation of range profile and range doppler map for
% channel 1

c0          =   3e8;
%--------------------------------------------------------------------------
% Include all necessary directories
%--------------------------------------------------------------------------
CurPath = pwd();
addpath([CurPath,'/../../PNet']);
addpath([CurPath,'/../../UsbMex']);
addpath([CurPath,'/../../Class']);

%--------------------------------------------------------------------------
% Setup Connection
%--------------------------------------------------------------------------
Brd         =   TinyRad('RadServe', '127.0.0.1');

Brd.BrdRst();

%--------------------------------------------------------------------------
% Software Version
%--------------------------------------------------------------------------
Brd.BrdDispSwVers();

%--------------------------------------------------------------------------
% Load Calibration Data
%--------------------------------------------------------------------------
CalDat = Brd.BrdGetCalDat();

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
Cfg.fStrt = 24.00e9;                    %   Start frequency   
Cfg.fStop = 24.25e9;                    %   Stop frequency
Cfg.TRampUp = 512e-6;                   %   UpChirp duration
Cfg.Perd = 0.6e-3;                      %   Period between measurements
Cfg.N = 512;                            %   Number of samples taken at start of chirp 
Cfg.Seq = [1];                          %   Antenna transmit sequence
Cfg.CycSiz = 2;                         %   Number of buffers in the acquisition framework 2
Cfg.FrmSiz = 200;                       %   Number of chirp sequences for one measurement cycle
Cfg.FrmMeasSiz = 64;                    %   Number of chirps sequences for collecting IF data

Brd.RfMeas(Cfg);

%--------------------------------------------------------------------------
% Read actual configuration
%--------------------------------------------------------------------------
NrChn           =   Brd.Get('NrChn');
N               =   Brd.Get('N');
fs              =   Brd.Get('fs');

%--------------------------------------------------------------------------
% Configure FMCW System
%--------------------------------------------------------------------------
Brd.Computation.SetParam('fStrt', Cfg.fStrt);
Brd.Computation.SetParam('fStop', Cfg.fStop);
Brd.Computation.SetParam('TRampUp', Cfg.TRampUp);
Brd.Computation.SetParam('fs', fs);
Brd.Computation.SetParam('FuSca', Brd.FuSca);

%--------------------------------------------------------------------------
% Configure Range Profile
%--------------------------------------------------------------------------
Brd.Computation.SetParam('Range_NFFT', 2.^ceil(log2(Cfg.N * 2)));
% Set the minimum and maximum range for returning the range profiles
Brd.Computation.SetParam('Range_RMin', 0);
Brd.Computation.SetParam('Range_RMax', 50);
Brd.Computation.SetParam('Range_SubtractMean', 1);

%--------------------------------------------------------------------------
% Configure Doppler
%--------------------------------------------------------------------------
Brd.Computation.SetParam('Tp', Cfg.Perd);
Brd.Computation.SetParam('Np', Cfg.FrmMeasSiz);
Brd.Computation.SetParam('Vel_NFFT', 2.^ceil(log2(Cfg.FrmMeasSiz * 2)));

Brd.Computation.SetType('RangeDoppler');

vRange = Brd.Computation.GetRangeBins();
vVel   = Brd.Computation.GetVelBins();

disp('Get Measurement data')
for Idx = 1:1000
    
    Data        =   Brd.BrdGetData(1); 
        
    RD          =   abs(Data(:,:,1));

    figure(1)
    imagesc(vVel,vRange,20.*log10(RD));

    drawnow
    
end

clear Brd