%< @file        UsbAdi.m                                                                                                                 
%< @date        2017-07-18          
%< @brief       Matlab class for interface to DemoRadUsb Mex file
%< @version     1.1.0

%< Version 2.0.0
%< RadServe support, with USBnAny instead of UsbDemoRad

%< Version 2.1.0
%< BrdDispInf with temperature output

classdef UsbAdi<Connection

    properties (Access = public)
        
        UsbDrvVers  	=   [];
		stUsbAdiVers 	= 	'1.1.0';
		        
        Rad_NrChn       =   4;        
        
        % ------------------------------------------------------------------
        % Configure Sampling
        % ------------------------------------------------------------------
        Rad_N           =   256;
        
        % Gain of 21 dB is configured
        FuSca           =   0.498 / 65536;
		
		stDemoRadVers 	= 	'2.2.0';
		
    end

    methods (Access = public)

        function obj  =   UsbAdi(varargin)
            obj = obj@Connection('TinyRad', varargin{:});
            
            obj.ConSetFileParam('N', obj.Rad_N, 'INT');
            
            obj.Computation.SetNrChn(4);
            obj.ConSetFileParam('NrChn', 4, 'INT');
        end

        function    delete(obj)
        end

        function    Ret     =   Dsp_SendSpiData(obj, SpiCfg, Regs)
            % Sends Data to device (selected by mask) using spi
            Regs    =   Regs(:);
            if (numel(Regs) > 256)
                Regs    =   Regs(1:256);
            end
            DspCmd          =   zeros(3 + numel(Regs), 1);
            Cod             =   hex2dec('9017');
            DspCmd(1)       =   SpiCfg.Mask;
            DspCmd(2)       =   1;
            DspCmd(3)       =   SpiCfg.Chn;
            DspCmd(4:end)   =   Regs;
            
            Ret             =   obj.CmdExec(0, Cod, DspCmd);
        end

        function    Ret     =   Dsp_GetSwVers(obj)
            % Reads the Software Version from the DSP and disps it
            DspCmd      =   zeros(1,1);
            Cod         =   hex2dec('900E');
            DspCmd(1)   =   0;
            
            Ret         =   obj.CmdExec(0, Cod, DspCmd);
        end

        function    Ret     =   BrdGetSwVers(obj)
            Ret     =   obj.Dsp_GetSwVers();
        end
        
        function BrdDispInf(obj)
            
            DspCmd    = zeros(1,1);
            Cod       = hex2dec('9013');
            DspCmd(1) = 0;
            
            Ret       = obj.CmdExec(0, Cod, DspCmd);
            
			% AD7414
            Temp = Ret(2);
            if (Temp >= 512)
                Temp = Temp - 1024;
            end
            Temp = Temp / 4;
            
            disp(' ');
            disp('-------------------------------------------------------------------');
            disp('Board Information');
            disp([' Sw-UID: ' num2str(Ret(1))]);
            disp([' Temp:   ' num2str(Temp) ' deg']);
            disp('-------------------------------------------------------------------');
            
        end

        function    BrdDispSwVers(obj)
            disp(' ');
            disp('-------------------------------------------------------------------');
            disp('FPGA Software UID');
            Vers    =   obj.Dsp_GetSwVers();
            if numel(Vers) > 2
                Tmp         =   Vers(1);
                SwPatch     =   floor(mod(Tmp, 2.^8));
                Tmp         =   floor(Tmp/2.^8);
                SwMin       =   floor(mod(Tmp, 2.^8));
                SwMaj       =   floor(Tmp/2.^8);
                disp([' Sw-Rev: ', num2str(SwMaj),'-',num2str(SwMin),'-',num2str(SwPatch)])    
                disp([' Sw-UID: ', num2str(Vers(2))])
                disp([' Hw-UID: ', num2str(Vers(3))])
            else
                disp('No version information available')
            end
            disp('-------------------------------------------------------------------');        
        end
        
        function    Ret     = BrdGetUID(obj)
            % Returns the UID of the Device"""
            Cmd     =   ones(3,1);
            Cod     =   hex2dec('9030');
            Cmd(2)  =   0;
            Cmd(3)  =   0;
            Ret     =   obj.CmdExec(0, Cod, Cmd);
        end

        function    Ret     =   BrdRdEEPROM(obj, Addr)
            % Reads a 32bit value, starting at given address"""
            Cmd     =   ones(3, 1);
            Cod     =   hex2dec('9030');
            Cmd(2)  =   2;
            Cmd(3)  =   Addr;
            Ret     =   obj.CmdExec(0, Cod, Cmd);
        end
        
        function    Ret     =   BrdWrEEPROM(obj, Addr, Data)
            Cmd     =   ones(4, 1);
            Cod     =   hex2dec('9030');
            Cmd(2)  =   1;
            Cmd(3)  =   Addr;
            Cmd(4)  =   Data;
            Ret     =   obj.CmdExec(0, Cod, Cmd);
        end
        
        function    Ret     =   BrdGetCalInf(obj)
            % Returns Cal Data from EEPROM
            disp('Get Cal Data');
            CalDat                  =   zeros(16,1);
            for Idx = 0:16-1
                CalDat(Idx + 1)     =   obj.BrdRdEEPROM(64 + Idx*4);
            end
            Idcs            =   find(CalDat > 2.^31);
            CalDat(Idcs)    =   CalDat(Idcs) - 2.^32;
            
            Ret.Type        =   CalDat(1);
            Ret.Date        =   CalDat(2);
            Ret.R           =   CalDat(3)./2^16;
            Ret.RCS         =   CalDat(4)./2^16;
            Ret.TxGain      =   CalDat(5)./2^16;
            Ret.IfGain      =   CalDat(6)./2^16;
            
        end
        
        function    Ret     =   BrdGetCalDat(obj)
            % Returns Cal Data from EEPROM
            disp('Get Cal Info');
            CalDat                  =   zeros(16,1);
            for Idx = 0:16-1
                CalDat(Idx + 1)     =   obj.BrdRdEEPROM(Idx*4);
            end
            Idcs            =   find(CalDat > 2.^31);
            CalDat(Idcs)    =   CalDat(Idcs) - 2.^32;
            
            CalDat          =   CalDat./2.^24;
            Ret             =   CalDat(1:2:end) + i.*CalDat(2:2:end); 
            
            obj.Computation.SetParam('CalRe', real(Ret(1:obj.Rad_NrChn))');
            obj.Computation.SetParam('CalIm', imag(Ret(1:obj.Rad_NrChn))');
        end        

        function    Ret     =   BrdSetCalDat(obj, Cal)
            
            Ret             =   [];
            disp('Set Cal Data');
            CalReal         =   real(Cal.Dat)*2.^24;
            CalImag         =   imag(Cal.Dat)*2.^24;

            CalData         =   zeros(22,1);  
            CalData(1:2:16) =   CalReal;
            CalData(2:2:16) =   CalImag;
            CalData(17)     =   Cal.Type
            CalData(18)     =   Cal.Date
            CalData(19)     =   Cal.R*2.^16
            CalData(20)     =   Cal.RCS*2.^16
            CalData(21)     =   Cal.TxGain*2.^16
            CalData(22)     =   Cal.IfGain*2.^16

            if numel(CalData) < 32
                WrDat       =   zeros(numel(CalData)*4,1);
                SendCnt     =   1;
                for Idx = 1:numel(CalData)
                    Dat                 =   CalData(Idx);
                    WrDat(SendCnt)      =   floor(mod(Dat,256));
                    Dat                 =   floor(Dat/256);
                    WrDat(SendCnt+1)    =   floor(mod(Dat,256));
                    Dat                 =   floor(Dat/256);
                    WrDat(SendCnt+2)    =   floor(mod(Dat,256));
                    Dat                 =   floor(Dat/256);
                    WrDat(SendCnt+3)    =   floor(mod(Dat,256));
                    SendCnt             =   SendCnt + 4;
                end
                for Idx = 1:numel(WrDat)
                    obj.BrdWrEEPROM(Idx - 1, WrDat(Idx));
                end
            else
                disp('CalData array to long to fit in EEPROM')
            end   
        end        
        
        function    Set(obj, stVal, varargin)
            
            switch stVal
                case 'cDebugInf'
                    if nargin > 2
                        obj.cDebugInf    =   varargin{1};
                    end 
                case 'Name'
                    if nargin > 2
                        if isstr(varargin{1})
                            obj.Name    =   varargin{1};
                        end 
                    end
                case 'Timeout'
                    if nargin > 2
                        if isstr(varargin{1})
                            obj.ConSetTimeout(varargin{1});
                        end 
                    end
                case 'CfgTimeout'
                    if nargin > 2
                        if isstr(varargin{1})
                            obj.ConSetCfgTimeout(varargin{1});
                        end 
                    end
                    
                otherwise
            end
        end

        % DOXYGEN ------------------------------------------------------
        %> @brief <span style="color: #ff0000;"> LowLevel: </span> Generate boxcar window
        %>
        %> This function returns a boxcar window.
        %>
        %>  @param[in]   M: window size
        %>
        %>  @param[In]   N (optional): Number of copies in second dimension
        function Win    =   boxcar(obj, M, varargin)
            Win             =   ones(M,1);
            if nargin > 2
                M       =   varargin{1};
                M       =   M(1);
                Win     =   repmat(Win, 1, M);
            end
        end
        
        function    Ret     =   Get(obj, stVal)
            % TODO: decide what to do here.
            Ret     = [];
            switch stVal
                case 'cDebugInf'
                    Ret     =   obj.cDebugInf;
                case 'Name'
                    Ret     =   obj.Name;
                case 'N'
                    if strcmp(obj.cType, 'RadServe') && (obj.cReplay > -1)
                        Ret = obj.ConGet(stVal, 'INT');
                    else
                        Ret     =   obj.Rad_N;
                    end
                case 'Samples'
                    if strcmp(obj.cType, 'RadServe') && (obj.cReplay > -1)
                        Ret = obj.ConGet(stVal, 'INT');
                    else
                        Ret     =   obj.Rad_N;
                    end
                case 'NrChn'
                    if strcmp(obj.cType, 'RadServe') && (obj.cReplay > -1)
                        Ret = obj.ConGet(stVal, 'INT');
                        obj.Computation.SetNrChn(Ret);
                        obj.Rad_NrChn =   Ret;
                    else
                        Ret     =   obj.Rad_NrChn;
                    end
                case 'FuSca'
                    obj.FuSca   = 0.498 / 65536;
                    Ret         = obj.FuSca;
                case 'fs'
                    if strcmp(obj.cType, 'RadServe') && (obj.cReplay > -1)
                        Ret = obj.ConGet(stVal,'DOUBLE');
                    else
                        Ret     =   1e6;
                    end
                case 'FileSize'
                    if strcmp(obj.cType, 'RadServe') && (obj.cReplay > -1)
                        Ret = obj.ConGet(stVal, 'DOUBLE');
                    else
                        Ret = 0;
                    end
                case 'MeasStart'
                    if strcmp(obj.cType, 'RadServe') && (obj.cReplay > -1)
                        Ret = obj.ConGet(stVal, 'DOUBLE');
                    else
                        Ret = 0;
                    end
                case 'ExtensionSize'
                    if strcmp(obj.cType, 'RadServe') && (obj.cReplay > -1)
                        Ret = obj.ConGet(stVal, 'DOUBLE');
                    else
                        Ret = 0;
                    end
                otherwise
                    Ret     =   []; 
            end
        end	    
         
        function Ret = ConGet (obj, Key, Type)
            Ret = [];
            if strcmp(obj.cType, 'RadServe')
                Ret = obj.ConGetFileParam(Key, Type);
                if strcmp('N', Key)
                    obj.Rad_N       =   Ret;
                elseif strcmp('NrChn', Key)
                    obj.Rad_NrChn   =   Ret;
                end
            end
        end

		function SetFileParam(obj, stKey, Val)
			if isstr(stKey)
				if isstr(Val)
					obj.ConSetFileParam(stKey, Val, 'STRING');
				else
					obj.ConSetFileParam(stKey, Val, 'DOUBLE');
				end
            else
                warning('Key is not of type string')
            end
        end
        
        function Ret    =   GetFileParam(obj, stKey, stType)
            if ~exist('stType', 'var')
                stType = 'UNKNOWN';
            end  
            
            if isstr(stKey)
                Ret     =   obj.ConGetFileParam(stKey, stType);
            else
                Ret     =   [];
                warning('Key is not of type string')
            end
        end    
        
        function    Ret     =   InLim(obj, Val, Low, High)
            Ret     =   Val;
            if Val < Low
                Val     =   Low;
            end
            if Val > High
                Val     =   High;
            end
        end
        
        % DOXYGEN ------------------------------------------------------
        %> @brief <span style="color: #ff0000;"> LowLevel: </span> Generate hanning window
        %>
        %> This function returns a hanning window.
        %>
        %>  @param[in]   M: window size
        %>
        %>  @param[In]   N (optional): Number of copies in second dimension
        function Win    =   hanning(obj, M, varargin)
            m   =   [-(M-1)/2: (M-1)/2].';
            Win =   0.5 + 0.5.*cos(2.*pi.*m/M);
            if nargin > 2
                M       =   varargin{1};
                M       =   M(1);
                Win     =   repmat(Win, 1, M);
            end
        end

        % DOXYGEN ------------------------------------------------------
        %> @brief <span style="color: #ff0000;"> LowLevel: </span> Generate hanning window
        %>
        %> This function returns a hamming window.
        %>
        %>  @param[in]   M: window size
        %>
        %>  @param[In]   N (optional): Number of copies in second dimension
        function Win    =   hamming(obj, M, varargin)
            m   =   [-(M-1)/2: (M-1)/2].';
            Win =   0.54 + 0.46.*cos(2.*pi.*m/M);
            if nargin > 2
                M       =   varargin{1};
                M       =   M(1);
                Win     =   repmat(Win, 1, M);
            end
        end
    end 
end