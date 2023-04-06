"""@package UsbADI
Implements a simple usb class, which loads a DLL
The DLL uses the WinUSB API to Read and Write blocks via USB
"""

import ctypes
import sys
import struct
from numpy import *


class UsbADI():
    """Implements an interface to the WinUSB driver

    Loads the dll via ctypes. Arguments which are passed to functions
    (which mainly act as wrapper) are casted to the correct type
    """

    def __init__(self):
        """Load DLL and initialize variables"""
        self.usb            = ctypes.cdll.LoadLibrary("Dll/usb.dll")
        self.UsbOpen        = False

        self.VersionMajor   = self.usb.GetVersMajor()
        self.VersionMinor   = self.usb.GetVersMinor()
        self.VersionFix     = self.usb.GetVersFix()

        # Open Usb Device
        self.UsbOpen        = self.ConnectToDevice()

        self.FuSca           =   0.498 / 65536;



    """@brief Sends Data to the device (selected by mask) using SPI on board
        
        This function is needed to set registers of device connected via SPI
        @param[in] SpiCfg - The selected device
        @param[in] Regs - A list containing the SPI register configuration
        @return array with boolean result and array with data on success
    """
    def Dsp_SendSpiData(self, SpiCfg, Regs):
        Regs = Regs.flatten(1)
        if (len(Regs) > 28):
            Regs = Regs[0:28]

        DspCmd = zeros(3 + len(Regs), dtype='uint32')
        Cod = int('0x9017', 0)
        DspCmd[0] = SpiCfg["Mask"]
        DspCmd[1] = 1
        DspCmd[2] = SpiCfg["Chn"]
        DspCmd[3:] = Regs

        Ret = self.CmdSend(0, Cod, DspCmd)
        Ret = self.CmdRecv()
        return Ret

    """@brief Returns the DSP software info
        @return - result (success/not) + Software information
    """
    def Dsp_GetSwVers(self):
        DspCmd = zeros(1, dtype='uint32')
        Cod = int('0x900E', 0)
        DspCmd[0] = 0
        Vers = self.CmdSend(0, Cod, DspCmd)
        Vers = self.CmdRecv()
        dRet = {
            "SwPatch": -1,
            "SwMin": -1,
            "SwMaj": -1,
            "SUid": -1,
            "HUid": -1
        }
        if Vers[0] is True:
            Data = Vers[1]
            if len(Data) > 2:
                Tmp = Data[0]
                SwPatch = int(Tmp % 2 ** 8)
                Tmp = floor(Tmp / 2 ** 8)
                SwMin = int(Tmp % 2 ** 8)
                SwMaj = int(floor(Tmp / 2 ** 8))
                dRet["SwPatch"]     = SwPatch
                dRet["SwMin"]       = SwMin
                dRet["SwMaj"]       = SwMaj
                dRet["SUid"]        = Data[1]
                dRet["HUid"]        = Data[2]
            else:
                print("No Version information available")
        return dRet


    """@brief Returns the DSP software version
        @return list containing the DSP software version
    """
    def BrdGetSwVers(self):
        return self.Dsp_GetSwVers()

    """@brief Prints the DSP software version
        @return -
    """
    def BrdDispSwVers(self):
        print("")
        print("===================================")
        VersInfo = self.Dsp_GetSwVers()
        print("Sw-Rev: " + str(VersInfo["SwMaj"]) + "." + str(VersInfo["SwMin"]) + "." + str(VersInfo["SwPatch"]))
        print("Sw-UID: " + str(VersInfo["SUid"]))
        print("Hw-UID: " + str(VersInfo["HUid"]))
        print("===================================")

    """@brief Returns the UID of the Device
        @return - result (success/not) + UID of device
    """
    def BrdGetUID(self):
        Cmd = ones(2, dtype='uint32')
        Cod = int("0x9030", 0)
        Cmd[1] = 0

        Ret = self.CmdSend(0, Cod, Cmd)
        Ret = self.CmdRecv()
        return Ret
        
    def BrdDispUID(self):
        Uid = self.BrdGetUID();
        
        if (Uid[0]):
            Uid = Uid[1];
            print("")
            print("===================================")
            print("UID:    ", format(Uid[1], '08X'), format(Uid[0], '08X'), ' h', sep='')
            print("===================================")
    
    def BrdDispInf(self):
        Cmd = ones(2, dtype='uint32')
        Cod = int("0x9013", 0)
        Cmd[1] = 0

        Ret = self.CmdSend(0, Cod, Cmd)
        Ret = self.CmdRecv()
        
        # AD7415 TempSensor
        Temp = Ret[1][1];
        if (Temp >= 512):
            # negative temperature
            Temp = (Temp - 1024);
        Temp = Temp / 4;
        
        print("")
        print("===================================")
        print("Sw-UID: " + str(Ret[1][0]))
        print("Temp:   " + str(Temp) + "°C");
        print("===================================")
        
        return Ret

    """@brief Reads a 32bit value, starting at given address
        @param[in] - Read address 
        @return - result (success/not) + Data read
    """
    def BrdRdEEPROM(self, Addr):
        Cmd     = ones(3, dtype='uint32')
        Cod     = int("0x9030", 0)
        Cmd[1]  = 2
        Cmd[2]  = Addr

        Ret     = self.CmdSend(0, Cod, Cmd)
        Ret     = self.CmdRecv()
        return Ret

    """@brief Writes a 32 bit value (size in eeprom is 8 bit), starting at given address 
        @param[in] - Write address 
        @param[in] - Data to write
        @return - result (success/not)
    """
    def BrdWrEEPROM(self, Addr, Data):
        Cmd = ones(4, dtype='uint32')
        Cod = int("0x9030", 0)
        Cmd[1] = 1
        Cmd[2] = Addr
        Cmd[3] = Data

        Ret = self.CmdSend(0, Cod, Cmd)
        Ret = self.CmdRecv()

        return Ret

    """@brief Return calibration data complete
        @return - result (success/not) + Calibration data
    """
    def BrdGetCalDat(self):
        CalDat      = zeros(32*4, dtype='uint8')
        for Loop in range(32*4):
            rdelem = self.BrdRdEEPROM(Loop)
            CalDat[Loop] = uint8(rdelem[1][0])
        CalRet = zeros(32, dtype='uint32')
        CalRdCnt = 0
        for Loop in range(len(CalRet)):
            CalRet[Loop] = CalDat[CalRdCnt] \
                           | (CalDat[CalRdCnt+1] << 8) \
                           | (CalDat[CalRdCnt+2] << 16) \
                           | (CalDat[CalRdCnt+3] << 24)
            CalRdCnt = CalRdCnt + 4
        dCal            =   dict()

        # Convert: data to double and account for signed values in case of cal data
        ConvDat         =   zeros(16)
        for Idx in range(0,16):
            if CalRet[Idx] > 2**31:
                ConvDat[Idx]    =   CalRet[Idx] - 2**32
            else:
                ConvDat[Idx]    =   CalRet[Idx]

        CalDat          =   zeros(8, dtype='complex')
        CalDat[:]       =   double(ConvDat[0:16:2])/2**24 + 1j*double(ConvDat[1:16:2])/2**24

        dCal["Dat"]     =   CalDat
        dCal["Type"]    =   CalRet[16]
        dCal["Date"]    =   CalRet[17]
        dCal["R"]       =   CalRet[18]/2**16
        dCal["RCS"]     =   CalRet[19]/2**16
        dCal["TxGain"]  =   CalRet[20]/2**16
        dCal["IfGain"]  =   CalRet[21]/2**16
        return dCal

    """@brief Set calibration data
        @param[in] - Calibration data
        @return - result (success/not)
    """
    def BrdSetCalDat(self, dCalData):
        CalReal         =   real(dCalData["Dat"])*2**24
        CalImag         =   imag(dCalData["Dat"])*2**24

        CalData         =   zeros(22,dtype='uint32')
        CalData[0:16:2] =   CalReal
        CalData[1:16:2] =   CalImag
        CalData[16]     =   dCalData["Type"]
        CalData[17]     =   dCalData["Date"]
        CalData[18]     =   dCalData["R"]*2**16
        CalData[19]     =   dCalData["RCS"]*2**16
        CalData[20]     =   dCalData["TxGain"]*2**16
        CalData[21]     =   dCalData["IfGain"]*2**16
        if len(CalData) < 32:
            DatSend = zeros(len(CalData), dtype='uint32')
            DatSend[0:] = CalData
            WrDat = zeros(len(CalData)*4, dtype='uint8')
            SendCnt = 0
            for Loop in range(len(DatSend)):
                uint32 = struct.pack("I", DatSend[Loop])
                arr = struct.unpack("B" * 4, uint32)
                WrDat[SendCnt]    = arr[0]
                WrDat[SendCnt+1]  = arr[1]
                WrDat[SendCnt+2]  = arr[2]
                WrDat[SendCnt+3]  = arr[3]
                SendCnt = SendCnt + 4
            for i in range(len(WrDat)):
                self.BrdWrEEPROM(i, WrDat[i])
            return True
        else:
            print("CalData array to long to fit in EEPROM")
            return False

    def CmdBuild(self, Ack, CmdCod, Data):
        LenData     = len(Data) + 1
        TxData      = zeros(LenData, dtype=uint32)
        TxData[0]   = (2**24)*Ack + (2**16)*LenData + CmdCod
        TxData[1:]  = uint32(Data)
        return TxData

    def CmdSend(self, Ack, Cod, Data):
        Cmd         = self.CmdBuild(Ack, Cod, Data)
        if not self.usb.UsbWriteCmd(ctypes.c_int(len(Cmd)), Cmd.ctypes):
            print("Cmd Write failed")

    def CmdRecv(self):
        Result      = (False, )
        arr = (ctypes.c_char * (4))()
        NrBytes = self.usb.UsbRead(4, arr)
        if NrBytes != 0:
            Header      = fromstring(arr, dtype='uint32')
            LenRxData   = Header[0]//(2**16)
            RxBytes = (ctypes.c_char * (LenRxData-1)*4) ()

            RxBytesLen     = self.usb.UsbRead(int((LenRxData - 1)*4), RxBytes)
            if RxBytesLen == ((LenRxData - 1)*4):
                Data    = zeros(LenRxData - 1, dtype='uint32')
                Data    = fromstring(RxBytes, dtype='uint32')
                Result  = (True, Data)
            else:
                Result  = (False, )
                print("len(RxBytes) wrong: %d != %d" % (len(RxBytes)), (LenRxData - 1)*4)
        else:
            print("Board Not Responding")
        return Result

    def CmdReadDatLen(self, Ack, Cod, Data, Len):

        Exit = False
        try: 
            Ret = self.CmdSend(Ack, Cod, Data)
            RxBytes = (ctypes.c_char * Len*2) ()
            RxBytesLen = self.usb.UsbRead(int(2*Len), RxBytes)
            if RxBytesLen == 2*Len:
                Data    = zeros(Len, dtype='int16')
                Data    = fromstring(RxBytes, dtype='int16')
            else:
                print("len(RxBytes) wrong: %d != %d" % (len(RxBytes)), (LenRxData - 1)*4)

        except KeyboardInterrupt:
            print('Keyboard Inerrupt')
            Exit = True

        finally:
            DatLen = len(Data)
            if DatLen == Len:
                Data = reshape(Data,(int(Len/4), 4))

            Ret = self.CmdRecv()

            if Exit:
                sys.exit(0)

        return Data


    def GetDllVersion(self):
        """Prints the DLL version number"""
        return str(self.VersionMajor) + "." + str(self.VersionMinor) + "." + str(self.VersionFix)

    def UsbRead(self, len):
        """Reads "len" bytes"""
        Data        = (ctypes.c_char*(int(len))) ()
        RxDataLen   = self.usb.UsbRead(int(len), Data)
        return Data

    def ConnectToDevice(self):
        """Initializes and Opens DLL driver"""
        if self.UsbOpen:
            print("Device already open.")
            return False
        else:
            Ret = self.usb.ConnectToDevice(True)
            return Ret

    def UsbWriteADICmd(self, TxData):
        self.usb.UsbWriteADICmd(ctypes.c_uint32(len(TxData)), TxData.ctypes)

    def __del__(self):
        """Closes Usb handles in DLL"""
        self.usb.CloseGlobalHandles()
