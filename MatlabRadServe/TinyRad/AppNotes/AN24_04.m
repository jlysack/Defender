% AN24_04 -- Accessing Calibration Data 
clear all;
close all;

% (1) Connect to DemoRad: Check if Brd exists: Problem with USB driver
% (2) Read Calibration Data
% (3) Read Calibration Information

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

clear Brd;