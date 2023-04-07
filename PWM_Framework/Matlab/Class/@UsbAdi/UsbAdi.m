%< @file        UsbAdi.m                                                                                                                 
%< @date        2017-07-18          
%< @brief       Matlab class for interface to DemoRadUsb Mex file
%< @version     1.1.0

classdef UsbAdi<handle

    properties (Access = public)
        
		UsbOpen     	=   0;
        UsbDrvVers  	=   [];
		stUsbAdiVers 	= 	'1.1.0';
		
        DebugInf        =   0;
        
        Rad_NrChn       =   4;        
        
        % ------------------------------------------------------------------
        % Configure Sampling
        % ------------------------------------------------------------------
        Rad_N           =   256;
        
        FuSca           =   0.498 / 65536;
		
		stDemoRadVers 	= 	'2.2.0';
		
    end

    methods (Access = public)

        function obj  =   UsbAdi() 
            obj.UsbOpen         =   0;
        end

        function    delete(obj)
			% TODO: close does not work properly
            disp('Del USB connection')
            if obj.UsbOpen > 0
                obj.UsbOpen     =   0;
                disp('Close usb connection')
                DemoRadUsb('Close');
            end
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

        function    BrdDispSwVers(obj);
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
                case 'DebugInf'
                    if nargin > 2
                        obj.DebugInf    =   varargin{1};
                    end 
                case 'Name'
                    if nargin > 2
                        if isstr(varargin{1})
                            obj.Name    =   varargin{1};
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
                case 'DebugInf'
                    Ret     =   obj.DebugInf;
                case 'Name'
                    Ret     =   obj.Name;
                case 'N'
                    Ret     =   obj.Rad_N;
                case 'Samples'
                    Ret     =   obj.Rad_N;
                case 'NrChn'
                    Ret     =   obj.Rad_NrChn;
                case 'FuSca'
                    obj.FuSca   = 0.498 / 65536;
                    Ret         = obj.FuSca;
                case 'fs'
                    Ret     =   1e6;
                otherwise
                    Ret     =   []; 
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
        
	
		
        function    TxData  =   CmdBuild(obj, Ack, CmdCod, Data)
            LenData         =   numel(Data) + 1;
            TxData          =   zeros(LenData,1);
            TxData(1)       =   (2.^24)*Ack + (2.^16)*LenData + CmdCod;
            TxData(2:end)   =   Data(:);
            TxData          =   uint32(TxData);
        end 

        function    Ret     =   CmdExec(obj, Ack, Cod, Data)
            if obj.UsbOpen == 0
                obj.UsbOpen         =   DemoRadUsb('Open');
                if obj.UsbOpen == 0
                    disp('Usb open failed');
                end
            end
            Cmd             =   obj.CmdBuild(Ack, Cod, Data);
            Ret             =   DemoRadUsb('ExecCmd', Cmd);
        end         
        
  
        function    Ret     =   CmdReadDatLen(obj, Ack, Cod, Data)
            Cmd             =   obj.CmdBuild(Ack, Cod, Data);
            Ret             =   DemoRadUsb('GetDatLen', Cmd);
            Len             =   numel(Ret);
            Ret             =   reshape(Ret,4,Len/4);
            Ret             =   Ret.';            
        end           
        
        
    end 
end