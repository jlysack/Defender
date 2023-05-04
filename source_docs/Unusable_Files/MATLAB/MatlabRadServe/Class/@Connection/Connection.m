%< @file        Connection.m                                                                
%< @author      Susanne Rechbauer (SuRe)                                                  
%< @date        2017-03          
%< @brief       Connection class for the connection to the boards over Matlab Mex and RadServe
%< @version     2.1.0

%< Version 2.2.0
%< Correct  Error with video handle

%< Version 2.3.0
%< Add cDebugInf paramters
%< Add function to readback video properties
%< Add Parameter cUsbNrTx

%< Version 2.4.0
%< ReplayFile - Multiple Videos
%< Updated: DispVideo, GetVideoProperties, GetVideo to select video if more than one is available
%< Added:   DispAllVideos, GetAllVideoProperties, GetAllVideos

%< Version 2.4.1
%< Updated: CreateFileExtension and GetExtensionPort

%< Version 2.4.2
%< Add function ConSetCfgTimeout

%< Version 2.5.0
%< Add function ConAppendTimestamp to notify RadServe to add timestamp to data (replay and dataport)

%< Version 2.5.1
%< Add Parameter cTimStampRS

%< Version 2.6.0
%< Added Parameters: cDPVideo, cDevIdx, cVideoFrmsColl
%< Added: CfgRadServe [AddVideoToFile, AddVideoToDataPort, AddTimStmpToFilename, LogDataPortToFile, HdfPath], CfgRadServe_Extension (Path, Selection, Param), CfgRadServe_ExtensionFile (AddChn, SplitChn)
%<   CfgRadServe_CameraList, CfgRadServe_CameraDeselectAll, CfgRadServe_CameraSelect, CfgRadServe_CameraDeselect
%<   PollReplayClosed, PollDataPortClosed, PollFileClosed
%< Updated: CreateFile, ReplayFile, ConSet
%< Obsolete: StopFile, CloseExtensionPort, AddVideo
%< Removed functions: CreateFileExtension, ReplayFileExtension, StopReplayFileExtension

%< Version 2.7.0
%< Updated: CfgRadServe_Camera functions
%< Added: cDataIdx

%< Version 2.7.1
%< Set to public: cExtMult

%< Version 2.7.2
%< Fix disconnect error

%< Version 2.7.3
%< Updated: CfgRadServe_Camera('Select'), set frame size
%< Updated: CfgRadServe_Camera('AddOptris'/'UpdateOptris') to allow storing raw data
%< Updated: GetVideo/GetAllVideos/DispVideo/DispAllVideos without cnt

%< Version 2.7.4
%< Added: cUid, board-selection via uid

%< Version 2.7.5
%< Error on OpenDevice stops the execution of the script

%< Version 2.8.0
%< support dataport functions of RadServe

%< Version 2.8.1
%< support internal range doppler/target list port or RadServe

%< Version 2.8.2
%< removed error message for setting Mult on internal configuration of range profile

%< Version 2.8.3
%< updated parameters for computation

%< Version 3.0.0
%< Merge classes for Radarbook2 and RadarLog

%< Version 3.0.1
%< Add ConForceSet for setting Mult

%< Version 3.1.0
%< Support TinyRad and RadServe v3.4.0

%< Version 3.1.1
%< Open Usb on SetTimeout

%< Version 3.1.2
%< Avoid continuous open/close for usb devices

%< Version 3.1.3
%< Add UID selection again

classdef Connection<handle
    
    properties (Access = protected)
        cType               =   'PNet';
        cIpAddr             =   '127.0.0.1';
        cCfgPort            =   8000;
        cDataPort           =   6000;
        cUid                =    [];

        %% RBK Specifics ----------------------
        cRbkIp              =   '192.168.1.1';
        cRbkCfg             =   8001;
        cRbkDat             =   6000;
        %%-------------------------------------

        cDevIdx             =    0;
        cDataOpened         =   -1;
        cReplay             =   -1;
        cReplayExt          =   -1;
        cExtSize            =    0;
        cDataIdx            =    0;

        cOpened             =   -1;
        cResponseOk         =   1;
        cResponseMsg        =   2;
        cResponseInt        =   3;
        cResponseData       =   4;
        cResponseDouble     =   5;
        cArmCmdBegin        =   hex2dec('6000');
        cArmCmdEnd          =   hex2dec('7FFF');
        cFpgaCmdBegin       =   hex2dec('9000');
        cFpgaCmdEnd         =   hex2dec('AFFF');
       
        cBufSiz             =   256;
        
        hCon                =   -1;
        hConDat             =   -1;
        hConDatTimeout      =    40;
        cPortOpen           =   -1;
        cPortNum            =    0;
        
        cDPVideo            =    0;
        hConVideo           =   [];
        cVideoPort          =   [];
        cVideoPortOpen      =   [];
        cVideoCols          =   [];
        cVideoRows          =   [];
        cVideoChn           =   [];
        cVideoRate          =   [];
        cVideoSize          =   [];
        cVideoFrames        =   [];
        cVideoFrmsColl      =   [];
        cVideoName          =   {};
        
        cMult               =   32;
        cDataPortKeepAlive  =   0;
        cNumPackets         =   0;
        
        cUsbNrTx            =   96;
        
        cCfgTimeout         =   100;
        cTimeout            =   -1;
        ConNew              =   0;
        
        cTimStampRS         =   0;
        
        Usb_Timeout         =   0;

        cDevType            =   'Unknown';
        
        cTinyCmdSend        =   0;
        cTinyDataSend       =   0;
        cTinyDataRead       =   0;
    end
    
    properties (Access = public)
        cDebugInf           =   0;
        cExtMult            =   0;

        Computation         =  [];
    end
    
    %% Constructor
    methods (Access = protected)
        % DOXYGEN ------------------------------------------------------
        %> @brief Class constructor
        %>
        %> Construct a class object to connect to the Radarlog or Radarbook with the USB Mex driver in Matlab or the RadServe
        %> Class can be inherited form Radarbook or RadarLog class
        %>
        %> @param[in]     stConType: Connection Type (string) 
        %>          -   <span style="color: #ff9900;"> 'PNet': </span>: TCP/IP stack with Mex file
        %>          -   <span style="color: #ff9900;"> 'Usb': </span>: USB connection
        %>          -   <span style="color: #ff9900;"> Tcp': </span>: Matlab TCP/IP stack requires instrumentation and control toolbox
        %>
        %> @param[in]     stIPAddr: IPAddress of Board '192.168.1.1' (string optional)  
        %>
        %> @return  Returns a object of the class with the desired connection settings   
        %>
        function obj = Connection (devType, stConType, varargin)
            if obj.cDebugInf > 10
                disp('Connection Initializer')
            end
            
            obj.cDevType = devType; % first arg must be dev type
            
            if (nargin < 2)
                stConType = 'Usb';
            end            
            
            if strcmp(obj.cDevType, 'RadarLog')
                % Set default values
                obj.cType       =   stConType;
                obj.cIpAddr     =   '127.0.0.1';
                obj.cCfgPort    =   8000;
                
                if numel(varargin) > 0
                    obj.cIpAddr         =   varargin{1};
                    if numel(varargin) > 1
                        obj.cCfgPort    =   varargin{2};
                        if numel(varargin) > 2
                            if ischar(varargin{3})
                                if (numel(varargin{3}) == 16)
                                    obj.cUid = [hex2dec(varargin{3}(1:8)) hex2dec(varargin{3}(9:16))];
                                else
                                    error('Uid too short');
                                end
                            end
                        else
                            obj.SetIndex(varargin{3});
                        end
                    end
                end
            elseif strcmp(obj.cDevType, 'Radarbook2')
                if numel(varargin) > 0
                    % Set default values
                    obj.cType           =   stConType;
                    obj.cRbkIp          =   '192.168.1.1';
                    obj.cRbkCfg         =   8001;             
                    obj.cRbkDat         =   6000 + floor(1000.*rand(1));
                    
                    if strcmp(stConType, 'RadServe')
                        obj.cIpAddr    =   varargin{1};
                        if numel(varargin) > 1
                            obj.cCfgPort =   varargin{2};
                            if numel(varargin) > 2
                                obj.cRbkIp = varargin{3};
                                if numel(varargin) > 3
                                    obj.cRbkCfg = varargin{4};
                                    if numel(varargin) > 4
                                        obj.cRbkDat = varargin{5};
                                    end
                                end
                            end
                        end
                        obj.cType = 'RadServe';
                    elseif numel(varargin) > 0
                        obj.cRbkIp = varargin{1};
                        if numel(varargin) > 1
                            obj.cRbkCfg = varargin{2};
                        end
                    end
                end
            elseif strcmp(obj.cDevType, 'TinyRad')
                % equal to RadarLog
                % Set default values
                obj.cType       =   stConType;
                obj.cIpAddr     =   '127.0.0.1';
                obj.cCfgPort    =   8000;
                
                if numel(varargin) > 0
                    obj.cIpAddr         =   varargin{1};
                    if numel(varargin) > 1
                        obj.cCfgPort    =   varargin{2};
                        if numel(varargin) > 2
                            if ischar(varargin{3})
                                if (numel(varargin{3}) == 16)
                                    obj.cUid = [hex2dec(varargin{3}(1:8)) hex2dec(varargin{3}(9:16))];
                                else
                                    error('Uid too short');
                                end
                            end
                        else
                            obj.SetIndex(varargin{3});
                        end
                    end
                end
                
                if strcmp(stConType, 'Usb')
                    %% set usb vid/pid to select tinyrad
                    USBnAny('setVid', uint16(hex2dec('064B')));
                    USBnAny('setPid', uint16(hex2dec('7823')));
                
                    USBnAny('setEp', 'par', 'in', uint8(1));
                    USBnAny('setEp', 'par', 'out', uint8(1));
                    USBnAny('setEp', 'uart', 'in', uint8(1));
                    USBnAny('setEp', 'uart', 'out', uint8(1));
                end
            end
            
            obj.Computation  =   Computation(obj);
            if strcmp(obj.cType, 'RadServe')
                obj.Computation.SetType('Raw');
            end
        end
    end % constructor
    
    %% Destructor
    methods (Access = public)    
        function delete (obj)
            disp('Delete class connection')
            if strcmp(obj.cType, 'RadServe') || strcmp(obj.cType, 'PNet')
                % close all connections
                if obj.hCon > -1
                    pnet(obj.hCon,'close');
                    obj.hCon = -1;
                end
                
                if obj.hConDat > -1
                    pnet(obj.hConDat, 'close');
                    obj.hConDat = -1;
                end
                
                for Idx = 1:numel(obj.hConVideo)
                    if obj.hConVideo(Idx) > -1
                        pnet(obj.hConVideo(Idx), 'close');
                        obj.hConVideo(Idx) = -1;
                    end
                end
            elseif strcmp(obj.cType, 'Usb')
                obj.UsbClose();
            end
            pause(0.2);
        end
    end % destructor
    
    %% Cmd Functions
    methods (Access = {?Connection, ?Computation})
        %   @function    CmdBuild                                                               
        %   @author      Haderer Andreas (HaAn)                                                  
        %   @date        2013-12-01          
        %   @brief       Build command for transmission to baseboard
        function Cmd     =   CmdBuild(obj, Ack, Cod, Data)
            RxData      =   zeros(1,1);            
            RxData      =   [RxData;Data(:)];
            Len         =   length(RxData);
            RxData(1)   =   2^24*Ack + 2^16*Len + Cod;
            Len         =   length(RxData);
            Cmd         =   uint32(RxData);
        end
        
        function CleanUpCmdExec(obj)
            if (obj.cTinyCmdSend == 1)
                Ret = USBnAny('recv32', int32(2048), 'uart');
            end
            
            if obj.ConNew > 0
                obj.UsbClose();
            end
        end
        
        function CleanUpDataSend(obj)
            if (obj.cTinyCmdSend == 1)
                if (obj.cTinyDataSend == 1)
                    % send 0 data
                    Data2048 = zeros(2048,1,'uint8');
                    USBnAny('send', uint8(Data2048), 'uart');

                    obj.CmdRecv();
                elseif (obj.cTinyDataSend == 2)
                    obj.CmdRecv();
                end
            end
        end
        
        function CleanUpDataRead(obj)
            if (obj.cTinyCmdSend == 1)
                if (obj.cTinyDataRead == 1)
                    % recv data
                    USBnAny('recv32', int32(2048), 'uart');

                    obj.CmdRecv();
                elseif (obj.cTinyDataRead == 2)
                    obj.CmdRecv();
                end
            end
            
            if obj.ConNew > 0
                obj.UsbClose();
            end
        end
        
        function   [Ret] = CmdExec(obj, Ack, Cod, Data, Open)
            cleanupObj = onCleanup(@obj.CleanUpCmdExec);
            
            if ~exist('Open','var')
                Ret =   obj.CmdSend(Ack, Cod, Data);
            else
                Ret =   obj.CmdSend(Ack, Cod, Data, Open);
            end
            Ret     =   obj.CmdRecv();
        end

        %   @function    CmdSend                                                               
        %   @author      Haderer Andreas (HaAn)                                                  
        %   @date        2013-12-01          
        %   @brief       Transmit command to ARM processor
        function    [Ret]   =   CmdSend(obj, Ack, Cod, Data, Open)
            Cmd                 =   obj.CmdBuild(Ack,Cod,Data);
            
            if strcmp(obj.cType, 'Usb')
                CmdBytes        =   obj.ToUint8(Cmd);                
                TxData          =   0;
                if obj.hCon > -1
                    TxData      =   1;
                    obj.ConNew      =   0;
                else
                    Dev             =   obj.UsbOpen();
                    if Dev > 0
                        obj.hCon        =   1;
                        TxData          =   1;
                        %obj.ConNew      =   1;
                    end
                end   
                
                if TxData > 0        
                    if strcmp(obj.cDevType, 'RadarLog')
                        USBnAny('send', uint8(CmdBytes), 'uart');
                    else
                        Len = uint16(numel(CmdBytes));
                        
                        Data2048 = zeros(2048,1,'uint8');
                        Data2048(1:2) = typecast(Len, 'uint8');
                        Data2048(3:(3+numel(CmdBytes)-1)) = CmdBytes;
                        
                        obj.cTinyCmdSend = 1;
                        USBnAny('send', uint8(Data2048), 'uart');
                    end
                end
               
            elseif strcmp(obj.cType,'PNet') 
                TxData  =   0;
                if obj.hCon > -1
                    TxData          =   1;
                    obj.ConNew      =   0;
                else
                    Ip = obj.cIpAddr;
                    Port = obj.cCfgPort;
                    if strcmp(obj.cDevType, 'Radarbook2')
                        Ip   = obj.cRbkIp;
                        Port = obj.cRbkCfg;
                    end
                    
                    obj.hCon    =   obj.OpenTcpipCom(Ip, Port);
                    if obj.hCon > -1
                        TxData          =   1;
                        obj.ConNew      =   1;
                    end
                end     
                
                if TxData > 0        
                    pnet(obj.hCon,'write',swapbytes(Cmd)); 
                end
            elseif strcmp(obj.cType, 'RadServe')
                if obj.hCon == -1
                    obj.hCon = obj.OpenTcpipCom(char(obj.cIpAddr), obj.cCfgPort);
                    if obj.hCon == -1
                        error('Couldn''t connect to RadServe');
                    end
                end
                
                if ~exist('Open','var')
                    Open = 1;
                end
                
                if obj.cOpened == -1 && Open == 1
                    if strcmp(obj.cDevType, 'RadarLog') || strcmp(obj.cDevType, 'TinyRad')
                        DevType = uint32(0);
                        if strcmp(obj.cDevType, 'TinyRad')
                            DevType = uint32(2);
                        end
                        %% change command to open with uid
                        if (numel(obj.cUid) == 2)
                            OpenData = [DevType uint32(obj.cDevIdx) obj.cUid];
                            CmdOpen = obj.CmdBuild(0, hex2dec('6103'), OpenData);
                            pnet(obj.hCon, 'write', swapbytes(CmdOpen));
                            Ret = obj.CmdRecv(1);

                            if (ischar(Ret))
                                error(Ret);
                            end

                            obj.cOpened = 1;
                        else
                            OpenData = [DevType uint32(obj.cDevIdx)];
                            CmdOpen = obj.CmdBuild(0, hex2dec('6103'), OpenData);
                            pnet(obj.hCon, 'write', swapbytes(CmdOpen));
                            Ret = obj.CmdRecv(1);

                            if (ischar(Ret))
                                error(Ret);
                            end

                            obj.cOpened = 1;
                            
