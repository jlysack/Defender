// usb.cpp : Definiert die exportierten Funktionen für die DLL-Anwendung.
//

//*********************************************************************************
// Includes
//*********************************************************************************
#include "mex.h"           // Include header file for matlab mex file functionality
#include "usbdev.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "stdafx.h"

#include "usbdriver.h"
#include "Windows.h"

int     DebugOpen   =   0;
int     DebugNrDev  =   0;
int     DebugLstErr =   0;
HANDLE  g_hRead                         = INVALID_HANDLE_VALUE;     // USB device read handle
HANDLE  g_hWrite                        = INVALID_HANDLE_VALUE;     // USB device write handle
/* AnHa: Handle needs to be closed */
HANDLE  hDevGlob                        = INVALID_HANDLE_VALUE;


void    GetVers(const int nlhs, mxArray *plhs[], const int nrhs, const mxArray *prhs[])
{
    if (nlhs == 1)
    {
        double          *RetData;

        plhs[0]         =   mxCreateDoubleMatrix(3, 1, mxREAL);
        RetData         =   mxGetPr(plhs[0]); 
        RetData[0]      =   (double)GetVersMajor();
        RetData[1]      =   (double)GetVersMinor();
        RetData[2]      =   0.0;     
    }
    else
    {
        printf("DemoRadUsb GetVers :: Number of return parameters!!\n");
    }
}

void    OpenDev(const int nlhs, mxArray *plhs[], const int nrhs, const mxArray *prhs[])
{
    bool        RetVal;

    RetVal  =   ConnectToDevice(true);
    //printf("LstErr Open: %d\n", DebugLstErr);
    //printf("Connected devices: %x \n", DebugNrDev);
    //printf("Open devices: %d \n", DebugOpen);


    if (RetVal == true)
    {
        printf("DemoRad::Connect true\n");
    }
    else
    {
        printf("DemoRad::Connect false\n");
    }
    if (nlhs == 1)
    {
        double          *RetData;

        plhs[0]     =   mxCreateDoubleMatrix(1, 1, mxREAL);
        RetData     =   mxGetPr(plhs[0]); 
        if (RetVal == true)
        {
            RetData[0]      =   1.0F;
        }
        else
        {
            RetData[0]      =   0.0F;
        }    
    }
    //printf("Dev: %d \n", (int)g_hRead);
}

void    CloseDev(const int nlhs, mxArray *plhs[], const int nrhs, const mxArray *prhs[])
{
    
    CloseGlobalHandles();

    if (nlhs != 0)
    {
        printf("DemoRadUsb close :: Does not support return parameter!!\n");
    }
    // printf("DemoRad::CloseDev end\n");
    // printf("LstErr: %d\n", DebugLstErr);
}


void    WriteToDev(const int nlhs, mxArray *plhs[], const int nrhs, const mxArray *prhs[])
{
    bool    RetVal;

    //printf("WriteToDev: %x\n", nrhs);
    RetVal  =   false;

    if ((nrhs == 2) && (mxIsUint32(prhs[1])))
    {
        uint32_t*   Data;
        int         Len;

        Data    =   (uint32_t*)mxGetData(prhs[1]);
        Len     =   (int)mxGetNumberOfElements(prhs[1]);   
        RetVal  =   UsbWriteCmd(Len, Data);
    }
    if (nlhs == 1)
    {
        double          *RetData;

        plhs[0]     =   mxCreateDoubleMatrix(1, 1, mxREAL);
        RetData     =   mxGetPr(plhs[0]); 
        if (RetVal == true)
        {
            RetData[0]      =   1.0F;
        }
        else
        {
            RetData[0]      =   0.0F;
        }    
    }    
}

void    ReadFromDev(const int nlhs, mxArray *plhs[], const int nrhs, const mxArray *prhs[])
{
    int32_t   RetVal;
    uint32_t  Data[4096];

    //printf("ReadFromDev: %x\n", nrhs);
    RetVal  =   0;

    if ((nrhs == 2) && (mxIsInt32(prhs[1])))
    {
        int32_t*    Len;

        Len     =   (int32_t*)mxGetData(prhs[1]);
        RetVal  =   (int)UsbRead((int)(*Len), Data);

    }
    if (nlhs == 1)
    {
        double          *RetData;
        int32_t         Loop;


        if (RetVal != 0)
        {
            plhs[0]     =   mxCreateDoubleMatrix(RetVal/4, 1, mxREAL);
            RetData     =   mxGetPr(plhs[0]); 
            for(Loop = 0; Loop < int32_t(RetVal/4); Loop++)
            {
                RetData[Loop]   =   (double)Data[Loop];
            }
        }
        else
        {
            plhs[0]     =   mxCreateDoubleMatrix(0, 0, mxREAL);
        }    
    }    
}

