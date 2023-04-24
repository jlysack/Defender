% Getting Started
close all;

% (1) Connect to TinyRad
% (2) Read board UID to verify connection to board


%--------------------------------------------------------------------------
% Include all necessary directories
%--------------------------------------------------------------------------
CurPath = pwd();
addpath([CurPath,'/../../DemoRadUsb']);
addpath([CurPath,'/../../Class']);

%--------------------------------------------------------------------------
% Setup Connection: open board object
%--------------------------------------------------------------------------
Brd     =   TinyRad();

% display software version
Brd.BrdDispSwVers()

% read UID of board
Uid     =   Brd.BrdGetUID();

Brd.BrdDispInf();


clear Brd;