%                             OpenData = [uint32(obj.cDevIdx)];
%                             % send command to set index on RadServe
%                             CmdSetIdx   = obj.CmdBuild(0, hex2dec('6113'), OpenData);      % use as default
%                             pnet(obj.hCon, 'write', swapbytes(CmdSetIdx));
%                             Ret         = obj.CmdRecv();
% 
%                             OpenData = [uint32(3)];
%                             % send command to open device on RadServe
%                             CmdOpen     = obj.CmdBuild(0, hex2dec('6120'), OpenData);      % use as default
%                             pnet(obj.hCon, 'write', swapbytes(CmdOpen));
%                             Ret         = obj.CmdRecv(1);
%                             if (ischar(Ret))
%                                 error(Ret);
%                             end
%                             obj.cOpened = 1;
                        end
                    else
                        stIp    = obj.cRbkIp;
                        Len     = length(stIp);
                        for Idx     = 1:(16-Len)
                            stIp  = [stIp ' '];
                        end
                        
                        OpenData = [uint32(1) typecast(uint8(stIp), 'uint32') obj.cRbkCfg obj.cRbkDat];
                        CmdOpen = obj.CmdBuild(0, hex2dec('6103'), OpenData);
                        pnet(obj.hCon, 'write', swapbytes(CmdOpen));
                        Ret = obj.CmdRecv(1);

                        if (ischar(Ret))
                            error(Ret);
                        end

                        obj.cOpened = 1;
                    end
                end
                pnet(obj.hCon, 'write', swapbytes(Cmd));
            else
                TxData  =   0;
                if obj.hCon > -1
                    TxData          =   1;
                    obj.ConNew      =   0;
                else
                    obj.hTcpCon         =   obj.OpenTcpipCom(obj.cIpAddr, obj.cCfgPort);
                    if strcmp(obj.hTcpCon.Status,'open')
                        obj.hCon        =   1;
                        TxData          =   1;
                        obj.ConNew      =   1;
                    else
                        obj.hCon        =   -1;
                    end
                end     
                
                if TxData > 0        
                    fwrite(obj.hTcpCon, swapbytes(Cmd), 'uint32');     
                end                
            end
            Ret     =   0;    
        end
        
        function Ret = DataSend(obj, Ack, Cod, Cmd, Data)
            cleanupObj = onCleanup(@obj.CleanUpDataSend);
            
            if strcmp(obj.cDevType, 'TinyRad')
                if strcmp(obj.cType, 'Usb')
                    obj.cTinyDataSend = 1;
                    Ret  = obj.CmdSend(Ack, Cod, Cmd);

                    DataBytes =   obj.ToUint8(Data);
                    TxData          =   0;
                    if obj.hCon > -1
                        TxData      =   1;
                    else
                        Dev             =   obj.UsbOpen();
                        if Dev > 0
                            obj.hCon        =   1;
                            TxData          =   1;
                            %obj.ConNew      =   1;
                        end
                    end   

                    if TxData > 0        
                        Len = uint16(numel(DataBytes));

                        Data2048 = zeros(2048,1,'uint8');
                        Data2048(1:2) = typecast(Len, 'uint8');
                        Data2048(3:(3+numel(DataBytes)-1)) = DataBytes;
                        obj.cTinyDataSend = 2;
                        USBnAny('send', uint8(Data2048), 'uart');
                    end

                    obj.cTinyDataSend = 3;
                    Ret  = obj.CmdRecv();
                    obj.cTinyDataSend = 0;
                elseif strcmp(obj.cType, 'RadServe')
                    CmdBytes = obj.CmdBuild(Ack, Cod, Cmd);
                                        
                    DataSend = [CmdBytes; Data'];
                    Ret = obj.CmdSend(0, hex2dec('6120'), DataSend);
                    Ret = obj.CmdRecv();
                end
            end
        end
        
        function Ret = DataRead(obj, Ack, Cod, DspCmd)
            cleanupObj = onCleanup(@obj.CleanUpDataRead);
            
            if strcmp(obj.cType, 'Usb') && strcmp(obj.cDevType, 'TinyRad')
                obj.cTinyDataRead = 1;
                CmdRet  = obj.CmdSend(Ack, Cod, DspCmd);
                
                TxData          =   0;
                if obj.hCon > -1
                    TxData      =   1;
                else
                    Dev             =   obj.UsbOpen();
                    if Dev > 0
                        obj.hCon        =   1;
                        TxData          =   1;
                        %obj.ConNew      =   1;
                    end
                end   
                
                if TxData > 0             
                    RdLen = DspCmd(3) * 2;
                    obj.cTinyDataRead = 2;
                    Ret   = USBnAny('recv32', int32(RdLen), 'uart');
                    while (numel(Ret) * 4 < RdLen)
                        Recv = USBnAny('recv32', int32(RdLen - numel(Ret) * 4), 'uart');
                        Ret = [Ret; Recv];
                    end
                    Ret   = typecast(Ret, 'int16');
                    Len   = numel(Ret);
                    Ret   = reshape(double(Ret), 4, Len/4);
                    Ret   = Ret.'; 
                end
                
                obj.cTinyDataRead = 3;
                CmdRet  = obj.CmdRecv();
                obj.cTinyDataRead = 0;
            end
        end

        %   @function       CmdRecv                                                               
        %   @author         Haderer Andreas (HaAn)                                                  
        %   @date           2013-12-01          
        %   @brief          Receive response from baseboard
        function    [Ret]   =   CmdRecv(obj, StopOnError);
            Ret     =   [];
            
            if ~exist('StopOnError','var')
                StopOnError = 0;
            end
            if strcmp(obj.cType, 'Usb')
                
                TxData  =   0;
                if obj.hCon > -1
                    TxData      =   1;
                else
                    disp(['REC: USB Connection closed previously'])
                end
                if TxData > 0
                    if strcmp(obj.cDevType, 'RadarLog')
                        RLen        =   USBnAny('recv32', int32(128), 'uart');
                        Header      =   double(RLen(1));
                        Len         =   mod(floor(Header/2^16),256);
                        if Len < 32
                            Ret         =   double(RLen(2:Len));
                        else
                            Ret         =   1;
                        end
                    else
                        obj.cTinyCmdSend = 2;
                        Ret         =   USBnAny('recv32', int32(2048), 'uart');
                        obj.cTinyCmdSend = 0;
                        Header      =   double(Ret(1));
                        Len         =   mod(floor(Header/2^16), 256);
                        if Len < 32
                            Ret     =   double(Ret(2:end));
                        else
                            Ret     =   1;
                        end
                    end
                end
                
                if obj.ConNew > 0
                    obj.UsbClose();
                end
            elseif strcmp(obj.cType, 'PNet')
                TxData  =   0;
                if obj.hCon > -1
                    TxData      =   1;
                else
                    disp(['REC: TCPIP Connection closed previously'])
                end
                
                if TxData > 0
                    %----------------------------------------------------------
                    % Read response
                    %----------------------------------------------------------
                    if strcmp(obj.cType,'PNet')
                        Len         =   pnet(obj.hCon, 'read', 1, 'uint32');
                    else
                        Len         =   fread(obj.hTcpCon, 1, 'uint32');
                    end
                    Len         =   double(swapbytes(uint32(Len)));
                    Len         =   floor(Len/2^16);
                    
                    if Len > 1
                        if strcmp(obj.cType,'PNet')
                            Ret         =   pnet(obj.hCon,'read', Len-1, 'uint32');
                        else
                            Ret         =   fread(obj.hTcpCon,Len-1,'uint32');        
                        end
                        Ret             =   double(swapbytes(uint32(Ret)));
                    else
                        Ret  =   Len;
                    end
                    
                end
                
                if obj.ConNew > 0
                    obj.CloseTcpipCom();
                end
            elseif strcmp(obj.cType, 'RadServe')
                if obj.hCon > -1
                    Len         =   pnet(obj.hCon, 'read', 1, 'uint32');
                    %disp(['Header: ', num2str(Len)])
                    Len         =   swapbytes(uint32(Len));
                    Type        =   mod(Len, 2^16);
                    Len         =   floor(double(Len)/2^16);
                    
                    err = 0;
                    if (Len > 1024)
                        err = 1;
                        Len = Len - 1024;
                    end
                    Len = Len - 1;
                    
                    if ~(numel(Len) > 0 || numel(Type) > 0)
                        if StopOnError > 0
                            error('Receive error');
                        else
                            disp('Receive error');
                        end
                        Ret = 0;
                    else
                        
                        if (err > 0) && (Len > 0) 
                            Ret = pnet(obj.hCon, 'read', Len*4, 'uint8');
                            if StopOnError > 0
                                error(char(Ret));
                            else
                                warning(char(Ret));
                            end
                            Ret = -1;
                        elseif ( ( ((obj.cArmCmdBegin <= Type) && (Type <= obj.cArmCmdEnd)) || ((obj.cFpgaCmdBegin <= Type) && (Type <= obj.cFpgaCmdEnd)) ) && (Len > 0))
                            Ret = pnet(obj.hCon, 'read', Len, 'uint32');
                            Ret = double(swapbytes(uint32(Ret)));
                        elseif (err == 0) && (Type == obj.cResponseMsg) && (Len > 0)
                            % handle non error case - TODO !
                            Ret = pnet(obj.hCon, 'read', Len*4, 'uint8');
                            % AnHa Return string to calling function
                            Ret = char(Ret);
                        elseif (err == 0) && (Type == obj.cResponseOk)
                            Ret = 0;
                        elseif (err == 0) && (Type == obj.cResponseDouble)
                            Ret = pnet(obj.hCon, 'read', Len*4, 'uint8');
                            Ret = typecast(Ret, 'double');
                        elseif (err == 0) && (Type == obj.cResponseInt)
                            Ret = pnet(obj.hCon, 'read', Len, 'uint32');
                            Ret             =   double(swapbytes(uint32(Ret)));
                        elseif (err == 0) && (Type == obj.cResponseData)
                            if (Len > 0)
                                Ret = pnet(obj.hCon, 'read', Len, 'uint32');
                                %Ret =   double(swapbytes(uint32(Ret))); %% TODO: check if this is ok
                            else
                                Ret = [];
                            end
                        else
                            Ret = 0;
                        end 
                    end
                end
            end
        end
        
        %   @function       ToUint8                                                               
        %   @author         Haderer Andreas (HaAn)                                                  
        %   @date           2013-12-01          
        %   @brief          Convert Command to Uint8 Values (UInt32 to 4 UInt8)
        %   @param[in]      Cmd: Array containing command (Uint8 values)
        %   @return         Array containing uint8 values 
        function    [CmdBytes]  =   ToUint8(obj, Cmd)
            CmdBytes    =   [];
            for Idx = 1:numel(Cmd)
                Val     =   double(Cmd(Idx));
                B0      =   mod(Val,256);
                Val     =   floor(Val/256);
                B1      =   mod(Val,256);
                Val     =   floor(Val/256);
                B2      =   mod(Val,256);
                Val     =   floor(Val/256);
                B3      =   mod(Val,256);
                CmdBytes    =   [CmdBytes; B0; B1; B2; B3];
            end
        end
    end % of cmd functions
    
    %% Open/Close functions
    methods (Access = protected)
        function ConOpen (obj)
            if strcmp(obj.cType,'Usb')
                if obj.hCon > -1
                    obj.UsbClose();
                    obj.UsbOpen();
                else
                    obj.UsbOpen();
                end
            elseif strcmp(obj.cType, 'PNet')
                if obj.hCon > -1
                    obj.CloseTcpipCom();
                    obj.hCon    =   obj.OpenTcpipCom(obj.cIpAddr, obj.cCfgPort);
                else
                    obj.hCon    =   obj.OpenTcpipCom(obj.cIpAddr, obj.cCfgPort);
                end
            elseif strcmp(obj.cType, 'RadServe')
                if obj.hCon == -1
                    obj.hCon = obj.OpenTcpipCom(obj, obj.cIpAddr, obj.cCfgPort);
                end
            end
        end
        
        function ConClose (obj)      
            if strcmp(obj.cType,'Usb')
                obj.UsbClose();
            elseif strcmp(obj.cType, 'PNet')
                if obj.hCon > -1
                    disp(['Close connection to ',obj.Name])
                    obj.CloseTcpipCom();
                    obj.hCon        =   -1;
                end     
            elseif strcmp(obj.cType, 'RadServe')
                if obj.hCon > -1
                    obj.CloseTcpipCom();
                    obj.hCon = -1;
                end               
            end
        end
        
        function ConCloseData (obj)       
            if strcmp(obj.cType,'Usb')
                obj.UsbClose();
            else
                if obj.hConDat > -1
                    disp(['Close Data connection to ',obj.Name])
                    obj.CloseTcpipDataCom();
                    obj.hConDat     =   -1;
                end     
            end
        end
        
        %   @function       UsbOpen.m                                                                
        %   @author         Haderer Andreas (HaAn)                                                  
        %   @date           2013-12-01          
        %   @brief          Open USB connection if connection is closed
        function Dev    =   UsbOpen(obj)
            if obj.hCon > -1 
                obj.UsbClose();
            end                
            obj.hCon    =   1;
            obj.hConDat =   1;
            Dev         =   USBnAny('open');
            if obj.cDebugInf > 10
                disp(['USB device pointer: ', num2str(Dev)]);
            end
        end

        %   @function       UsbClose.m                                                                
        %   @author         Haderer Andreas (HaAn)                                                  
        %   @date           2013-12-01          
        %   @brief          Close USB connection if connection is open               
        function UsbClose(obj)
            if obj.hCon > -1
                USBnAny('close');
                obj.hConDat         =   -1;
                obj.hCon            =   -1;
                obj.ConNew          =   0;
            end
        end
        
        %   @function       OpenTcpipCom.m                                                                
        %   @author         Haderer Andreas (HaAn)                                                  
        %   @date           2013-12-01          
        %   @brief          Open TCPIP connection at given address and port number
        %   @param[in]      IpAdr:  String containing valid IP address; string is not checked
        %   @param[in]      Port:   Port number of connection
        %   @return         tcpCon: Handle to TCP connection            
        function        tcpCon  =   OpenTcpipCom(obj, IpAdr, Port) 
            if strcmp(obj.cType,'PNet')||strcmp(obj.cType,'RadServe')
                % Use Pnet functions
                %disp('TCP/IP with PNet functions');
                %disp(['Con:', num2str(Port)]);
                tcpCon      = pnet('tcpconnect',IpAdr, Port);
                pnet(tcpCon,'setreadtimeout',2);
                pnet(tcpCon,'setwritetimeout',2);
            else
                % Use TcpIp functions
                %disp('TCP/IP with Matlab functions');
                tcpCon = tcpip(IpAdr, Port,'NetworkRole','Client','InputBufferSize',100000);           % tcp connection settings
                fopen(tcpCon);  
            end
        end
        
        %   @function       CloseTcpipCom.m                                                                
        %   @author         Haderer Andreas (HaAn)                                                  
        %   @date           2013-12-01          
        %   @brief          Close TCPIP cfg connection if open
        %                   Set hCon to -1 indicates that the connection is closed               
        function CloseTcpipCom(obj)
            if strcmp(obj.cType,'PNet') || strcmp(obj.cType, 'RadServe')
                % Use Pnet functions
                if obj.hCon > -1
                    pnet(obj.hCon,'close');
                    obj.hCon    =   -1;
                end
            else
                if obj.hCon > 0
                    % Use TcpIp functions
                    fclose(obj.hTcpCon);
                end
                obj.hCon    =   -1;
            end            
        end 
        
        function OpenTcpipDataCom(obj, port)
            if obj.hConDat == -1
                % Use Pnet functions
                %disp('TCP/IP with PNet functions');
                %disp(['Con:', num2str(Port)]);
                obj.hConDat  = pnet('tcpconnect',obj.cIpAddr, port);
                pnet(obj.hConDat,'setreadtimeout',4);
                pnet(obj.hConDat,'setwritetimeout',2);
                if (obj.hConDat == -1)
                    disp('Couldn''t connect to data port.');
                end
            end
        end
        
        %   @function       CloseTcpipDataCom.m                                                                
        %   @author         Haderer Andreas (HaAn)                                                  
        %   @date           2013-12-01          
        %   @brief          Close TCPIP data connection if connection is open
        %                   Set hConDat to -1 -> connection is closed           
        function CloseTcpipDataCom(obj)
            if strcmp(obj.cType,'PNet') || strcmp(obj.cType, 'RadServe')
                % Use Pnet functions
                if obj.hConDat > 0
                    pnet(obj.hConDat,'close');
                    obj.hConDat     =   -1;
                end
            else
                % Use TcpIp functions
                fclose(obj.hTcpConDat);
                obj.hConDat     =   -1;
            end
        end 
        
        function OpenTcpipVideoCom(obj, Idx)
            if obj.hConVideo(Idx) == -1
                % Use Pnet functions
                %disp('TCP/IP with PNet functions');
                %disp(['Con:', num2str(Port)]);
                obj.hConVideo(Idx)  = pnet('tcpconnect',obj.cIpAddr, obj.cVideoPort(Idx));
                pnet(obj.hConVideo(Idx),'setreadtimeout',2);
                pnet(obj.hConVideo(Idx),'setwritetimeout',2);
                if (obj.hConVideo(Idx) == -1)
                    disp(['Couldn''t connect to video port ' num2str(obj.cVideoPort(Idx)) '.']);
                end
            end
        end
        
        function CloseTcpipVideoCom(obj, Idx)
            if obj.hConVideo(Idx) > -1
                pnet(obj.hConVideo(Idx),'close');
                obj.hConVideo(Idx)   =   -1;
            end
        end
    end % of open/close functions
    
    %% file functions
    methods (Access = public)
        % DOXYGEN ------------------------------------------------------
        %> @brief Create File 
        %>     
        %>      
        %>
        %>  @param[in]  stName: file name
        %>              Max number of packets: (Mult*N*NrChn)
        %>
        %>  @return             
        function Ret = CreateFile(obj, stName, Max, Extension)
            Len     = mod(length(stName),4);
            for Idx     = 1:(4-Len)
                stName  = [stName ' '];
            end
            
            if ~exist('Max','var')
                Max = obj.cNumPackets;
            end
            
            if ~exist('Extension', 'var')
                Extension = 0;
            end
                
            % create file cmd
            data = [uint32(Extension) uint32(length(stName)) typecast(uint8(stName), 'uint32') uint32(Max)];
            [Ret] = obj.CmdSend(0, hex2dec('6145'), data);
            [Ret] = obj.CmdRecv();
            
            % write file cmd - only necessary for RadServe < v3.0.0
            %Data    = [uint32(Max)];
            %[Ret]   = obj.CmdSend(0, hex2dec('6146'), Data);
            %[Ret]   = obj.CmdRecv();
        end
        
        function Ret    =   StopFile(obj)
            disp('StopFile() is obsolete');
        end
        
        function CloseFile(obj)              
            Ret     = obj.CmdSend(0, hex2dec('6147'), []);
            Ret     = obj.CmdRecv();
            
            obj.PollFileClosed();
        end
        
        function PollFileClosed(obj)
            Ret = 1;
            if (obj.hCon > -1)
                while (Ret == 1)
                    Ret = obj.CmdSend(0, hex2dec('6148'), [], 0);
                    Ret = obj.CmdRecv();
                end
            end
        end
        
        function ReplayFileAs(obj, stTarget, stName, varargin)            
            if strcmp(stTarget, 'Raw')
                obj.ReplayFileN(stName, 'TargetLvl', 1, varargin{:});
            elseif strcmp(stTarget, 'RangeProfile')
                obj.ReplayFileN(stName, 'TargetLvl', 2, varargin{:});
            elseif strcmp(stTarget, 'RangeDoppler')
                obj.ReplayFileN(stName, 'TargetLvl', 3, varargin{:});
            elseif strcmp(stTarget, 'DetectionList')
                obj.ReplayFileN(stName, 'TargetLvl', 4, varargin{:});
            elseif strcmp(stTarget, 'TargetTracker')
                obj.ReplayFileN(stName, 'TargetLvl', 5, varargin{:});
            else
                obj.ReplayFileN(stName, 'TargetLvl', 1, varargin{:});
            end
        end
        
        function ReplayFile(obj, stName, FrameIdx, Video, Extension)
            Idx = 1;
            if exist('FrameIdx','var')
                Idx = FrameIdx;
            end
        
            WithVideo = 'no';
            if exist('Video','var')
                if Video > 0
                    WithVideo = 'yes';
                end
            end
            
            if ~exist('Extension', 'var')
                Extension = 'no';
            else
                if Extension > 0
                    Extension = 'yes';
                else
                    Extension = 'no';
                end
            end
        
            obj.ReplayFileN(stName, 'FrameIdx', Idx, 'WithVideo', WithVideo, 'Extension', Extension)
        end
        
        function ReplayFileN(obj, stName, stDataType, varargin)
            wasSupported = obj.Computation.isSupported;
            
            if wasSupported == 0
                obj.Computation.Enable();
            end
            
            compData = -1;
            if exist('stDataType', 'var')
                if ~(strcmp(stDataType, 'RangeProfile') || strcmp(stDataType, 'RangeDoppler') || strcmp(stDataType, 'DetectionList') || strcmp(stDataType, 'TargetTracker'))
                    varargin = [stDataType varargin];
                else
                    compData = 1;
                end
            else
                stDataType = '';
            end
            
            inParser = inputParser;
            addRequired(inParser,'stName',@ischar);
            addParameter(inParser,'FrameIdx', 1, @(x) isnumeric(x) && isscalar(x) && (x > 0));
            addParameter(inParser,'WithVideo', 'no', @(x) any(validatestring(x,{'yes','no'})));
            addParameter(inParser,'Extension', 'no', @(x) any(validatestring(x,{'yes','no'})));
            addParameter(inParser,'TargetLvl', -1, @(x) isnumeric(x) && isscalar(x) && (x >= -1));
            parse(inParser, stName, varargin{:});
            
            Len     = mod(length(stName),4);
            for Idx     = 1:(4-Len)
                stName  = [stName ' '];
            end
            
            if strcmp(inParser.Results.Extension, 'yes') || compData > -1
                intExt = 1;
                targetLvl = inParser.Results.TargetLvl;
            else
                intExt = 0;
                targetLvl = inParser.Results.TargetLvl;
            end
            
            % replay file cmd ... frameIdx -1 to start with 0 on server side
            Data = [uint32(intExt) uint32(inParser.Results.FrameIdx - 1) uint32(length(stName)) typecast(uint8(stName), 'uint32') uint32(targetLvl)];
            [Ret] = obj.CmdSend(0,hex2dec('6149'), Data, 0);
            [Ret] = obj.CmdRecv();
            
            if (numel(Ret) == 1 && Ret ~= -1)
                % RadServe < 3.0.0 in use
                PortNum = Ret;
                NumVideo = 1; % try receiving video info
            elseif (numel(Ret) > 1)
                Ret = swapbytes(Ret);
                PortNum       = Ret(1);
                obj.cExtSize  = Ret(2);
                obj.cExtMult  = Ret(3);
                
                DataType = Ret(4);
                
                if intExt ~= 0 && targetLvl ~= 0
                    obj.cReplayExt = 1;
                end
                NumVideo      = Ret(5);
                
                if (numel(Ret) > 5)
                    Remainder = Ret(6:end);
                end
                
                if (DataType ~= 0 && numel(Remainder) > 0)
                    obj.Computation.SetDataType(DataType, typecast(Remainder, 'single'));
                end
            end
                        
            if (PortNum > 0)
                obj.cPortOpen = 1;
                obj.cPortNum = PortNum;
            end
            
            % video info must be called before connecting -> if called after, no video will be provided
            if NumVideo > 0 && strcmp(inParser.Results.WithVideo,'yes')
                obj.cVideoPort     = [];
                obj.cVideoCols     = [];
                obj.cVideoRows     = [];
                obj.cVideoChn      = [];
                obj.cVideoRate     = [];
                obj.cVideoSize     = [];
                obj.cVideoFrames   = [];
                obj.cVideoFrmsColl = [];
                obj.cVideoPort     = [];
                obj.cVideoPortOpen = [];
                obj.cVideoName     = {};
                obj.hConVideo      = [];
                            
                for VidIdx=1:NumVideo
                    [Ret] = obj.CmdSend(0,hex2dec('614B'), uint32(VidIdx-1), 0);
                    [Ret] = obj.CmdRecv();

                    if (numel(Ret) >= 7)
                        Ret = swapbytes(Ret);
                        %VideoInfo = typecast(Ret, 'uint32');
                        if (Ret(1) > 0)
                            obj.cVideoPort     = [obj.cVideoPort     Ret(1)];
                            obj.cVideoCols     = [obj.cVideoCols     Ret(2)];
                            obj.cVideoRows     = [obj.cVideoRows     Ret(3)];
                            obj.cVideoChn      = [obj.cVideoChn      Ret(4)];
                            obj.cVideoRate     = [obj.cVideoRate     Ret(6)];
                            obj.cVideoSize     = [obj.cVideoSize     Ret(2) * Ret(3)*Ret(4)];
                            obj.cVideoFrames   = [obj.cVideoFrames   Ret(7)];
                            obj.cVideoPortOpen = [obj.cVideoPortOpen 1];
                            obj.hConVideo      = [obj.hConVideo -1];
                            obj.cVideoFrmsColl = [obj.cVideoFrmsColl 0];
                            
                            if (numel(Ret) >= 8)
                                obj.cVideoName = {obj.cVideoName, char(typecast(Ret(8:end),'uint8'))};
                            end
                        end
                    end
                end
            end
            
            obj.OpenTcpipDataCom(obj.cPortNum);

            if strcmp(inParser.Results.WithVideo,'yes') && (sum(obj.cVideoPortOpen) >= 1)
                for VidIdx = 1:numel(obj.cVideoPort)
                    obj.OpenTcpipVideoCom(VidIdx);
                end
                %obj.OpenTcpipVideoCom(obj.cVideoPort);
            end
            
            obj.cReplay = 1;
            
            if wasSupported == 0
                obj.Computation.Disable();
            end
        end
        
        function StopReplayFile(obj)
            if obj.cReplay > -1
                data    = [];
                Ret     = obj.CmdSend(0,hex2dec('614C'), data, 0);
                Ret     = obj.CmdRecv();
                
                obj.PollReplayClosed();
                obj.cReplay = -1;
            end
            
            for Idx = 1:numel(obj.hConVideo)
                obj.CloseTcpipVideoCom(Idx);
            end
            obj.CloseTcpipDataCom();
        end
        
        function PollReplayClosed(obj)
            Ret = 1;
            if (obj.hCon > -1)
                % poll replay closed
                while (Ret == 1)
                    Ret = obj.CmdSend(0, hex2dec('614D'), [], 0);
                    Ret = obj.CmdRecv();
                end                       
            end
        end        
    end % of file functions
    
    % data port functions
    methods (Access = public)
        function GetDataPort(obj, varargin)
            inParser = inputParser;
            addParameter(inParser, 'Extension', 0, @(x) isnumeric(x) && isscalar(x) && (x >= -1));
            parse(inParser, varargin{:});
            
            if inParser.Results.Extension > 0
                intExt = inParser.Results.Extension;
            else
                intExt = 0;
            end
            
            compExt = 0;
            DataType = obj.Computation.GetDataType();
            if DataType > 0
                compExt = intExt;
                intExt = DataType;
            end
            
            if obj.cPortOpen == -1
                data    = [uint32(intExt) uint32(obj.cNumPackets)];
                if (compExt > 0)
                    data = [data uint32(compExt)];
                end 
                [Ret]   = obj.CmdSend(0, hex2dec('6140'), data);
                [Ret]   = obj.CmdRecv();
                
                NumVideo = 0;
                if (numel(Ret) == 1 && Ret ~= -1)
                    obj.cPortOpen = 1;
                    obj.cPortNum = Ret;
                    NumVideo = 0;
                elseif numel(Ret) > 1
                    Ret = swapbytes(Ret);
                    obj.cPortOpen = 1;
                    obj.cPortNum = Ret(1);
                    % Ret(2) = datsize
                    % Ret(3) = mult
                    
                    if intExt >= 1
                        obj.cExtSize = Ret(2);
                        if numel(Ret) > 3
                            obj.cExtMult = Ret(3);
                            NumVideo = Ret(4);
                        else
                            obj.cExtMult = obj.cMult;
                            NumVideo = 0;
                        end
                    else
                        NumVideo = Ret(4);
                    end
                end
                
                if (NumVideo > 0 && obj.cDPVideo > 0)
                    obj.cVideoPort     = [];
                    obj.cVideoCols     = [];
                    obj.cVideoRows     = [];
                    obj.cVideoChn      = [];
                    obj.cVideoRate     = [];
                    obj.cVideoSize     = [];
                    obj.cVideoFrames   = [];
                    obj.cVideoFrmsColl = [];
                    obj.cVideoPort     = [];
                    obj.cVideoPortOpen = [];
                    obj.cVideoName     = {};
                    obj.hConVideo      = [];
                                
                    for VidIdx=1:NumVideo
                        [Ret] = obj.CmdSend(0, hex2dec('6142'), uint32(VidIdx-1), 0);
                        [Ret] = obj.CmdRecv();
    
                        if (numel(Ret) >= 6)
                            Ret = swapbytes(Ret);
                            %VideoInfo = typecast(Ret, 'uint32');
                            if (Ret(1) > 0)
                                obj.cVideoPort     = [obj.cVideoPort     Ret(1)];
                                obj.cVideoCols     = [obj.cVideoCols     Ret(2)];
                                obj.cVideoRows     = [obj.cVideoRows     Ret(3)];
                                obj.cVideoChn      = [obj.cVideoChn      Ret(4)];
                                obj.cVideoRate     = [obj.cVideoRate     Ret(6) * obj.cMult];
                                obj.cVideoSize     = [obj.cVideoSize     Ret(2)*Ret(3)*Ret(4)];
                                obj.cVideoPortOpen = [obj.cVideoPortOpen 1];
                                obj.hConVideo      = [obj.hConVideo -1];
                                obj.cVideoFrmsColl = [obj.cVideoFrmsColl 0];
                                if (numel(Ret) >= 7)
                                    obj.cVideoName = {obj.cVideoName, char(typecast(Ret(7:end),'uint8'))};
                                end
                            end
                        end
                    end
                end
                    
                obj.OpenTcpipDataCom(obj.cPortNum);

                if (obj.cDPVideo && sum(obj.cVideoPortOpen) >= 1)
                    for VidIdx = 1:NumVideo
                        obj.OpenTcpipVideoCom(VidIdx);
                    end
                end

                obj.cDataOpened = 1;
            end
        end
        
        function CloseDataPort(obj)
            if (strcmp(obj.cType, 'RadServe'))
                if (obj.cDataOpened > -1) && (obj.cPortOpen == 1)
                    data    = [];
                    [Ret]   = obj.CmdSend(0, hex2dec('6143'), data);
                    [Ret]   = obj.CmdRecv();
                    if Ret == 0
                        obj.cPortOpen = -1;
                        obj.cDataOpened = -1;
                        obj.cExtSize = 0;
                    end
                end

                obj.PollDataPortClosed();

                obj.CloseTcpipDataCom();
            end
        end
        
        function PollDataPortClosed(obj)
            Ret = 1;
            if (obj.hCon > -1)
                % poll dataport closed?
                while (Ret == 1)
                    Ret = obj.CmdSend(0, hex2dec('6144'), [], 0);
                    Ret = obj.CmdRecv();
                end
            end
        end
        
        function RestartDataPort(obj, varargin)
            inParser = inputParser;
            addParameter(inParser,'NumPackets', 0, @(x) isnumeric(x) && isscalar(x) && (x > 0));
            parse(inParser, varargin{:});
            
            if (inParser.Results.NumPackets == 0)
                NumPackets = obj.cNumPackets;
            else
                NumPackets = inParser.Results.NumPackets;
            end
            
            if obj.cPortOpen == -1
                data    = [uint32(NumPackets)];
                
                [Ret]   = obj.CmdSend(0, hex2dec('6142'), data);
                [Ret]   = obj.CmdRecv();
            end
        end
        
        function GetExtensionPort(obj, Extension)
            obj.GetDataPort('Extension', Extension);
        end
    end % of data port functions
    
    % stream functions
    %methods (Access = public)
    %    function Ret    =   CreateStream (obj)                
    %        % create stream cmd
    %        data = [uint32(0) uint32(obj.cMult)];
    %        [Ret] = obj.CmdSend(0, hex2dec('6160'), data);
    %        [Ret] = obj.CmdRecv();
    %        
    %        % start stream cmd
    %        Data    = [uint32(0) uint32(Num)];
    %        [Ret]   = obj.CmdSend(0, hex2dec('6161'), Data);
    %        [Ret]   = obj.CmdRecv();
    %    end
    %    
    %    function Ret    =   StopStream(obj)
    %        data = [uint32(0)];
    %        [Ret] = obj.CmdSend(0,hex2dec('6162'), data);
    %        [Ret] = obj.CmdRecv();
    %    end
    %    
    %    function CloseStream(obj)
    %        data    = [uint32(0)];
    %        [Ret]   = obj.CmdSend(0,hex2dec('6163'), data);
    %        [Ret]   = obj.CmdRecv();
    %        
    %        % poll stream closed?
    %    end
    %end % of stream functions
    
    methods (Access = public)
        function SetIndex(obj, Index)
            obj.cDevIdx = Index;
        end
                             
        function Ret    =   ConAppendTimestamp(obj, Val)
            Data        =   [uint32(Val)];
            Ret         =   obj.CmdSend(0, hex2dec('610C'), Data, 0);
            Ret         =   obj.CmdRecv();
        end
        
        function ConSetFileParam(obj, stName, Val, DataType)            
            if strcmp(obj.cType, 'RadServe') && obj.cReplay < 0 && obj.cReplayExt < 0
                if ~exist('DataType','var')
                    DataType = 'STRING';
                end
                
                %% set config
                if strcmp(DataType, 'INT')
                    Type    =   uint32(1);
                    Data    =   uint32(Val);
                elseif strcmp(DataType, 'DOUBLE')
                    Type    =   uint32(2);
                    Data    =   typecast(Val, 'uint32');
                elseif strcmp(DataType, 'ARRAY32')
                    Type    =   uint32(3);
                    Data    =   [uint32(numel(Val)) uint32(Val)];
                elseif strcmp(DataType, 'ARRAY64')
                    Type    =   uint32(4);
                    Data    =   [uint32(numel(Val)) typecast(Val, 'uint32')];
                else
                    Type    =   uint32(0);
                    TmpVal    =   Val;
                    
                    Tmp     =   mod(length(TmpVal),4);
                    if (Tmp ~= 0)
                        for Idx = 1:(4-Tmp)
                            TmpVal = [TmpVal ' '];
                        end
                    end
                    Data = typecast(uint8(TmpVal), 'uint32');
                end
                
                Len         =   mod(length(stName),4);
                if (Len ~= 0)
                    for Idx = 1:(4-Len)
                        stName  = [stName, ' '];
                    end
                end
                
                if obj.cDebugInf > 0
                    disp(['ConSetFileParam: ', num2str(numel(stName)), ': ', stName])
                end
                dat         =   [Type uint32(length(stName)) typecast(uint8(stName),'uint32') Data];
                Ret         =   obj.CmdSend(0,hex2dec('6105'),dat, 0);
                Ret         =   obj.CmdRecv();
            end
        end
        
        function Ret = ConGetFileParam(obj, stName, DataType)
            if strcmp(obj.cType, 'RadServe')
                if ~exist('DataType','var')
                    DataType = 'UNKNOWN';
                end
                
                if strcmp(stName, 'RangeProfile')
                    stName = 'CfgRP';
                    DataType = 'ARRAY64';
                elseif strcmp(stName, 'RangeDoppler')
                    stName = 'CfgRD';
                    DataType = 'ARRAY64';
                elseif strcmp(stName, 'TargetList')
                    stName = 'CfgTL';
                    DataType = 'ARRAY64';
                end
               
                len = mod(length(stName),4);
                if (len ~= 0)
                    for n = 1:(4-len)
                        stName = [stName ' '];
                    end
                end
                
                if strcmp(DataType, 'INT') || strcmp(DataType, 'Int')
                    Type = uint32(1);
                elseif strcmp(DataType, 'DOUBLE') || strcmp(DataType, 'Double')
                    Type = uint32(2);
                elseif strcmp(DataType, 'ARRAY32') || strcmp(DataType, 'Array32')
                    Type = uint32(3);
                elseif strcmp(DataType, 'ARRAY64') || strcmp(DataType, 'Array64')
                    Type = uint32(4);
                elseif strcmp(DataType, 'STRING') || strcmp(DataType, 'String')
                    Type = uint32(0);
                else
                    Type = uint32(5); % UNKNOWN
                end
        
                data = [Type typecast(uint8(stName),'uint32')];
                [Ret]       =   obj.CmdSend(0,hex2dec('6156'),data,0);
                [Ret]       =   obj.CmdRecv();
                
                if strcmp(DataType, 'ARRAY64')
                    Ret = typecast(swapbytes(Ret), 'double');
                elseif strcmp(DataType, 'ARRAY32')
                    Ret = swapbytes(Ret);
                end
            end
        end 
    end
    
    methods (Access = protected)
        function Ret    =   ConClrFifo(obj)
            Data        =   [];
            Ret         =   obj.CmdSend(0, hex2dec('612B'), Data);
            Ret         =   obj.CmdRecv();
            disp('Clear Fifo')
        end
        
        function ConSetTimeout(obj, value)
            if (value ~= obj.cTimeout) && (value > 0)
                if strcmp(obj.cType,'Usb')
                    if obj.hCon < 0
                        Dev             =   obj.UsbOpen();
                    	USBnAny('timeout', int32(obj.Usb_Timeout));
                        obj.UsbClose();
					else
                    	USBnAny('timeout', int32(obj.Usb_Timeout));
                    end
                elseif strcmp(obj.cType, 'RadServe')
                    if (value ~= obj.cTimeout)
                        Data = [uint32(value)];
                        obj.CmdSend(0, hex2dec('6107'), Data);
                        obj.CmdRecv();
                        obj.cTimeout = value;
                    end
                end 
            end
        end
        
        function ConSetCfgTimeout(obj, value)
            if (value ~= obj.cCfgTimeout) && (value > 0)
                if strcmp(obj.cType, 'RadServe')
                    if (value ~= obj.cCfgTimeout)
                        Data = [uint32(value)];
                        obj.CmdSend(0, hex2dec('6106'), Data);
                        obj.CmdRecv();
                        obj.cCfgTimeout = value;
                    end
                end 
            end
        end
    end
        
    methods (Access = {?Connection,?Computation})
        function Ret = ConGetData(obj, Len)
            if obj.hConDat > -1
                Ret = zeros(1,Len,'uint8');
                tmp = pnet(obj.hConDat, 'read', Len, 'uint8');
                tmpIdx = numel(tmp);
                
%                 if (tmpIdx == 0) % stop if no data is received on first try
%                     Ret = [];
%                 end
                
                Ret(1:tmpIdx) = tmp;
                Len = Len - tmpIdx;
                %% attempt reading until all required data is received
                while (Len > 0)
                    tmp = pnet(obj.hConDat, 'read', Len, 'uint8');
                    tmpSize = numel(tmp);
                    if (tmpSize == 0) % no data received = stop
                        Len = -1;
                    else
                        Ret(tmpIdx+1:tmpIdx+tmpSize) = tmp;
                        tmpIdx = tmpIdx + tmpSize;
                        Len = Len - tmpSize;
                    end
                end
            else
                Ret = 0;
            end
        end
    end
    
    methods (Access = public)
        % DOXYGEN ------------------------------------------------------
        %> @brief Display version information of USB mex driver
        %>
        %> Display version information in the Matlab command window
        %>  
        function DispSrvVers(obj)
            if strcmp(obj.cType,'Usb')
                USBnAny('version');
            elseif strcmp(obj.cType, 'RadServe')
                [Ret]       =   obj.CmdSend(0,hex2dec('6100'),[]);
                [Ret]       =   obj.CmdRecv();
            end
        end

        function ListDev(obj)
            if strcmp(obj.cType, 'RadServe')
                data = [];
                [Ret] = obj.CmdSend(0,hex2dec('6110'), data, 0);
                [Ret] = obj.CmdRecv();
                disp(Ret);
            end
        end

        % DOXYGEN ------------------------------------------------------
        %> @brief Set attribute of class object
        %>
        %> Sets different attributes of the class object
        %>
        %> @param[in]     stSel: String to select attribute
        %> 
        %> @param[in]     Val: value of the attribute (optional); can be a string or a number  
        %>  
        %> Supported parameters  
        %>      -   <span style="color: #ff9900;"> 'BufSiz': </span> Set buffer size in RadServe <br>
        %>      -   <span style="color: #ff9900;"> 'Mult': </span> Set Packetsize for file streaming  <br>                    
        %>        
        %> e.g. Set BufSiz to 1024
        %>   @code
        %>      Brd =   Radarlog( )
        %>         
        %>      Brd.ConSet('BufSiz',1024)
        %>   @endcode           
        function ConSet(obj,varargin)
            if strcmp(obj.cType, 'RadServe')
                if nargin > 1
                    stVal       = varargin{1};
                    switch stVal
                        case 'BufSiz'
                            if nargin > 2
                                obj.cBufSiz     =   varargin{2};
                                [Ret] = obj.CmdSend(0,hex2dec('6108'), [uint32(obj.cBufSiz)], 0);
                                [Ret] = obj.CmdRecv();
                            end
                        case 'Mult'
                            if nargin > 2
                                obj.cMult       =   varargin{2};
                                [Ret] = obj.CmdSend(0,hex2dec('6109'), [uint32(obj.cMult)], 0);
                                [Ret] = obj.CmdRecv();
                            end
                        case 'KeepAlive'
                            if nargin > 2
                                obj.cDataPortKeepAlive = varargin{2};
                                [Ret] = obj.CmdSend(0,hex2dec('610B'), [uint32(obj.cDataPortKeepAlive)], 0);
                                [Ret] = obj.CmdRecv();
                            end
                        case 'NumPackets'
                            if nargin > 2
                                obj.cNumPackets = varargin{2};
                            end
                        case 'UsbNrTx'
                            if nargin > 2
                                obj.cUsbNrTx = varargin{2};
                                [Ret] = obj.CmdSend(0,hex2dec('610A'), [uint32(obj.cUsbNrTx)], 0);
                                [Ret] = obj.CmdRecv();
                            end
                    end
                end
            end
        end
        
        function ConForceSet(obj,varargin)
            if strcmp(obj.cType, 'RadServe')
                if nargin > 1
                    stVal       = varargin{1};
                    switch stVal
                        case 'Mult'
                            if nargin > 2
                                obj.cMult       =   varargin{2};
                                [Ret] = obj.CmdSend(0,hex2dec('6109'), [uint32(obj.cMult) 1], 0);
                                [Ret] = obj.CmdRecv();
                            end
                    end
                end
            end
        end
                       
        function RadServe_PrintParameterList(obj, stDataType)
            dataType = 0;
            if strcmp(stDataType, 'RangeProfile')
                dataType = 2;
            elseif strcmp(stDataType, 'RangeDoppler')
                dataType = 3;
            elseif strcmp(stDataType, 'TargetList')
                dataType = 4;
            else
                disp('Invalid DataType given.');
                return;
            end
            Data        =   [uint32(dataType)];
            Ret         =   obj.CmdSend(0, hex2dec('6162'), Data, 0);
            Ret         =   obj.CmdRecv();
            disp(Ret);
        end
        
        function CfgRadServe(obj, varargin)
            if strcmp(obj.cType, 'RadServe') && nargin > 2
                stVal       = varargin{1};
                switch stVal
                    case 'CreateCmdLogFile'
                        stName = varargin{2};
                        len = mod(length(stName),4);
                        if (len ~= 0)
                            for n = 1:(4-len)
                                stName = [stName ' '];
                            end
                        end
                        if (nargin > 3)
                            if strcmp(varargin{3}, 'FPGA')
                                type = 0;
                            elseif strcmp(varargin{3}, 'RadServe')
                                type = 1;
                            else
                                type = 2;
                            end
                        else
                            type = 2;
                        end
                        
                        Data = [uint32(type) uint32(length(stName))  typecast(uint8(stName),'uint32')];
                        [Ret] = obj.CmdSend(0,hex2dec('6102'), Data, 0);
                        [Ret] = obj.CmdRecv();                        
                    case 'AddVideoToFile'
                        Data = [uint32(varargin{2})];
                        [Ret] = obj.CmdSend(0,hex2dec('6118'), Data, 0);
                        [Ret] = obj.CmdRecv();
                    case 'AddVideoToDataPort'
                        obj.cDPVideo = varargin{2};
                        Data = [uint32(obj.cDPVideo)];
                        [Ret] = obj.CmdSend(0,hex2dec('6119'), Data, 0);
                        [Ret] = obj.CmdRecv();
                    case 'AddTimStmpToFilename'
                        Data = [uint32(varargin{2})];
                        [Ret] = obj.CmdSend(0,hex2dec('610E'), Data, 0);
                        [Ret] = obj.CmdRecv();
                    case 'LogDataPortToFile'
                        stName = varargin{2};
                        if (nargin > 3)
                            if strcmp(varargin{3}, 'RangeProfile')
                                level = 2;
                            elseif strcmp(varargin{3}, 'RangeDoppler')
                                level = 3;
                            elseif strcmp(varargin{3}, 'DetectionList')
                                level = 4;
                            elseif strcmp(varargin{3}, 'TargetTracker')
                                level = 5;
                            elseif strcmp(varargin{3}, 'Extension')
                                level = 6;
                            else
                                level = 0;
                            end
                        else
                            level = 0;
                        end
                            
                        if strcmp(stName, '')
                            Data = [uint32(0) uint32(0) uint32(level)];
                        else
                            len = mod(length(stName),4);
                            if (len ~= 0)
                                for n = 1:(4-len)
                                    stName = [stName ' '];
                                end
                            end
                            Data = [uint32(1) uint32(length(stName)) typecast(uint8(stName),'uint32') uint32(level)];
                        end
                        
                        [Ret] = obj.CmdSend(0,hex2dec('610F'), Data, 0);
                        [Ret] = obj.CmdRecv();
                    case 'HdfPath'
                        stName = varargin{2};
                        len = mod(length(stName),4);
                        if (len ~= 0)
                            for n = 1:(4-len)
                                stName = [stName ' '];
                            end
                        end
                        Data = [typecast(uint8(stName),'uint32')];
                        
                        [Ret] = obj.CmdSend(0,hex2dec('610D'), Data, 0);
                        [Ret] = obj.CmdRecv();
                end
            end                        
        end
        
        function CfgRadServe_Extension(obj, stVal, varargin)
            if strcmp(obj.cType, 'RadServe')
                switch (stVal)
                    case 'General'
                        inParser = inputParser;
                        addParameter(inParser,'Path', '', @(x) ischar(x));
                        addParameter(inParser,'Selection', 0, @(x) isnumeric(x) && isscalar(x) && (x >= 0));
                        addParameter(inParser,'Parameters', [], @(x) isvector(x));
                        parse(inParser, varargin{:});

                        stPath = inParser.Results.Path;
                        Len     = mod(length(stPath),4);
                        for Idx     = 1:(4-Len)
                            stPath  = [stPath ' '];
                        end

                        Data = [uint32(0) uint32(length(stPath)) typecast(uint8(stPath), 'uint32') uint32(inParser.Results.Selection) uint32(numel(inParser.Results.Parameters))];
                        if (numel(inParser.Results.Parameters) > 0)
                            Data = [Data typecast(inParser.Results.Parameters, 'uint32')];
                        end

                        [Ret] = obj.CmdSend(0,hex2dec('6160'), Data, 0);
                        [Ret] = obj.CmdRecv();
                    case 'File'
                        inParser = inputParser;
                        addParameter(inParser, 'AddRaw', 'no', @(x) any(validatestring(x,{'yes','no'})));
                        addParameter(inParser, 'SplitChn', 'no', @(x) any(validatestring(x,{'yes','no'})));
                        parse(inParser, varargin{:});

                        if strcmp(inParser.Results.AddRaw, 'yes')
                            intAddRaw = 1;
                        else
                            intAddRaw = 0;
                        end

                        if strcmp(inParser.Results.SplitChn, 'yes')
                            intSplitChn = 1;
                        else
                            intSplitChn = 0;
                        end

                        Data = [uint32(intAddRaw) uint32(intSplitChn)];

                        [Ret] = obj.CmdSend(0,hex2dec('6161'), Data, 0);
                        [Ret] = obj.CmdRecv();
                end
            end
        end
        
        function CfgRadServe_Camera(obj, stVal, varargin)
            if strcmp(obj.cType, 'RadServe')
                switch(stVal)
                    case 'List'
                        [Ret] = obj.CmdSend(0,hex2dec('6114'), [], 0);
                        [Ret] = obj.CmdRecv()
                    case 'DeselectAll'
                        [Ret] = obj.CmdSend(0,hex2dec('6115'), [], 0);
                        [Ret] = obj.CmdRecv();
                    case 'Deselect'
                        inParser = inputParser;
                        addParameter(inParser,'Id', 0, @(x) isnumeric(x) && isscalar(x) && (x >= 0));
                        parse(inParser, varargin{:});
                        
                        Data = [uint32(inParser.Results.Id)];
                        [Ret] = obj.CmdSend(0,hex2dec('6117'), Data, 0);
                        [Ret] = obj.CmdRecv();
                    case 'Select'
                        inParser = inputParser;
                        addParameter(inParser,'HdfName', '', @(x) ischar(x));
                        addParameter(inParser,'Id', 0, @(x) isnumeric(x) && isscalar(x) && (x >= 0));
                        addParameter(inParser,'Rate', 0, @(x) isnumeric(x) && isscalar(x) && (x > 0));
                        addParameter(inParser,'Width', 1920, @(x) isnumeric(x) && isscalar(x) && (x > 0));
                        addParameter(inParser,'Height', 1080, @(x) isnumeric(x) && isscalar(x) && (x > 0));
                        parse(inParser, varargin{:});

                        stPath = inParser.Results.HdfName;
                        Len     = mod(length(stPath),4);
                        for Idx     = 1:(4-Len)
                            stPath  = [stPath ' '];
                        end

                        Data = [uint32(inParser.Results.Id) uint32(inParser.Results.Rate) uint32(length(stPath)) typecast(uint8(stPath), 'uint32') uint32(inParser.Results.Width) uint32(inParser.Results.Height)];
                        [Ret] = obj.CmdSend(0,hex2dec('6116'), Data, 0);
                        [Ret] = obj.CmdRecv();
                    case 'AddOptris'
                        inParser = inputParser;
                        addParameter(inParser,'Serial', 0, @(x) isnumeric(x) && isscalar(x) && (x > 0));
                        addParameter(inParser,'ConfigFile', '', @(x) ischar(x));
                        addParameter(inParser,'Emissivity', 1, @(x) isnumeric(x) && isscalar(x) && (x > 0));
                        addParameter(inParser,'Transmissivity', 1, @(x) isnumeric(x) && isscalar(x) && (x > 0));
                        addParameter(inParser,'ColoringPalette', 'Iron', @(x) ischar(x));
                        addParameter(inParser,'ScalingMethod', 'MinMax', @(x) ischar(x));
                        addParameter(inParser,'RawData', 1, @(x) isnumeric(x) && isscalar(x));
                        parse(inParser, varargin{:});

                        stPath = inParser.Results.ConfigFile;
                        Len     = mod(length(stPath),4);
                        for Idx     = 1:(4-Len)
                            stPath  = [stPath ' '];
                        end
                        
                        stPalette = inParser.Results.ColoringPalette;
                        Len     = mod(length(stPalette),4);
                        for Idx     = 1:(4-Len)
                            stPalette  = [stPalette ' '];
                        end
                        Len     = length(stPalette) / 4;
                        for Idx     = 1:(3-Len)
                            stPalette  = [stPalette '    '];
                        end
                        
                        stScaling = inParser.Results.ScalingMethod;
                        Len     = mod(length(stScaling),4);
                        for Idx     = 1:(4-Len)
                            stScaling  = [stScaling ' '];
                        end
                        Len     = length(stScaling) / 4;
                        for Idx     = 1:(2-Len)
                            stScaling  = [stScaling '    '];
                        end

                        Data = [uint32(inParser.Results.Serial) uint32(single(inParser.Results.Emissivity)) uint32(single(inParser.Results.Transmissivity)) typecast(uint8(stPalette), 'uint32') typecast(uint8(stScaling), 'uint32') typecast(uint8(stPath), 'uint32') uint32(inParser.Results.RawData)];
                        [Ret] = obj.CmdSend(0,hex2dec('611A'), Data, 0);
                        [Ret] = obj.CmdRecv();
                    case 'UpdateOptris'
                        inParser = inputParser;
                        addParameter(inParser,'Serial', 0, @(x) isnumeric(x) && isscalar(x) && (x > 0));
                        addParameter(inParser,'Emissivity', 1, @(x) isnumeric(x) && isscalar(x) && (x > 0));
                        addParameter(inParser,'Transmissivity', 1, @(x) isnumeric(x) && isscalar(x) && (x > 0));
                        addParameter(inParser,'ColoringPalette', 'Iron', @(x) ischar(x));
                        addParameter(inParser,'ScalingMethod', 'MinMax', @(x) ischar(x));
                        addParameter(inParser,'RawData', 1, @(x) isnumeric(x) && isscalar(x));
                        parse(inParser, varargin{:});
                        
                        stPalette = inParser.Results.ColoringPalette;
                        Len     = mod(length(stPalette),4);
                        for Idx     = 1:(4-Len)
                            stPalette  = [stPalette ' '];
                        end
                        Len     = length(stPalette) / 4;
                        for Idx     = 1:(3-Len)
                            stPalette  = [stPalette '    '];
                        end
                        
                        stScaling = inParser.Results.ScalingMethod;
                        Len     = mod(length(stScaling),4);
                        for Idx     = 1:(4-Len)
                            stScaling  = [stScaling ' '];
                        end
                        Len     = length(stScaling) / 4;
                        for Idx     = 1:(2-Len)
                            stScaling  = [stScaling '    '];
                        end

                        Data = [uint32(inParser.Results.Serial) uint32(single(inParser.Results.Emissivity)) uint32(single(inParser.Results.Transmissivity)) typecast(uint8(stPalette), 'uint32') typecast(uint8(stScaling), 'uint32') uint32(inParser.Results.RawData)];
                        [Ret] = obj.CmdSend(0,hex2dec('611B'), Data, 0);
                        [Ret] = obj.CmdRecv();                        
                    case 'RemoveOptris'
                        inParser = inputParser;
                        addParameter(inParser,'Serial', 0, @(x) isnumeric(x) && isscalar(x) && (x > 0));
                        parse(inParser, varargin{:});
                        
                        Data = [uint32(inParser.Results.Serial)];
                        [Ret] = obj.CmdSend(0,hex2dec('611C'), Data, 0);
                        [Ret] = obj.CmdRecv();  
                end
            end    
        end
        
        function AddVideo(obj, Add)        
            disp('AddVideo is obsolete, please use CfgRadServe_Camera(''List'') to receive camera list and CfgRadServe_Camera(''Select'', ''Id'', <id>, ''Rate'', <rate>, ''HdfName'', <name>, ''Width'', <width>, ''Height'', <height>) to select a camera');
        end
        
        function DispVideo(obj, fig, VidIdx)
            if ~exist('VidIdx','var')
                VidIdx = 1;
            end
                            
            if ~exist('fig','var')
                fig = 1;
            end
            
            if (1 <= VidIdx && VidIdx <= numel(obj.hConVideo))
                if (obj.hConVideo(VidIdx) > 0)
                    while (uint32(obj.cDataIdx / obj.cVideoRate(VidIdx)) > obj.cVideoFrmsColl(VidIdx))

                        Len = obj.cVideoSize(VidIdx);
                        Vid = zeros(Len,1);
                        Idx = 1;

                        while (Len > 0)
                            tmp = pnet(obj.hConVideo(VidIdx), 'read', Len, 'uint8');
                            tmpSiz = numel(tmp);
                            if (tmpSiz == 0)
                                Len = -1;
                            else
                                Vid(Idx:Idx+tmpSiz-1, 1) = tmp;
                                Idx = Idx + tmpSiz;
                                Len = Len - tmpSiz;
                            end
                        end

                        if (Len ~= -1)
                            inp = Vid;
                            if (numel(inp) > 0)
                                mat = reshape(inp, obj.cVideoChn(VidIdx), obj.cVideoCols(VidIdx), obj.cVideoRows(VidIdx));
                                tmp = zeros(obj.cVideoCols(VidIdx), obj.cVideoRows(VidIdx), obj.cVideoChn(VidIdx), 'uint8');

                                for idx=1:obj.cVideoChn(VidIdx)
                                    tmp(:,:,idx) = mat(idx,:,:);
                                end

                                img = zeros(obj.cVideoRows(VidIdx), obj.cVideoCols(VidIdx), obj.cVideoChn(VidIdx), 'uint8');

                                for idx=1:obj.cVideoChn(VidIdx)
                                    img(:,:,obj.cVideoChn(VidIdx)-idx+1) = tmp(:,:,idx)';
                                end
                                obj.cVideoFrmsColl(VidIdx) = obj.cVideoFrmsColl(VidIdx) + 1;
                                figure(fig), imshow(img);
                            end
                        end
                    end
                end
            end
        end 
        
        function DispAllVideos(obj, fig)
            if ~exist('fig','var')
                fig = 1;
            end
            
            if (numel(fig) ~= numel(obj.hConVideo))
                tmp = 0:(numel(obj.hConVideo)-1);
                fig = tmp + fig(1);
            end                
            
            for VidIdx = 1:numel(obj.hConVideo)
                hasVid = 1;
                if (obj.hConVideo(VidIdx) > 0)
                    while (uint32(obj.cDataIdx / obj.cVideoRate(VidIdx)) > obj.cVideoFrmsColl(VidIdx) && hasVid == 1)
                        Len = obj.cVideoSize(VidIdx);
                        Vid = zeros(Len,1);
                        Idx = 1;

                        while (Len > 0)
                            tmp = pnet(obj.hConVideo(VidIdx), 'read', Len, 'uint8');
                            tmpSiz = numel(tmp);
                            if (tmpSiz == 0)
                                hasVid = 0;
                                Len = -1;
                            else
                                Vid(Idx:Idx+tmpSiz-1, 1) = tmp;
                                Idx = Idx + tmpSiz;
                                Len = Len - tmpSiz;
                            end
                        end

                        if (Len ~= -1)
                            inp = Vid;
                            if (numel(inp) > 0)
                                mat = reshape(inp, obj.cVideoChn(VidIdx), obj.cVideoCols(VidIdx), obj.cVideoRows(VidIdx));
                                tmp = zeros(obj.cVideoCols(VidIdx), obj.cVideoRows(VidIdx), obj.cVideoChn(VidIdx), 'uint8');

                                for idx=1:obj.cVideoChn(VidIdx)
                                    tmp(:,:,idx) = mat(idx,:,:);
                                end

                                img = zeros(obj.cVideoRows(VidIdx), obj.cVideoCols(VidIdx), obj.cVideoChn(VidIdx), 'uint8');

                                for idx=1:obj.cVideoChn(VidIdx)
                                    img(:,:,obj.cVideoChn(VidIdx)-idx+1) = tmp(:,:,idx)';
                                end
                                obj.cVideoFrmsColl(VidIdx) = obj.cVideoFrmsColl(VidIdx) + 1;
                                figure(fig(VidIdx)), imshow(img);
                            end
                        end
                    end
                end
            end
        end
        
        % DOXYGEN ------------------------------------------------------
        %> @brief Get properties of video in HDF5 file
        %>
        %> Sets different attributes of the class object
        %>
        %> @param[out]      Vid: structure with video properties
        %>          
        function Vid    =   GetVideoProperties(obj, VidIdx)
            if ~exist('VidIdx','var')
                VidIdx = 1;
            end
            
            if (1 <= VidIdx && VidIdx <= numel(obj.hConVideo))
                Vid.Rate    =   obj.cVideoRate(VidIdx);
                Vid.Cols    =   obj.cVideoCols(VidIdx);
                Vid.Rows    =   obj.cVideoRows(VidIdx);
                Vid.Chns    =   obj.cVideoChn(VidIdx);
                Vid.Name    =   ''; %obj.cVideoName(VidIdx);
            else
                Vid.Rate = 0;
                Vid.Cols = 0;
                Vid.Rows = 0;
                Vid.Chns = 0;
                Vid.Name = '';
            end
        end
        
        % DOXYGEN ------------------------------------------------------
        %> @brief Get properties of video in HDF5 file
        %>
        %> Sets different attributes of the class object
        %>
        %> @param[out]      Vid: structure with video properties
        %>          
        function [Num Vid]    =   GetAllVideoProperties(obj)
            Num = numel(obj.hConVideo);
            Vid = struct([]);
            
            for VidIdx = 1:Num
                Vid(VidIdx).Rate    =   obj.cVideoRate(VidIdx);
                Vid(VidIdx).Cols    =   obj.cVideoCols(VidIdx);
                Vid(VidIdx).Rows    =   obj.cVideoRows(VidIdx);
                Vid(VidIdx).Chns    =   obj.cVideoChn(VidIdx);
                Vid(VidIdx).Name    =   ''; %obj.cVideoName(VidIdx);
            end
        end        
        
        function Img = GetVideo(obj, VidIdx)
            Img = [];
            
            if ~exist('VidIdx','var')
                VidIdx = 1;
            end
            
            if (1 <= VidIdx && VidIdx <= numel(obj.hConVideo))
                if (numel(obj.hConVideo) > 0 && obj.hConVideo(VidIdx) > 0)
                    while (uint32(obj.cDataIdx / obj.cVideoRate(VidIdx)) > obj.cVideoFrmsColl(VidIdx))

                        Len = obj.cVideoSize(VidIdx);
                        Vid = zeros(Len,1);
                        Idx = 1;

                        while (Len > 0)
                            tmp = pnet(obj.hConVideo(VidIdx), 'read', Len, 'uint8');
                            tmpSiz = numel(tmp);
                            if (tmpSiz == 0)
                                disp('no vid');
                                Len = -1;
                            else
                                Vid(Idx:Idx+tmpSiz-1, 1) = tmp;
                                Idx = Idx + tmpSiz;
                                Len = Len - tmpSiz;
                            end
                        end

                        if (Len ~= -1)
                            inp = Vid;
                            if (numel(inp) > 0)
                                mat = reshape(inp, obj.cVideoChn(VidIdx), obj.cVideoCols(VidIdx), obj.cVideoRows(VidIdx));
                                tmp = zeros(obj.cVideoCols(VidIdx), obj.cVideoRows(VidIdx), obj.cVideoChn(VidIdx), 'uint8');

                                for idx=1:obj.cVideoChn(VidIdx)
                                    tmp(:,:,idx) = mat(idx,:,:);
                                end

                                Img = zeros(obj.cVideoRows(VidIdx), obj.cVideoCols(VidIdx), obj.cVideoChn(VidIdx), 'uint8');

                                for idx=1:obj.cVideoChn(VidIdx)
                                    Img(:,:,obj.cVideoChn(VidIdx)-idx+1) = tmp(:,:,idx)';
                                end
                                obj.cVideoFrmsColl(VidIdx) = obj.cVideoFrmsColl(VidIdx) + 1;
                            end
                        end
                    end
                end
            end
        end          
        
        function Img = GetAllVideos(obj, VidIdx)
            Img = [];
            if (1 <= VidIdx && VidIdx <= numel(obj.hConVideo))
                if (obj.hConVideo(VidIdx) > 0)
                    while (uint32(obj.cDataIdx / obj.cVideoRate(VidIdx)) > obj.cVideoFrmsColl(VidIdx))

                        Len = obj.cVideoSize(VidIdx);
                        Vid = zeros(Len,1);
                        Idx = 1;

                        while (Len > 0)
                            tmp = pnet(obj.hConVideo(VidIdx), 'read', Len, 'uint8');
                            tmpSiz = numel(tmp);
                            if (tmpSiz == 0)
                                disp('no vid');
                                Len = -1;
                            else
                                Vid(Idx:Idx+tmpSiz-1, 1) = tmp;
                                Idx = Idx + tmpSiz;
                                Len = Len - tmpSiz;
                            end
                        end

                        if (Len ~= -1)
                            inp = Vid;
                            if (numel(inp) > 0)
                                mat = reshape(inp, obj.cVideoChn(VidIdx), obj.cVideoCols(VidIdx), obj.cVideoRows(VidIdx));
                                tmp = zeros(obj.cVideoCols(VidIdx), obj.cVideoRows(VidIdx), obj.cVideoChn(VidIdx), 'uint8');

                                for idx=1:obj.cVideoChn(VidIdx)
                                    tmp(:,:,idx) = mat(idx,:,:);
                                end

                                Img = zeros(obj.cVideoRows(VidIdx), obj.cVideoCols(VidIdx), obj.cVideoChn(VidIdx), 'uint8');

                                for idx=1:obj.cVideoChn(VidIdx)
                                    Img(:,:,obj.cVideoChn(VidIdx)-idx+1) = tmp(:,:,idx)';
                                end
                                obj.cVideoFrmsColl(VidIdx) = obj.cVideoFrmsColl(VidIdx) + 1;
                            end
                        end
                    end
                end
            end
        end
    end    
end