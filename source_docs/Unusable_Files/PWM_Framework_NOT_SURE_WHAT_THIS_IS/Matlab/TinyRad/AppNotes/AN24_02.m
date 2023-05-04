% AN24_02 -- FMCW Basics 
clear;
close all;

% (1) Connect to TinyRad: Check if Brd exists: Problem with USB driver
% (3) Configure RX
% (4) Configure TX
% (5) Start Measurements
% (6) Configure calculation of range profile
% Configure script
Disp_FrmNr          =   1;
Disp_TimSig         =   1;
Disp_RP             =   1;

c0 = 299792458;
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
% Configure Transmitter (Antenna 0 - 2, Pwr 0 - 100)
%--------------------------------------------------------------------------
TxPwr           =   100;
Brd.RfTxEna(1, TxPwr);

%--------------------------------------------------------------------------
% Configure Up-Chirp and timing for the measurements
%--------------------------------------------------------------------------
Cfg.fStrt       =   24.00e9;                    %   Start frequency   
Cfg.fStop       =   24.25e9;                    %   Stop frequency
Cfg.TRampUp     =   512e-6;                     %   UpChirp duration 
Cfg.Perd        =   100e-3;                     %   Period between measurements
Cfg.N           =   512;                        %   Number of samples taken at start of chirp 
Cfg.Seq         =   [1];                        %   Antenna transmit sequence
Cfg.CycSiz      =   2;                          %   Number of buffers in the acquisition framework 2 are required
Cfg.FrmSiz      =   2;                          %   Number of chirp sequences for one measurement cycle
Cfg.FrmMeasSiz  =   1;                          %   Number of chirps sequences for collecting IF data

Brd.RfMeas(Cfg);


%--------------------------------------------------------------------------
% Read actual configuration
%--------------------------------------------------------------------------
N               =   Brd.Get('N');
NrChn           =   Brd.Get('NrChn');
fs              =   Brd.Get('fs');

%--------------------------------------------------------------------------
% Check TCP/IP data rate:
% 16 Bit * Number of Enabled Channels * Number of Samples are measureed in
% the interval TInt. If the data rate is too high, than frames can be losed
%--------------------------------------------------------------------------
DataRate        =   16*NrChn*N.*Cfg.FrmMeasSiz./(Cfg.Perd*Cfg.FrmSiz);
disp(['DataRate: ', num2str(DataRate/1e6), ' MBit/s'])

%--------------------------------------------------------------------------
% Configure Signal Processing
%--------------------------------------------------------------------------
% Processing of range profile
NFFT                =   2^12;
Win                 =   Brd.hanning(N, NrChn);
ScaWin              =   sum(Win(:,1));
% Read back ramp slope: configured ramp slope can deviate from configured
kf                  =   Brd.RfGet('kf');
vRange              =   [0:NFFT-1].'./NFFT.*fs.*c0/(2.*kf);

disp('Get Measurement data')

tic
for Idx = 1:100
    
    % read data for configured measurement sequence
    Data        =   Brd.BrdGetData();    
    
    if Disp_FrmNr > 0
        % Show Cycle (buffer) number:
        disp(num2str(Data(1,:)))
    end 
        
    if Disp_TimSig > 0
        % Display sampled signals for the collected chirp
        figure(1)
        plot(Data(2:end,1:NrChn))
        grid on;
        xlabel('n ( )')
        ylabel('xIF (LSB)')
    end
    
    if Disp_RP > 0
        % Calculate range profile
        % Scale data to the input of the ADC in volt (Brd.FuSca)
        % ADC full scale constant; automatically calculated when ADC gain
        % is changed with Brd.Set('AfeGaindB')
        % Range profile is corrected with gain of window function and
        % additional factor two is used to scale the amplitude of the
        % signal as real input samples are processed
        RP          =   2*fft(Data.*Win,NFFT,1).*Brd.FuSca/ScaWin;
        
        figure(2)
        plot(vRange(1:NFFT./2),20.*log10(abs(RP(1:NFFT./2,:))))
        grid on;
        xlabel('R (m)')
        ylabel('RP (dBV)')
        
        
    end
        
    drawnow(); 
    
end

clear Brd;
