% Getting Started
close all;

% (1) Connect to TinyRad
% (2) Read board UID to verify connection to board


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
ConSel = 0;

%--------------------------------------------------------------------------
% Setup Connection: open board object
%--------------------------------------------------------------------------
if ConSel > 0
    Brd     =   TinyRad('RadServe', '127.0.0.1');
else
    Brd     =   TinyRad();
end

% display software version
Brd.BrdDispSwVers()

% read UID of board
Uid     =   Brd.BrdGetUID();

Brd.BrdDispInf();


clear Brd;