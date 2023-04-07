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
Brd = TinyRad('RadServe', '127.0.0.1');

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
TxPwr = 80;

%--------------------------------------------------------------------------
% Configure Transmitter (Antenna 0 - 2, Pwr 0 - 100)
%--------------------------------------------------------------------------
Brd.RfTxEna(1, TxPwr);

%--------------------------------------------------------------------------
% Configure Up-Chirp and timing for the measurements
%--------------------------------------------------------------------------
Cfg.fStrt = 24.00e9;                %   Start frequency   
Cfg.fStop = 24.25e9;                %   Stop frequency
Cfg.TRampUp = 512e-6;               %   UpChirp duration
Cfg.Perd = 0.6e-3;                  %   Period between measurements
Cfg.N = 512;                        %   Number of samples taken at start of chirp 
Cfg.Seq = [1];                      %   Antenna transmit sequence
Cfg.CycSiz = 2;                     %   Number of buffers in the acquisition framework 2
Cfg.FrmSiz = 100;                   %   Number of chirp sequences for one measurement cycle
Cfg.FrmMeasSiz = 64;                %   Number of chirps sequences for collecting IF data

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
Brd.Computation.SetParam('Range_RMin', 20);
Brd.Computation.SetParam('Range_RMax', 150);
Brd.Computation.SetParam('Range_SubtractMean', 1);

%--------------------------------------------------------------------------
% Configure Doppler
%--------------------------------------------------------------------------
Brd.Computation.SetParam('Tp', Cfg.Perd);
Brd.Computation.SetParam('Np', Cfg.FrmMeasSiz);
Brd.Computation.SetParam('Vel_NFFT', 2.^ceil(log2(Cfg.FrmMeasSiz * 2)));

%--------------------------------------------------------------------------
% Configure Angular Domain
%--------------------------------------------------------------------------
Brd.Computation.SetParam('Ang_NFFT', 128);
Brd.Computation.SetParam('Ang_Flip', 1);        % Flip Angle 
Brd.Computation.SetParam('Ang_Interpolate', 1);

%--------------------------------------------------------------------------
% Configure Detection
%--------------------------------------------------------------------------
% varying the detection threshold
%  - Thres_Mult is the multiplication factor for the threshold estimation
%  - Thres_Old represents how slow/fast the threshold reacts to changes
Brd.Computation.SetParam('Thres_Mult', 2.8);
Brd.Computation.SetParam('Thres_Old', 0.9);

% Configure Kalman Filter
Brd.Computation.SetParam('Track_SigmaX', 0.1);
Brd.Computation.SetParam('Track_SigmaY', 0.1);
% Update Interval for Tracking algorithm
Brd.Computation.SetParam('Track_dT', Cfg.FrmSiz*Cfg.Perd)

% Define Size of Cluster to be assigned to existing track
Brd.Computation.SetParam('Track_VarX', 0.04);
Brd.Computation.SetParam('Track_VarY', 0.04);
Brd.Computation.SetParam('Track_VarVel', 0.5);
Brd.Computation.SetParam('TT_NumDetections', 50);

% Output detections with cluster information for Tracks
Brd.Computation.SetParam('TT_OutputCluster', 1);

Brd.Computation.SetType('TargetTracker');

disp('Get Measurement data')
for Idx = 1:1000
    
    Data        =   Brd.BrdGetData();
        
    if numel(Data.Tracks) > 0
        
%        Data of Tracker contains struct array with the following entries
%         Id
%         X
%         Y
%         Vel
%         VelX
%         VelY
%         Mag
%         VarX
%         VarY
%         HistX
%         HistY
        
        if numel(Data.Detections) > 0
            DetX        =   [Data.Detections.X];
            DetY        =   [Data.Detections.Y];
            DetTrack    =   [Data.Detections.Track];
        else
            DetX        =   [];
            DetY        =   [];
            DetTrack    =   [];            
        end
        figure(1)
        clf;
        % also plot untracked detections
        if numel(Data.Detections) > 0
            IdcsNotAssigned  = find(DetTrack == -1);
            plot(DetX(IdcsNotAssigned), DetY(IdcsNotAssigned), 'kx')
            hold on;
            axis([-50 50 30 150])
        end
        
        for Idx = 1:numel(Data.Tracks)
            
            hLine =  plot(Data.Tracks(Idx).X, Data.Tracks(Idx).Y, 'o', 'LineWidth', 2);
            hold on;
            Color   =   get(hLine, 'Color');
            plot(Data.Tracks(Idx).HistX, Data.Tracks(Idx).HistY,'-', 'Color', Color)
            
            IdcsTrack   =   find(DetTrack == Data.Tracks(Idx).Id);
            plot(DetX(IdcsTrack), DetY(IdcsTrack),'x', 'Color', Color)
            
            grid on;
            axis([-50 50 30 150])
        end
        %axis([-75 75 0 100])
    end
    
end

