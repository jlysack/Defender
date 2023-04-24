%< @file        TinyRad.m                                                                                                                 
%< @date        2017-07-18          
%< @brief       Matlab class for initialization of DemoRadPwm board
%< @version     1.0.0


%< @version     1.1.0
%< Increase buffer size constraint requires 2.4.0 DSP firmware

%< @version 	1.2.0
%< Correct Antenna positions

%< @version     2.0.0
%< Support RadServe and Computations

%< @version     2.1.0
%< Reshape Data from RadServe correctly

classdef TinyRad<UsbAdi

    properties (Access = public)

        %>  Object of first receiver (DevAdf5904 class object)
        Adf_Rx1                     =   [];
        %>  Object of transmitter (DevAdf5901 class object)
        Adf_Tx1                     =   [];

        %>  Object of transmitter Pll (DevAdf4159 class object)
        Adf_Pll                     =   [];
    end

    properties (Access = private)
        
        Rf_USpiCfg_Pll_Chn          =   2;
        Rf_USpiCfg_Tx_Chn           =   1;
        Rf_USpiCfg_Rx_Chn           =   0;


        Rf_fStrt                    =   24e9;
        Rf_fStop                    =   24.25e9;
        Rf_TRampUp                  =   256e-6;
        Rf_TRampDo                  =   256e-6;
        
        Rf_VcoDiv                   =   2;

        stRfVers                    =   '2.0.0';
        
        Seq = [];
        FrmMeasSiz = 1;
                
    end

    methods (Access = public)

        function obj    =   TinyRad(varargin)
            obj = obj@UsbAdi(varargin{:});
            
            if obj.cDebugInf > 10
                disp('AnalogBoard Initialize')
            end

            % Initialize Receiver
            USpiCfg.Mask        =   1;
            USpiCfg.Chn         =   obj.Rf_USpiCfg_Rx_Chn; 
            obj.Adf_Rx1         =   DevAdf5904(obj, USpiCfg);
    
            USpiCfg.Mask        =   1;
            USpiCfg.Chn         =   obj.Rf_USpiCfg_Tx_Chn;
            obj.Adf_Tx1         =   DevAdf5901(obj, USpiCfg);
            
            USpiCfg.Mask        =   1;
            USpiCfg.Chn         =   obj.Rf_USpiCfg_Pll_Chn;
            obj.Adf_Pll         =   DevAdf4159(obj, USpiCfg);            
            
            % Set only four channels
            obj.Set('NrChn',4);
            obj.Computation.Enable();
            obj.Computation.SetParam('fStrt', obj.Rf_fStrt);
            obj.Computation.SetParam('fStop', obj.Rf_fStop);
            obj.Computation.SetParam('TRampUp', obj.Rf_TRampUp);
        end

        % DOXYGEN ------------------------------------------------------
        %> @brief Class destructor
        %>
        %> Delete class object  
        function delete(obj)

        end


        % DOXYGEN ------------------------------------------------------
        %> @brief Get Version information of Adf24Tx2Rx8 class
        %>
        %> Get version of class 
        %>      - Version string is returned as string
        %>
        %> @return  Returns the version string of the class (e.g. 0.5.0)           
        function    Ret     =   RfGetVers(obj)            
            Ret     =   obj.stVers;
        end


        % DOXYGEN ------------------------------------------------------
        %> @brief Get attribute of class object
        %>
        %> Reads back different attributs of the object
        %>
        %> @param[in]   stSel: String to select attribute
        %> 
        %> @return      Val: value of the attribute (optional); can be a string or a number  
        %>  
        %>      -   <span style="color: #ff9900;"> 'TxPosn': </span> Array containing positions of Tx antennas 
        %>      -   <span style="color: #ff9900;"> 'RxPosn': </span> Array containing positions of Rx antennas
        %>      -   <span style="color: #ff9900;"> 'ChnDelay': </span> Channel delay of receive channels
        function    Ret     =   RfGet(obj, varargin)
            Ret     =   [];
            if nargin > 1
                stVal       = varargin{1};
                switch stVal
                    case 'TxPosn'
                        Ret     =   zeros(2,1);
                        Ret(1)  =   0;
                        Ret(2)  =   -18.654e-3;
                    case 'RxPosn'
                        Ret     =   -[0:3].';
                        Ret     =   Ret.*6.2170e-3 - 49.136e-3;                    
                    case 'B'
                        Ret     =   (obj.Rf_fStop - obj.Rf_fStrt);  
                    case 'kf'
                        Ret     =   (obj.Rf_fStop - obj.Rf_fStrt)./obj.Rf_TRampUp;
                    case 'fc'
                        Ret     =   (obj.Rf_fStop + obj.Rf_fStrt)/2;
                    otherwise

                end
            end
        end
            
        % DOXYGEN ------------------------------------------------------
        %> @brief Enable all receive channels
        %>
        %> Enables all receive channels of frontend
        %>
        %>  
        %> @note: This command calls the Adf4904 objects Adf_Rx
        %>        In the default configuration all Rx channels are enabled. The configuration of the objects can be changed before 
        %>        calling the RxEna command.
        %>
        %> @code 
        %> CfgRx1.Rx1      =   0;
        %> Brd.Adf_Rx1.SetCfg(CfgRx1); 
        %> @endcode
        %>  In the above example Chn1 of receiver 1 is disabled and all channels of receiver Rx2 are disabled
        function    RfRxEna(obj)
            disp('RfRxEna');
            obj.RfAdf5904Ini(1);
        end

        % DOXYGEN ------------------------------------------------------
        %> @brief Configure receivers 
        %>
        %> Configures selected receivers
        %>
        %> @param[in]   Mask: select receiver: 1 receiver 1; 2 receiver 2
        %>  
        function    RfAdf5904Ini(obj, Mask)
            if Mask == 1
                obj.Adf_Rx1.Ini();
                
                if obj.cDebugInf > 10
                    disp('Rf Initialize Rx1 (ADF5904)')
                end
            end
        end

        % DOXYGEN -------------------------------------------------
        %> @brief Displays status of frontend in Matlab command window  
        %>
        %> Display status of frontend in Matlab command window         
        function    BrdDispSts(obj)
            obj.BrdDispInf();
        end

        % DOXYGEN ------------------------------------------------------
        %> @brief Enable transmitter
        %>
        %> Configures TX device
        %>
        %> @param[in]   TxChn
        %>                  - 0: off
        %>                  - 1: Transmitter 1 on
        %>                  - 2: Transmitter 2 on
        %> @param[in]   TxPwr: Power register setting 0 - 256; only 0 to 100 has effect
        %>
        %>  
        function    RfTxEna(obj, TxChn, TxPwr)
            TxChn           =   floor(mod(TxChn, 3));
            TxPwr           =   floor(mod(TxPwr, 2.^8));

            Cfg.TxChn       =   TxChn;
            Cfg.TxPwr       =   TxPwr;

            obj.Adf_Tx1.SetCfg(Cfg);
            obj.Adf_Tx1.Ini();
            
        end
        
        function    RfMeas(obj, Cfg)  
            
            AdarCfg.X   =   3;
            AdarCfg.R   =   5;
            AdarCfg.N   =   76;
            AdarCfg.M   =   100;
            RetVal  =   obj.Dsp_CfgAdarPll(AdarCfg);
            if RetVal   == 1
                disp('ADAR PLL Locked')
            else
                warning('ADAR PLL not locked')
            end

            % Check configuration
            if Cfg.Perd <= Cfg.N*1e-6 + 22e-6
                error('Period is to short: increase period > TRampUp + 22us')
            end
            
            if Cfg.CycSiz < 2
                error('At least two buffers required')
            end
            
            if (4*Cfg.N*Cfg.FrmMeasSiz*Cfg.CycSiz*numel(Cfg.Seq)) > hex2dec('60000')
                error('Required memory greater than DSP buffer size: decrease CycSiz, N, FrmMeasSiz')
            end
            
            if Cfg.FrmMeasSiz > Cfg.FrmSiz
                error('Number of frames to record > number of frames')
            end
                        
            obj.RfAdf4159Ini(Cfg);
            obj.Dsp_CfgMeas(Cfg);
            obj.Dsp_StrtMeas(Cfg);            
            
            obj.ConSetFileParam('N', uint32(obj.Rad_N), 'INT');
            obj.ConSet('Mult', obj.FrmMeasSiz * numel(obj.Seq));
            
            obj.Computation.SetParam('fs', 1e6);
            obj.Computation.SetParam('FuSca', obj.FuSca);
            
        end
        
        function    Ret     =   BrdRst(obj)
            DspCmd          =   zeros(2, 1);
            Cod             =   hex2dec('9031');
            DspCmd(1)       =   1;
            DspCmd(2)       =   0;
            Ret             =   obj.CmdSend(0, Cod, DspCmd);  
            Ret             =   obj.CmdRecv();
        end
        
        function    Ret     =   Dsp_CfgMeas(obj, Cfg)
            
            obj.Seq         =   Cfg.Seq(:);
            obj.FrmMeasSiz  =   Cfg.FrmMeasSiz;
            obj.Dsp_CfgMeasSiz(Cfg);
            Ret     =   obj.Dsp_CfgMeasSeq(Cfg);
        end
        
        
        function    Ret     =   Dsp_CfgAdarPll(obj, Cfg)
            DspCmd          =   zeros(6, 1);
            Cod             =   hex2dec('9031');
            DspCmd(1)       =   1;
            DspCmd(2)       =   12;
            DspCmd(3)       =   Cfg.X;
            DspCmd(4)       =   Cfg.R;
            DspCmd(5)       =   Cfg.N;
            DspCmd(6)       =   Cfg.M;
            Ret             =   obj.CmdSend(0, Cod, DspCmd);            
            Ret             =   obj.CmdRecv();
        end
            
         function    Ret     =   Dsp_SetAdarReg(obj, Regs)
            DspCmd          =   zeros(2 + numel(Regs), 1);
            Cod             =   hex2dec('9031');
            DspCmd(1)       =   1;
            DspCmd(2)       =   10;
            DspCmd(3:end)   =   Regs(:);
            Ret             =   obj.CmdSend(0, Cod, DspCmd);            
            Ret             =   obj.CmdRecv();
        end       
        
        function    Ret     =   Dsp_CfgMeasSeq(obj, Cfg)

            Seq             =   Cfg.Seq(:);
            % Rotate by one because state refers to next measurement state
            Seq             =   [Seq(2:end); Seq(1)];
            
            DspCmd          =   zeros(2 + numel(Seq), 1);
            Cod             =   hex2dec('9031');
            DspCmd(1)       =   1;
            DspCmd(2)       =   3;
            DspCmd(3:end)   =   Seq;
            
            Ret             =   obj.CmdSend(0, Cod, DspCmd);
            Ret             =   obj.CmdRecv();
        end         
        
        function    Ret     =   Dsp_CfgMeasSiz(obj, Cfg)
            
            
            DspCmd          =   zeros(6, 1);
            Cod             =   hex2dec('9031');
            DspCmd(1)       =   1;
            DspCmd(2)       =   2;
            DspCmd(3)       =   numel(Cfg.Seq);
            DspCmd(4)       =   Cfg.FrmSiz;
            DspCmd(5)       =   Cfg.FrmMeasSiz;
            DspCmd(6)       =   Cfg.CycSiz;
            Ret             =   obj.CmdSend(0, Cod, DspCmd);
            Ret             =   obj.CmdRecv();
        end        
        
        function    Ret     =   Dsp_StrtMeas(obj, Cfg)
            
            obj.Rad_N       =   Cfg.N;
            
            DspCmd          =   zeros(4, 1);
            Cod             =   hex2dec('9031');
            DspCmd(1)       =   1;
            DspCmd(2)       =   1;
            DspCmd(3)       =   round(Cfg.Perd./10e-9);
            DspCmd(4)       =   Cfg.N;
            Ret             =   obj.CmdSend(0, Cod, DspCmd);
            Ret             =   obj.CmdRecv();
        end
        
        function    Ret     =   Dsp_GetDmaErr(obj)

            DspCmd          =   zeros(4, 1);
            Cod             =   hex2dec('9033');
            DspCmd(1)       =   1;
            DspCmd(2)       =   1;
            Ret             =   obj.CmdSend(0, Cod, DspCmd);
            Ret             =   obj.CmdRecv();
        end        
        
        
        function    Ret     =   Dsp_GetDat(obj, Len)
            DspCmd          =   zeros(4, 1);
            Cod             =   hex2dec('9032');
            DspCmd(1)       =   1;
            DspCmd(2)       =   1;
            DspCmd(3)       =   Len;                                        %Cfg.N*4*numel(Cfg.Seq)*Cfg.FrmMeasSiz;
            Ret             =   obj.DataRead(0, Cod, DspCmd);
        end        
        
        function    Dat     =   BrdGetData(obj, NrPack, varargin)
            Len             =   obj.Rad_NrChn * obj.Rad_N * numel(obj.Seq).*obj.FrmMeasSiz;
            
            if strcmp(obj.cType, 'RadServe') 
                if ~exist('NrPack', 'var')
                    NrPack = 1;
                end
                
                inParser = inputParser;
                addRequired(inParser,'NrPack',@(x) isnumeric(x) && isscalar(x) && (x > 0));
                addParameter(inParser,'Extension', -1, @(x) isnumeric(x) && isscalar(x) && (x >= -1));
                parse(inParser, NrPack, varargin{:});
                
                %----------------------------------------------------------
                % Open Data Port
                %----------------------------------------------------------
                if obj.hConDat < 0
                    % GetDataPort(obj, Num, DataType)
                    if (inParser.Results.Extension <= 0)
                        obj.GetDataPort();
                    else
                        obj.GetExtensionPort(inParser.Results.Extension);
                    end
                    obj.cDataIdx = 0;
                end
                
                if (obj.Computation.GetDataType() <= 1 && obj.cReplay == -1 && obj.cReplayExt == -1 && inParser.Results.Extension ~= 1)
                    UsbData = obj.ConGetData(Len * 2 * NrPack);
                    UsbData = int16(typecast(UsbData,'int16'));
                    UsbData = reshape(double(UsbData), obj.Rad_N, obj.Rad_NrChn, numel(UsbData)/(obj.Rad_NrChn * obj.Rad_N));
                    
                    Dat = zeros(numel(UsbData)/(obj.Rad_NrChn), obj.Rad_NrChn);
                    for Idx = 1:numel(UsbData)/(obj.Rad_NrChn * obj.Rad_N)
                        for Chn = 1:obj.Rad_NrChn
                            Dat( (1 + obj.Rad_N * (Idx - 1)) : (obj.Rad_N * Idx), Chn) = UsbData(:, Chn, Idx);
                        end
                    end
                elseif (obj.Computation.GetDataType() <= 1 && obj.cReplay == 1)
                    Len = obj.Rad_N * obj.Rad_NrChn * obj.cExtMult;
                    UsbData = obj.ConGetData(Len * 2);
                    UsbData = int16(typecast(UsbData, 'int16'));
                    
                    Dat     = reshape(double(UsbData), numel(UsbData)/obj.Rad_NrChn, obj.Rad_NrChn);
                elseif (inParser.Results.Extension ~= 1)
                    Dat    = obj.Computation.GetData(NrPack);
                    obj.cDataIdx = obj.cDataIdx + obj.cExtMult * NrPack;
                else
                    Dat    = int16(typecast(obj.ConGetData(NrPack*obj.cExtSize*2),'int16')); % extsize is in int16, read in uint8
                    obj.cDataIdx = obj.cDataIdx + obj.cExtMult * NrPack;
                end
            else
                Dat             =   obj.Dsp_GetDat(Len);
            end
        end
           
       function    RfAdf4159Ini(obj, Cfg)
            obj.Adf_Pll.SetCfg(Cfg);
            obj.Adf_Pll.Ini();
        end
        
        function    Ret     =   Fpga_SetUSpiData(obj, SpiCfg, Regs)
            Ret     =   obj.Dsp_SendSpiData(SpiCfg, Regs);
        end
     
        function    UIfdB   =   RefCornerCube(obj, fc, aCorner, R, Freq,varargin)        
            
            c0          =   3e8;
            %--------------------------------------------------------------------------
            % Transmit Power 
            % Gc 17 dB is for this method of calculation and compared to
            % datasheet RfIn to Ifout pp; Gc for 22 db seems to be
            % differentially
            %--------------------------------------------------------------------------
            PtdBm       =   7;
            GtdB        =   12;
            GrdB        =   12;
            GcdB        =   17;                         
            if nargin > 4
                Cfg     =   varargin
                if isfield(Cfg,'PtdBm')
                    PtdBm   =   Cfg.PtdBm;
                end
            end
            
            
            
            C1 = 10e-9;
            R1 = 2.86e3;
            
            
            
            FreqC = 1/(2.*pi.*C1*R1);    
            
            HHighPass = (i.*Freq./FreqC)./(1 + i.*Freq./FreqC);
            
            %--------------------------------------------------------------------------
            % Calculate Values
            %--------------------------------------------------------------------------
            Pt          =   10.^(PtdBm./10).*1e-3;
            Gt          =   10.^(GtdB./10);
            Gr          =   10.^(GrdB./10);
            Lambdac     =   c0/fc;
            
            RCS         =   4.*pi.*aCorner.^4./(3.*Lambdac.^2)
            
            Pr          =   Pt./(4.*pi.*R.^4).*Gt./(4.*pi).*Gr./(4.*pi).*RCS.*Lambdac.^2;
            PrdBm       =   10.*log10(Pr./1e-3);
            PIfdBm      =   PrdBm + GcdB;
            UIf         =   sqrt(50.*10.^(PIfdBm./10).*1e-3)*sqrt(2);
            UIfdB       =   20.*log10(UIf) + 20.*log10(abs(HHighPass));        
        end            
        
    end 
end