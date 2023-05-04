% AN24_10 -- FMCW Basics 
clear;
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
Brd         =   TinyRad('RadServe', '127.0.0.1');

Brd.ReplayFile('Tst3', 1, 1);

%--------------------------------------------------------------------------
% Read actual configuration
%--------------------------------------------------------------------------
NrChn           =   Brd.Get('NrChn');
N               =   Brd.Get('N');
NumFrms         =   Brd.Get('FileSize');

for Idx = 1:NumFrms
    
    Data        =   Brd.BrdGetData(); 
    
    disp(['Cycle:', num2str(Data(1))])
    
    figure(2)
    plot(Data)
    drawnow()
    
   
end

Brd.StopReplayFile();

clear Brd;