void    ExecCmd(const int nlhs, mxArray *plhs[], const int nrhs, const mxArray *prhs[])
{
    int32_t     RetVal;
    uint32_t    ReadData[4096];
    uint32_t    Header;
    uint32_t    RetLen;
    int32_t     Loop;

    //printf("WriteToDev: %x\n", nrhs);
    RetVal  =   0;

    if ((nrhs == 2) && (mxIsUint32(prhs[1])))
    {
        uint32_t*   Data;
        int         Len;

        Data    =   (uint32_t*)mxGetData(prhs[1]);
        Len     =   (int)mxGetNumberOfElements(prhs[1]);
        // Send Cmd   
        RetVal  =   UsbWriteCmd(Len, Data);
        for(Loop = 0; Loop < 1000; Loop++);
        RetVal  =   (int)UsbRead(4, ReadData);
        //printf("RetVal: %x", RetVal);
        Header  =   ReadData[0];
        RetLen  =   Header >> 16;
        //printf("RetLen: %x", RetLen);
        RetVal  =   (int)UsbRead((int)4*(RetLen - 1), ReadData);


    }
    if (nlhs == 1)
    {
        double          *RetData;
        int32_t         Loop;

        //printf("ExecCmd Assign %d\n", RetVal);

        if (RetVal != 0)
        {
            plhs[0]     =   mxCreateDoubleMatrix(RetVal/4, 1, mxREAL);
            RetData     =   mxGetPr(plhs[0]); 
            for(Loop = 0; Loop < int32_t(RetVal/4); Loop++)
            {
                RetData[Loop]   =   (double)ReadData[Loop];
            }
        }
        else
        {
            plhs[0]     =   mxCreateDoubleMatrix(0, 0, mxREAL);
        }   
    }    
}

void    ReadI16FromDev(const int nlhs, mxArray *plhs[], const int nrhs, const mxArray *prhs[])
{
    int32_t   RetVal;
    uint32_t  Data[131072];

    //printf("ReadFromDev: %x\n", nrhs);
    RetVal  =   0;

    if ((nrhs == 2) && (mxIsInt32(prhs[1])))
    {
        int32_t*    Len;

        Len     =   (int32_t*)mxGetData(prhs[1]);
        RetVal  =   (int)UsbRead((int)(*Len), Data);

    }
    if (nlhs == 1)
    {
        double          *RetData;
        int32_t         Loop;

        if (RetVal != 0)
        {
            int16_t     *pData16;

            plhs[0]     =   mxCreateDoubleMatrix(2*RetVal/4, 1, mxREAL);
            RetData     =   mxGetPr(plhs[0]); 
            pData16     =   (int16_t*)Data;
            for(Loop = 0; Loop < int32_t(2*RetVal/4); Loop++)
            {
                RetData[Loop]    =   (double)(*pData16);
                pData16++;
            }
        }
        else
        {
            plhs[0]     =   mxCreateDoubleMatrix(0, 0, mxREAL);
        }    
    }    
}

void    GetData(const int nlhs, mxArray *plhs[], const int nrhs, const mxArray *prhs[])
{
    int32_t     RetVal;
    int32_t     RetValRead;
    int32_t     Loop;
    uint32_t    Data[131072];
    uint32_t    StrtPosn;
    uint32_t    StopPosn;
    uint32_t    ReadData[4096];
    uint32_t    Header;
    uint32_t    RetLen; 
       

    //printf("GetData: %x\n", nrhs);
    RetVal  =   0;

    if ((nrhs == 2) && (mxIsUint32(prhs[1])))
    {
        uint32_t*   WriteData;
        int         Len;

        WriteData   =   (uint32_t*)mxGetData(prhs[1]);
        Len         =   (int)mxGetNumberOfElements(prhs[1]); 
        StrtPosn    =   WriteData[2];
        StopPosn    =   WriteData[3];
        RetVal      =   UsbWriteCmd(Len, WriteData);

        //printf("Strt: %d\n", StrtPosn);
        //printf("Stop: %d\n", StopPosn);
        Len         =   (int)(256*4*2*3*(StopPosn-StrtPosn));

        for(Loop = 0; Loop < 1000; Loop++);

        RetVal      =   (int)UsbRead(Len, Data);
        RetValRead  =   (int)UsbRead(4, ReadData);
        //printf("RetVal: %x\n", RetVal);
        Header      =   ReadData[0];
        RetLen      =   Header >> 16;
        //printf("RetLen: %x\n", RetLen);
        RetValRead  =   (int)UsbRead((int)4*(RetLen - 1), ReadData);

    }
    if (nlhs == 1)
    {
        double          *RetData;
        int32_t         Loop;

        if (RetVal != 0)
        {
            int16_t     *pData16;

            plhs[0]     =   mxCreateDoubleMatrix(2*RetVal/4, 1, mxREAL);
            RetData     =   mxGetPr(plhs[0]); 
            pData16     =   (int16_t*)Data;
            for(Loop = 0; Loop < int32_t(2*RetVal/4); Loop++)
            {
                RetData[Loop]    =   (double)(*pData16);
                pData16++;
            }
        }
        else
        {
            plhs[0]     =   mxCreateDoubleMatrix(0, 0, mxREAL);
        }    
    }    
}

