% AN24_10 -- FMCW Basics 
clear all;
close all;

% (1) Connect to TinyRad: Check if Brd exists: Problem with USB driver
% (3) Configure RX
% (4) Configure TX
% (5) Start Measurements
% (6) Configure calculation of range profile

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

% Reset prvious configuration if board was already configured
Brd.BrdRst();

%--------------------------------------------------------------------------
% Software Version
%--------------------------------------------------------------------------
Brd.BrdDispSwVers();

%--------------------------------------------------------------------------
% Configure Receiver
%--------------------------------------------------------------------------
Brd.RfRxEna();

%--------------------------------------------------------------------------
% Load Calibration Data
%--------------------------------------------------------------------------
CalDat = Brd.BrdGetCalDat();

%--------------------------------------------------------------------------
% Configure Transmitter (Antenna 0 - 2, Pwr 0 - 100)
%--------------------------------------------------------------------------
TxPwr = 100;
Brd.RfTxEna(1, TxPwr);

%--------------------------------------------------------------------------
% Configure Up-Chirp and timing for the measurements
%--------------------------------------------------------------------------
Cfg.fStrt = 24.00e9;            %   Start frequency   
Cfg.fStop = 24.25e9;            %   Stop frequency
Cfg.TRampUp = 512e-6;           %   UpChirp duration
Cfg.Perd = 0.6e-3;              %   Period between measurements
Cfg.N = 512;                    %   Number of samples taken at start of chirp 
Cfg.Seq = [1];                  %   Antenna transmit sequence
Cfg.CycSiz = 2;                 %   Number of buffers in the acquisition framework 2
Cfg.FrmSiz = 100;                %   Number of chirp sequences for one measurement cycle
Cfg.FrmMeasSiz = 90;            %   Number of chirps sequences for collecting IF data

Brd.RfMeas(Cfg);

n = [0:Cfg.N-1].';
%--------------------------------------------------------------------------
% Read actual configuration
%--------------------------------------------------------------------------
NrChn = Brd.Get('NrChn');
N = Brd.Get('N');
fs = Brd.Get('fs');

%--------------------------------------------------------------------------
% Store Cfg Parameters to HDF5 file
%--------------------------------------------------------------------------
CfgFields = fields(Cfg);
for Idx = 1:numel(CfgFields)
    
    if eval(['numel(Cfg.',CfgFields{Idx},')']) > 1
        Brd.SetFileParam(['Cfg_',CfgFields{Idx}], eval(['Cfg.',CfgFields{Idx}]), 'ARRAY64');
    else
        Brd.SetFileParam(['Cfg_',CfgFields{Idx}], eval(['Cfg.',CfgFields{Idx}]));
    end
    
end

NrUsbPkts = 10000;
MeasTim = NrUsbPkts*Cfg.FrmSiz*Cfg.Perd;
disp(['Measurement duration: ', num2str(MeasTim), ' s'])


Brd.CreateFile('TinyRad_Traf1', NrUsbPkts);
pause(ceil(MeasTim)+2);
Brd.CloseFile();

Brd.BrdDispSwVers();
Brd.BrdRst();

clear Brd;
