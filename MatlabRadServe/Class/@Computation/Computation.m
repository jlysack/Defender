%< @file        Computation.m                                                                
%< @author      Susanne Rechbauer (SuRe)                                                  
%< @date        2019-05
%< @brief       Computation class for configuring and displaying RadServe computations
%< @version     1.0.0

%< Version 1.1.0
%< Rename parameters

%< Version 1.1.1
%< Add Track_dT

%< Version 1.1.2
%< Add Ang_Flip

classdef Computation<handle

    properties (Access = public) % {?Computation, ?Connection})
        isSupported   = 0;
        nrChn         = 1;
        dataType      = 0;
        dtypeLen      = 4;
        
        rpMult        = 0;
        rpMin         = 0;
        rpMax         = 0;
        rpLen         = 0;
        rpSort        = 0;
        
        rdLen         = 0; 
        rdVelMin      = 0;
        rdVelMax      = 0;
        
        dlLen         = 0;
        
        ttNumTar      = 0;
        ttTarSize     = 0;
        ttNumTracks   = 0;
        ttNumHist     = 0;
        
        Raw           = 'Raw';
        Range         = 'Range';
        RP            = 'RangeProfile';
        Vel           = 'Vel';
        RD            = 'RangeDoppler';
        Ang           = 'Ang';
        Thres         = 'Thres';
        DL            = 'DetectionList';
        Track         = 'Track';
        TT            = 'TargetTracker';
        
        isSet_FuSca   = 0;
        isSet_fStrt   = 0;
        isSet_fStop   = 0;
        isSet_TRampUp = 0;
        isSet_fs      = 0;
        isSet_CalRe   = 0;
        isSet_CalIm   = 0;
        isSet_Tp      = 0;
        isSet_Np      = 0;
        
        viewX         = [];
        viewY         = [];
        
        connection    = 0;
    end
    
    methods (Access = public)
        function obj = Computation(conn)
            
            if (conn == 0)
                error('No Connection class given');
            end
            
            obj.connection    = conn;
        end
        
        function vRange = GetRangeBins(obj)
            NFFT    =   obj.connection.ConGetFileParam('Range_NFFT');
            c0      =   1./sqrt(4.*pi.*1e-7.*8.85e-12);
            kf      =   (obj.connection.ConGetFileParam('fStop') - obj.connection.ConGetFileParam('fStrt'))/obj.connection.ConGetFileParam('TRampUp');
            fs      =   obj.connection.ConGetFileParam('fs');
            Range   =   [0:NFFT/2].'./NFFT.*fs.*c0/(2.*kf);
            dR      =   1.'./NFFT.*fs.*c0/(2.*kf);    
            
            RMinIdx =   round(obj.rpMin./dR)+1;
            RMaxIdx =   round(obj.rpMax./dR)+1;
            
            if RMaxIdx > NFFT./2 + 1
                RMaxIdx = NFFT./2 + 1;
            end
            if RMinIdx < 1
                RMinIdx = 1;
            end
            
            vRange  =   Range(RMinIdx:RMaxIdx);
            
        end
        
        function vVel = GetVelBins(obj)
                fStop  = obj.connection.ConGetFileParam('fStop');
                fStrt  = obj.connection.ConGetFileParam('fStrt');
                NFFTVel = obj.connection.ConGetFileParam('Vel_NFFT');
                Tp     = obj.connection.ConGetFileParam('Tp');
                c0     = 1./sqrt(4.*pi.*1e-7.*8.85e-12);
                
                fc       = (fStop + fStrt)/2;
                vVel = [-NFFTVel./2:NFFTVel./2-1].'./NFFTVel.*(1/Tp).*c0/(2.*fc);
            
        end        
        
        function Plot (obj, Data)
            if (obj.dataType <= 1)
            elseif (obj.dataType == 2)
                clf;
                figure(1);
                for chn = 1:obj.nrChn
                    plot(obj.viewX, 20.*log10(abs(Data(1:end,chn,1))));
                    hold on;
                end
            elseif (obj.dataType == 3)
                figure(1);
                imagesc(obj.viewY,obj.viewX,20.*log10(abs(Data(1:end,:,1))+0.5e-6));
                colormap(jet)
                drawnow;
            elseif (obj.dataType == 4)
                Targets = Data;
                TarPosFastCnt   = 0;
                TarPosSlowCnt   = 0;
                TarNegFastCnt   = 0;
                TarNegSlowCnt   = 0;
                TarPosFastRange = zeros(numel(Targets));
                TarPosSlowRange = zeros(numel(Targets));
                TarNegFastRange = zeros(numel(Targets));
                TarNegSlowRange = zeros(numel(Targets));
                TarPosFastAng   = zeros(numel(Targets));
                TarPosSlowAng   = zeros(numel(Targets));
                TarNegFastAng   = zeros(numel(Targets));
                TarNegSlowAng   = zeros(numel(Targets));

                for TarIdx = 1:numel(Targets)
                    if (Targets(TarIdx).Vel < 0)
                        if (Targets(TarIdx).Vel < 1)
                            TarNegFastCnt   = TarNegFastCnt + 1;
                            TarNegFastRange(TarNegFastCnt) = Targets(TarIdx).Range;
                            TarNegFastAng(TarNegFastCnt)   = Targets(TarIdx).Ang;
                        else
                            TarNegSlowCnt   = TarNegSlowCnt + 1;
                            TarNegSlowRange(TarNegSlowCnt) = Targets(TarIdx).Range;
                            TarNegSlowAng(TarNegSlowCnt)   = Targets(TarIdx).Ang;
                        end
                    else
                        if (Targets(TarIdx).Vel > 1)
                            TarPosFastCnt   = TarPosFastCnt + 1;
                            TarPosFastRange(TarPosFastCnt) = Targets(TarIdx).Range;
                            TarPosFastAng(TarPosFastCnt)   = Targets(TarIdx).Ang;
                        else
                            TarPosSlowCnt   = TarPosSlowCnt + 1;
                            TarPosSlowRange(TarPosSlowCnt) = Targets(TarIdx).Range;
                            TarPosSlowAng(TarPosSlowCnt)   = Targets(TarIdx).Ang;
                        end
                    end
                end

                figure(1);
                clf;
                if (TarPosFastCnt > 0)
                    TarPosFastRange = TarPosFastRange(1:TarPosFastCnt);
                    TarPosFastAng   = TarPosFastAng(1:TarPosFastCnt);
                    scatter(TarPosFastRange.*sin(TarPosFastAng), TarPosFastRange.*cos(TarPosFastAng), 50, 'r', 'filled');
                    if (TarPosSlowCnt > 0 || TarNegFastCnt > 0 || TarNegSlowCnt > 0)
                        hold on;
                    end
                end

                if (TarPosSlowCnt > 0)
                    TarPosSlowRange = TarPosSlowRange(1:TarPosSlowCnt);
                    TarPosSlowAng   = TarPosSlowAng(1:TarPosSlowCnt);
                    scatter(TarPosSlowRange.*sin(TarPosSlowAng), TarPosSlowRange.*cos(TarPosSlowAng), 50, 'r');
                    if (TarNegFastCnt > 0 || TarNegSlowCnt > 0)
                        hold on;
                    end
                end

                if (TarNegFastCnt > 0)
                    TarNegFastRange = TarNegFastRange(1:TarNegFastCnt);
                    TarNegFastAng   = TarNegFastAng(1:TarNegFastCnt);
                    scatter(TarNegFastRange.*sin(TarNegFastAng), TarNegFastRange.*cos(TarNegFastAng), 50, 'b', 'filled');
                    if (TarNegSlowCnt > 0)
                        hold on;
                    end
                end

                if (TarNegSlowCnt > 0)
                    TarNegSlowRange = TarNegSlowRange(1:TarNegSlowCnt);
                    TarNegSlowAng   = TarNegSlowAng(1:TarNegSlowCnt);
                    scatter(TarNegSlowRange.*sin(TarNegSlowAng), TarNegSlowRange.*cos(TarNegSlowAng), 50, 'b');
                end

                xlabel('x (m)')
                ylabel('y (m)')
                axis([-100 100 0 500])
                grid on;
            
            elseif (obj.dataType == 5)
                figure(1);
                for Idx = 1:numel(Data)
                    plot([Data{Idx}.X], [Data{Idx}.Y],'x')
                    plot([Data{Idx}.HistX], [Data{Idx}.HistY],'-r')
                end
            end
        end
        
        function CreateView (obj)
            if (obj.dataType <= 1)   
                
            elseif (obj.dataType == 2)
                NFFT   =    obj.connection.ConGetFileParam('Range_NFFT');
                c0     =    1./sqrt(4.*pi.*1e-7.*8.85e-12);
                kf     =    (obj.connection.ConGetFileParam('fStop') - obj.connection.ConGetFileParam('fStrt'))/obj.connection.ConGetFileParam('TRampUp');
                fs     =    obj.connection.ConGetFileParam('fs');
                obj.viewX = [0:NFFT/2].'./NFFT.*fs.*c0/(2.*kf);
                
                if (obj.rpMin ~= 0)
                    obj.viewX = obj.viewX + obj.rpMin;
                end

                obj.viewX = obj.viewX(1:obj.rpLen);   
            
            elseif (obj.dataType == 3)
                fStop  = obj.connection.ConGetFileParam('fStop');
                fStrt  = obj.connection.ConGetFileParam('fStrt');
                NFFTVel = obj.connection.ConGetFileParam('Vel_NFFT');
                NFFT   = obj.connection.ConGetFileParam('Range_NFFT');
                Tp     = obj.connection.ConGetFileParam('Tp');
                c0     = 1./sqrt(4.*pi.*1e-7.*8.85e-12);
                kf     = (fStop - fStrt)/obj.connection.ConGetFileParam('TRampUp');
                fs     = obj.connection.ConGetFileParam('fs');
                
                fc       = (fStop + fStrt)/2;
                vFreqVel = [-NFFTVel./2:NFFTVel./2-1].'./NFFTVel.*(1/Tp);
                obj.viewY = vFreqVel*c0/(2.*fc); 

                obj.viewX = [0:NFFT/2].'./NFFT.*fs.*c0/(2.*kf);
                
                if (obj.rpMin ~= 0)
                    obj.viewX = obj.viewX + obj.rpMin;
                end

                obj.viewX = obj.viewX(1:obj.rpLen);   
            
            elseif (obj.dataType == 4)
            
            elseif (obj.dataType == 5)
            end
        end
        
        function Enable (obj)
            obj.isSupported = 1;
        end
        
        function Disable (obj)
            obj.isSupported = 1;
        end
        
        function Type = GetDataType (obj)
            Type = obj.dataType;
        end 
        
        function SetNrChn(obj, nrChn)
            obj.nrChn = nrChn;
        end
         
        function SetDataType(obj, Type, Param)
            if obj.isSupported < 1
                error('Computations are not supported with this version.');
            end
            
            if (Type == 2 && numel(Param) == 5)
                obj.dataType = Type;
                obj.rpLen    = uint32(Param(1));
                obj.rpMin    = Param(2);
                obj.rpMax    = Param(3);
                obj.rpMult   = uint32(Param(4));
                obj.rpSort   = uint32(Param(5));
                
            elseif (Type == 3 && numel(Param) == 6)
                obj.dataType = Type;
                obj.rpLen    = uint32(Param(1));
                obj.rpMin    = Param(2);
                obj.rpMax    = Param(3);
                obj.rdLen    = uint32(Param(4));
                obj.rdVelMin = Param(5);
                obj.rdVelMax = Param(6);
                
            elseif (Type == 4 && numel(Param) == 1)
                obj.dataType = Type;
                obj.dlLen    = uint32(Param(1));
                
            elseif (Type == 5 && numel(Param) == 4)
                obj.dataType    = Type;
                obj.ttNumTar    = uint32(Param(1));
                obj.ttTarSize   = uint32(Param(2));
                obj.ttNumTracks = uint32(Param(3));
                obj.ttNumHist   = uint32(Param(4));
                
            else
                disp('Not enough parameters received.');
            end
        end
               
        function SetType (obj, stType)
            conn = obj.connection;
            
            Data = zeros(4 + 0, 'uint32');
            Data(1) = uint32(2^32-1);
            Data(2) = uint32(0);
            Data(4) = uint32(0);
            
            if strcmp(stType, obj.Raw)
                id = 0;
                Data(3) = uint32(id);
                                
                Ret = conn.CmdSend(0, hex2dec('6160'), Data, 0);
                Ret = conn.CmdRecv();
                
                obj.dataType = id;
                return;
            end
                
            if obj.isSupported < 1
                error('Computations are not supported with this version.');           
            end
            
            if strcmp(stType, obj.RP)
                if (obj.isSet_FuSca > 0 && obj.isSet_fStrt > 0 && obj.isSet_fStop > 0 && obj.isSet_TRampUp > 0 &&  obj.isSet_fs > 0 && obj.isSet_CalRe > 0 && obj.isSet_CalIm > 0)
                    id = 2;
                    Data(3) = uint32(id);
                    
                    Ret = conn.CmdSend(0, hex2dec('6160'), Data, 0);
                    Ret = conn.CmdRecv();
                    
                    obj.SetDataType(id, swapbytes(typecast(Ret, 'single')));
                end
                
            elseif strcmp(stType, obj.RD)
                if (obj.isSet_Np > 0 && obj.isSet_Tp > 0)
                    id = 3;
                    Data(3) = uint32(id);
                    
                    obj.SetParam('RP_SortOutput', 0);
                    
                    Np = conn.ConGetFileParam('Np');
                    conn.cExtMult = Np;
                    
                    Ret = conn.CmdSend(0, hex2dec('6160'), Data, 0);
                    Ret = conn.CmdRecv();
                                    
                    obj.SetDataType(id, swapbytes(typecast(Ret, 'single')));
                end
                    
            elseif strcmp(stType, obj.DL)
                id = 4;
                Data(3) = uint32(id);
                
                obj.SetParam('RP_SortOutput', 0);
                
                Np = conn.ConGetFileParam('Np');
                conn.cExtMult = Np;
                
                Ret = conn.CmdSend(0, hex2dec('6160'), Data, 0);
                Ret = conn.CmdRecv();
                                
                obj.SetDataType(id, swapbytes(typecast(Ret, 'single')));
                
            elseif strcmp(stType, obj.TT)
                id = 5;  
                Data(3) = uint32(id);
                
                obj.SetParam('RP_SortOutput', 0);
                
                Np = conn.ConGetFileParam('Np');
                conn.cExtMult = Np;
                
                Ret = conn.CmdSend(0, hex2dec('6160'), Data, 0);
                Ret = conn.CmdRecv();
                
                obj.SetDataType(id, swapbytes(typecast(Ret, 'single')));
                
            else
                disp('DataType unknown');
            end
        end
                
        function SetParam (obj, stParam, val)
            conn = obj.connection;
            
            if strcmp(stParam, 'FuSca')
                conn.ConSetFileParam('FuSca', val, 'DOUBLE');
                obj.isSet_FuSca   = 1;
            elseif strcmp(stParam, 'fStrt')
                conn.ConSetFileParam('fStrt', val, 'DOUBLE');
                obj.isSet_fStrt   = 1;
            elseif strcmp(stParam, 'fStop')
                conn.ConSetFileParam('fStop', val, 'DOUBLE');
                obj.isSet_fStop   = 1;
            elseif strcmp(stParam, 'TRampUp')
                conn.ConSetFileParam('TRampUp', val, 'DOUBLE');
                obj.isSet_TRampUp = 1;
            elseif strcmp(stParam, 'fs')
                conn.ConSetFileParam('fs', val, 'DOUBLE');
                obj.isSet_fs      = 1;
            elseif strcmp(stParam, 'CalRe')
                conn.ConSetFileParam('CalRe', val, 'ARRAY64');
                obj.isSet_CalRe   = 1;
            elseif strcmp(stParam, 'CalIm')
                conn.ConSetFileParam('CalIm', val, 'ARRAY64');
                obj.isSet_CalIm   = 1;
            elseif strcmp(stParam, 'Tp')
                conn.ConSetFileParam('Tp', val, 'DOUBLE');
                obj.isSet_Tp      = 1;
            elseif strcmp(stParam, 'Np')
                conn.ConSetFileParam('Np', val, 'INT');
                obj.isSet_Np      = 1;
            elseif strcmp(stParam, 'Range_NFFT')
                conn.ConSetFileParam('Range_NFFT', val, 'INT');
            elseif strcmp(stParam, 'Range_IniN')
                conn.ConSetFileParam('Range_IniN', val, 'INT');
            elseif strcmp(stParam, 'Range_WinType')
                conn.ConSetFileParam('Range_WinType', val, 'INT');
            elseif strcmp(stParam, 'Range_SubtractMean')
                conn.ConSetFileParam('Range_SubtractMean', val, 'INT');
            elseif strcmp(stParam, 'Range_RMin')
                conn.ConSetFileParam('Range_RMin', val, 'DOUBLE');
            elseif strcmp(stParam, 'Range_RMax')
                conn.ConSetFileParam('Range_RMax', val, 'DOUBLE');
            elseif strcmp(stParam, 'RP_Mult')
                conn.ConSetFileParam('RP_Mult', val, 'INT');
            elseif strcmp(stParam, 'RP_SortOutput')
                conn.ConSetFileParam('RP_SortOutput', val, 'INT');
            elseif strcmp(stParam, 'Vel_NFFT')
                conn.ConSetFileParam('Vel_NFFT', val, 'INT');
            elseif strcmp(stParam, 'Vel_WinType')
                conn.ConSetFileParam('Vel_WinType', val, 'INT');
            elseif strcmp(stParam, 'RD_BufSiz')
                conn.ConSetFileParam('RD_BufSiz', val, 'INT');        
            elseif strcmp(stParam, 'Ang_NFFT')
                conn.ConSetFileParam('Ang_NFFT', val, 'INT');
            elseif strcmp(stParam, 'Ang_Interpolate')
                conn.ConSetFileParam('Ang_Interpolate', val, 'INT');       
            elseif strcmp(stParam, 'Ang_Flip')
                conn.ConSetFileParam('Ang_Flip', val, 'INT');
            elseif strcmp(stParam, 'Thres_Mult')
                conn.ConSetFileParam('Thres_Mult', val, 'DOUBLE');
            elseif strcmp(stParam, 'Thres_Mult2')
                conn.ConSetFileParam('Thres_Mult2', val, 'DOUBLE');
            elseif strcmp(stParam, 'Thres_Old')
                conn.ConSetFileParam('Thres_Old',  val, 'DOUBLE');
            elseif strcmp(stParam, 'Thres_VelMin')
                conn.ConSetFileParam('Thres_VelMin', val, 'DOUBLE');
            elseif strcmp(stParam, 'Thres_VelMax')
                conn.ConSetFileParam('Thres_VelMax', val, 'DOUBLE');
            elseif strcmp(stParam, 'Thres_UseVel')
                conn.ConSetFileParam('Thres_UseVel', val, 'INT');            
            elseif strcmp(stParam, 'Thres_Range1')
                conn.ConSetFileParam('Thres_Range1', val, 'DOUBLE');
            elseif strcmp(stParam, 'Thres_Range2')
                conn.ConSetFileParam('Thres_Range2', val, 'DOUBLE');
            elseif strcmp(stParam, 'DL_NumDetections')
                conn.ConSetFileParam('DL_NumDetections', val, 'INT');
            elseif strcmp(stParam, 'DL_SortAsc')
                conn.ConSetFileParam('DL_SortAsc', val, 'INT');
            elseif strcmp(stParam, 'DL_BufSiz')
                conn.ConSetFileParam('DL_BufSiz', val, 'INT');
            elseif strcmp(stParam, 'DL_Mode')
                conn.ConSetFileParam('DL_Mode', val, 'INT');
            elseif strcmp(stParam, 'Track_SigmaX')
                conn.ConSetFileParam('Track_SigmaX', val, 'DOUBLE');
            elseif strcmp(stParam, 'Track_SigmaY')
                conn.ConSetFileParam('Track_SigmaY', val, 'DOUBLE');
            elseif strcmp(stParam, 'Track_dT')
                conn.ConSetFileParam('Track_dT', val, 'DOUBLE');
            elseif strcmp(stParam, 'Track_VarX')
                conn.ConSetFileParam('Track_VarX', val, 'DOUBLE');
            elseif strcmp(stParam, 'Track_VarY')
                conn.ConSetFileParam('Track_VarY', val, 'DOUBLE');
            elseif strcmp(stParam, 'Track_VarVel')
                conn.ConSetFileParam('Track_VarVel', val, 'DOUBLE');
            elseif strcmp(stParam, 'Track_MinVarX')
                conn.ConSetFileParam('Track_MinVarX', val, 'DOUBLE');
                conn.ConSetFileParam('Track_HasMinVar', 1, 'INT');
            elseif strcmp(stParam, 'Track_MinVarY')
                conn.ConSetFileParam('Track_MinVarY', val, 'DOUBLE');
                conn.ConSetFileParam('Track_HasMinVar', 1, 'INT');
            elseif strcmp(stParam, 'TT_NumDetections')
                conn.ConSetFileParam('TT_NumDetections', val, 'INT');
            elseif strcmp(stParam, 'TT_NumTracks')
                conn.ConSetFileParam('TT_NumTracks', val, 'INT');
            elseif strcmp(stParam, 'TT_HistLen')
                conn.ConSetFileParam('TT_HistLen', val, 'INT');
            elseif strcmp(stParam, 'TT_MaxHist')
                conn.ConSetFileParam('TT_MaxHist', val, 'INT');
            elseif strcmp(stParam, 'TT_UseAreas')
                conn.ConSetFileParam('TT_UseAreas', val, 'INT');
            elseif strcmp(stParam, 'TT_Areas')
                conn.ConSetFileParam('TT_Areas', val, 'ARRAY64');
            elseif strcmp(stParam, 'TT_ExcludeVel')
                conn.ConSetFileParam('TT_ExcludeVel', val, 'INT');
            elseif strcmp(stParam, 'TT_Vel_UseRange')
                conn.ConSetFileParam('TT_Vel_UseRange', val, 'INT');
            elseif strcmp(stParam, 'TT_Vel_Min')
                conn.ConSetFileParam('TT_Vel_Min', val, 'DOUBLE');
            elseif strcmp(stParam, 'TT_Vel_Max')
                conn.ConSetFileParam('TT_Vel_Max', val, 'DOUBLE');
            elseif strcmp(stParam, 'TT_BufSiz')
                conn.ConSetFileParam('TT_BufSiz', val, 'INT');
            elseif strcmp(stParam, 'TT_RemCnt')
                conn.ConSetFileParam('TT_RemCnt', val, 'INT');
            elseif strcmp(stParam, 'TT_OutputCluster')
                conn.ConSetFileParam('TT_OutputCluster', val, 'INT');
            end
        end
        
        function Data = GetData(obj, NrPack)
            conn = obj.connection;
                
            if obj.dataType == 2
                %% range profile
                rpData = conn.ConGetData(NrPack * obj.rpLen * obj.nrChn * 8);
                rpData = typecast(rpData, 'single');
                cData = complex(rpData(1:2:end), rpData(2:2:end));
                Data = reshape(cData, obj.rpLen, obj.nrChn, NrPack);
                %if (obj.rpSort == 1)
                    %% no sort
                %    Data = reshape(cData, obj.rpLen, obj.nrChn, obj.rpMult, NrPack);
                %else
                %    Data = reshape(cData, obj.rpLen, obj.rpMult, obj.nrChn, NrPack);
                %    Data = permute(Data, [1, 3, 2, 4]);
                %end
                
            elseif obj.dataType == 3
                %% range doppler
                rdData = conn.ConGetData(NrPack * obj.rpLen * obj.rdLen * obj.nrChn * 8);
                rdData = typecast(rdData, 'single');
                cData = complex(rdData(1:2:end), rdData(2:2:end));

                Data = reshape(cData, obj.rdLen, obj.rpLen, obj.nrChn, NrPack);       
                Data = permute(Data, [2 1 3 4]); 
                
            elseif obj.dataType == 4
                %% detection list
                DtypeLen = 4;
                tlData = conn.ConGetData(NrPack * obj.dlLen * (5 * DtypeLen + 2 * DtypeLen * obj.nrChn));
                tlData = typecast(tlData, 'single');
                tlData = reshape(tlData, 5 + 2 * obj.nrChn, obj.dlLen);
                Data = struct('Range', {}, 'Vel', {}, 'Mag', {}, 'Ang', {}, 'Noise', {}, 'Amp', {});
                for tIdx = 1:(NrPack * obj.dlLen)
                    if (tlData(1, tIdx) == 0 && tlData(2, tIdx) == 0 && tlData(3, tIdx) == 0 && tlData(4, tIdx) == 0)
                    else
                        Data(tIdx).Range = tlData(1, tIdx);
                        Data(tIdx).Vel   = tlData(2, tIdx);
                        Data(tIdx).Mag   = tlData(3, tIdx);
                        Data(tIdx).Ang   = tlData(4, tIdx);
                        Data(tIdx).Noise = tlData(5, tIdx);
                        Data(tIdx).Amp   = complex(tlData(6:2:end, tIdx), tlData(7:2:end, tIdx));
                    end
                end
                %% Todo DataIdx
                
            elseif obj.dataType == 5
                %% track list
                len    = obj.dtypeLen * ( 3 + ( 9 + 2 * obj.ttNumHist ) * obj.ttNumTracks + obj.ttTarSize * obj.ttNumTar );
                ttData = conn.ConGetData(NrPack * len);
                ttData = typecast(ttData, 'uint32');
                ttData = ttData(4:end); % ignore first three entries, as they contain the LenHist, Target count and tar size values
                ttData = typecast(ttData, 'single');
                
                Tracks = [];
                for trackIdx = 0:(obj.ttNumTracks-1)
                    Track.Id    = ttData((9 + 2 * obj.ttNumHist) * trackIdx + 1);
                    Track.X     = ttData((9 + 2 * obj.ttNumHist) * trackIdx + 2);
                    Track.Y     = ttData((9 + 2 * obj.ttNumHist) * trackIdx + 3);
                    Track.Vel   = ttData((9 + 2 * obj.ttNumHist) * trackIdx + 4);
                    Track.VelX  = ttData((9 + 2 * obj.ttNumHist) * trackIdx + 5);
                    Track.VelY  = ttData((9 + 2 * obj.ttNumHist) * trackIdx + 6);
                    Track.Mag   = ttData((9 + 2 * obj.ttNumHist) * trackIdx + 7);
                    Track.VarX  = ttData((9 + 2 * obj.ttNumHist) * trackIdx + 8);
                    Track.VarY  = ttData((9 + 2 * obj.ttNumHist) * trackIdx + 9);
                    Track.HistX = [];
                    Track.HistY = [];
                    
                    hist = ttData(((9 + 2 * obj.ttNumHist) * trackIdx + 10):end);
                    if ~(Track.Id == 0 && Track.X == 0 && Track.Y == 0 && Track.VelX == 0 && Track.VelY == 0)
                        for histIdx = 0:(obj.ttNumHist-1)
                            HistX = hist(2 * histIdx + 1);
                            HistY = hist(2 * histIdx + 2);
                            if ~(HistX == 0 && HistY == 0)
                                Track.HistX = [Track.HistX HistX];
                                Track.HistY = [Track.HistY HistY];
                            else
                                break;
                            end
                        end
                        Tracks = [Tracks Track];
                    else
                        break;
                    end
                end
                
                Detections = [];
                Offset = (9 + 2 * obj.ttNumHist) * obj.ttNumTracks + 1;
                ttData = ttData(Offset:end);
                for tarIdx = 0:(obj.ttNumTar-1)
					if obj.ttTarSize == 2
						Det.X = ttData(obj.ttTarSize * tarIdx + 1);
						Det.Y = ttData(obj.ttTarSize * tarIdx + 2);
						
						if (Det.X == 0 && Det.Y == 0)
							break;
						else
							Detections = [Detections Det];              
						end
                    else
						Det.Range = ttData(obj.ttTarSize * tarIdx + 1);
						Det.Vel   = ttData(obj.ttTarSize * tarIdx + 2);
						Det.Mag   = ttData(obj.ttTarSize * tarIdx + 3);
						Det.Ang   = ttData(obj.ttTarSize * tarIdx + 4);
						Det.Noise = ttData(obj.ttTarSize * tarIdx + 5);
						Det.Track = typecast(ttData(obj.ttTarSize * tarIdx + 6), 'int32');
						Det.Amp   = complex(ttData((obj.ttTarSize * tarIdx + 7):2:(obj.ttTarSize * tarIdx + 7 + 2 * obj.nrChn - 1)), ttData((1 + obj.ttTarSize * tarIdx + 7):2:(obj.ttTarSize * tarIdx + 7 + 2 * obj.nrChn - 1)));
						Det.X     = Det.Range * sin(Det.Ang);
						Det.Y     = Det.Range * cos(Det.Ang);
						
						if (Det.Range == 0 && Det.Ang == 0 && Det.Vel == 0)
							break;
						else
							Detections = [Detections Det];
						end
					end
                end
                                        
                %% Todo DataIdx
                Data.Detections = Detections;
                Data.Tracks  = Tracks;
            end
        end
    end     
end