% AN24_04 -- Accessing Calibration Data 
clear;
close all;

% (1) Connect to DemoRad: Check if Brd exists: Problem with USB driver
% (2) Read Calibration Data
% (3) Read Calibration Information

%--------------------------------------------------------------------------
% Include all necessary directories
%--------------------------------------------------------------------------
CurPath = pwd();
addpath([CurPath,'/../../DemoRadUsb']);
addpath([CurPath,'/../../Class']);

%--------------------------------------------------------------------------
% Setup Connection
%--------------------------------------------------------------------------
Brd         =   TinyRad();

%--------------------------------------------------------------------------
% Software Version
%--------------------------------------------------------------------------
Brd.BrdDispSwVers();

%--------------------------------------------------------------------------
% Read the positions of the transmit and receive antennas
%--------------------------------------------------------------------------
TxPosn          =   Brd.RfGet('TxPosn');
RxPosn          =   Brd.RfGet('RxPosn');

%--------------------------------------------------------------------------
% Display the calibration information
%--------------------------------------------------------------------------
%Brd.BrdDispCalInf();

CalDat          =   Brd.BrdGetCalDat()

CalInf          =   Brd.BrdGetCalInf()