void    GetDatLen(const int nlhs, mxArray *plhs[], const int nrhs, const mxArray *prhs[])
{
    int32_t     RetVal;
    int32_t     RetValRead;
    int32_t     Loop;
    uint32_t    Data[131072];
    uint32_t    ReadData[4096];
    uint32_t    Header;
    uint32_t    RetLen; 
       
    RetVal  =   0;

    if ((nrhs == 2) && (mxIsUint32(prhs[1])))
    {
        uint32_t*   WriteData;
        int         Len;
        int         DatLen;

        WriteData   =   (uint32_t*)mxGetData(prhs[1]);
        Len         =   (int)mxGetNumberOfElements(prhs[1]); 
        DatLen      =   WriteData[3]*2;
        /*
        printf("1: %d\n", WriteData[1]);
        printf("2: %d\n", WriteData[2]);
        printf("3: %d\n", WriteData[3]);
        printf("4: %d\n", WriteData[4]);
        */
        RetVal      =   UsbWriteCmd(Len, WriteData);
        
        //printf("Read Data Length: %d\n", DatLen);
        for(Loop = 0; Loop < 1000; Loop++);

        RetVal      =   (int)UsbRead(DatLen, Data);
        RetValRead  =   (int)UsbRead(4, ReadData);
        //printf("RetVal: %x\n", RetVal);
        Header      =   ReadData[0];
        RetLen      =   Header >> 16;
        //printf("RetLen: %x\n", RetLen);
        RetValRead  =   (int)UsbRead((int)4*(RetLen - 1), ReadData);
        
        //printf("RetValRead: %x\n", RetValRead);
        

    }
    if (nlhs == 1)
    {
        double          *RetData;
        int32_t         Loop;

        if (RetVal != 0)
        {
            int16_t     *pData16;

            plhs[0]     =   mxCreateDoubleMatrix(2*RetVal/4, 1, mxREAL);
            RetData     =   mxGetPr(plhs[0]); 
            pData16     =   (int16_t*)Data;
            for(Loop = 0; Loop < int32_t(2*RetVal/4); Loop++)
            {
                RetData[Loop]    =   (double)(*pData16);
                pData16++;
            }
        }
        else
        {
            plhs[0]     =   mxCreateDoubleMatrix(0, 0, mxREAL);
        }    
    }    
}

void mexFunction(const int nlhs, mxArray *plhs[], const int nrhs, const mxArray *prhs[])
{
    char *Cmd = NULL;

    if (nrhs >= 1)
    {
        if (mxIsChar(prhs[0]))
        {
            Cmd     =   mxArrayToString(prhs[0]);
            if (strcmp("Vers",Cmd) == 0)
            {
                GetVers(nlhs, plhs, nrhs, prhs);
            }
            if (strcmp("Open",Cmd) == 0)
            {
                printf("DemoRad::Open device\n");
                OpenDev(nlhs, plhs, nrhs, prhs);
            }
            if (strcmp("Close", Cmd) == 0)
            {
                printf("DemoRad::Close device\n");
                CloseDev(nlhs, plhs, nrhs, prhs);
            }
            if (strcmp("WriteCmd", Cmd) == 0)
            {
                WriteToDev(nlhs, plhs, nrhs, prhs);
            }
            if (strcmp("Read", Cmd) == 0)
            {
                ReadFromDev(nlhs, plhs, nrhs, prhs);
            }
            if (strcmp("ReadI16", Cmd) == 0)
            {
                ReadI16FromDev(nlhs, plhs, nrhs, prhs);
            }    
            if (strcmp("ExecCmd", Cmd) == 0)
            {
                ExecCmd(nlhs, plhs, nrhs, prhs);   
            }  
            if (strcmp("GetData", Cmd) == 0)
            {
                GetData(nlhs, plhs, nrhs, prhs);     
            }  
            if (strcmp("GetDatLen", Cmd) == 0)
            {
                GetDatLen(nlhs, plhs, nrhs, prhs);     
            }              
        }     
    }
}