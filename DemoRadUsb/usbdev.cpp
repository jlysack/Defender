// usb.cpp : Definiert die exportierten Funktionen für die DLL-Anwendung.
//

#include "stdafx.h"

#include <stdlib.h>
#include <stdio.h>
#include <string>

#include "usbdev.h"
#include "usbdriver.h"
#include "Windows.h"
#include "winusb.h"


// guid for this device
EXTERN_C const GUID GUID_CLASS_BF_USB_BULKADI;
EXTERN_C const GUID GUID_CLASS_BF_USB_WINUSB;

/////////////////////////////////////////////////////
// globals
/////////////////////////////////////////////////////
DWORD 	g_dwTotalDevices				= 0;						// total Blackfin device connected
DWORD 	g_dwTotalDevices_WinUsb			= 0;						// total Blackfin WINUSB devices detected
UINT 	g_unDeviceNumber				= 0;						// device number selected
char 	g_pszDeviceDesc[256];										// device name string for display only
extern 	HANDLE 	g_hRead;											// USB device read handle
extern 	HANDLE 	g_hWrite;											// USB device write handle
extern 	HANDLE 	g_hReadEvent;
extern 	HANDLE 	g_hWriteEvent;
extern 	int 	DebugNrDev;
extern 	int 	DebugOpen;
extern 	int 	DebugLstErr;

extern 	HANDLE  hDevGlob;

_USBDEVICE_TYPE usbDeviceType;

int GetVersMajor(void)
{
	return VERS_MAJOR;
}

int GetVersMinor(void)
{
	return VERS_MINOR;
}

int GetVersFix(void)
{
	return VERS_FIX;
}

// Initialzied and Displays connected usb devices with WINUSB
bool FindConnectedDevices(void)
{
	usbDeviceType				= WINUSB_DEVICE;
	g_dwTotalDevices_WinUsb		= QueryNumDevices((LPGUID)&GUID_CLASS_BF_USB_WINUSB);
	g_dwTotalDevices			= g_dwTotalDevices_WinUsb;
	DebugNrDev 					= (int)g_dwTotalDevices_WinUsb;
	// One or more devices found
	if (g_dwTotalDevices >= 1)
	{
		return true;
	}
	else // no device found
	{
		return false;
	}
}

// Copies the handle and connects to device by opening it
// SYNC/ASYNC defines, used to determine which method of I/O you want to use
//  USE_SYNC	false
//  USE_ASYNC	true
bool ConnectToDevice(bool bUseAsyncIo)
{
	DWORD 		LstErr;

	// if no devices found print message and return
	if (!FindConnectedDevices())
	{
		//cout << endl << "No " << endl << g_pszDeviceDesc << "devices were found" << endl;
		DebugOpen 	= 	-1;
		return false;
	}

	// make sure it's a valid device number
	if (g_unDeviceNumber >= g_dwTotalDevices)
	{
		//cerr << "Invalid device number " << g_unDeviceNumber << endl;
		DebugOpen 	= 	-2;
		return false;

	}

	if (WINUSB_DEVICE == usbDeviceType)
	{
		// open write handle
		g_hWrite 	= OpenDeviceHandle((LPGUID)&GUID_CLASS_BF_USB_WINUSB, READ_WRITE_PIPE, g_unDeviceNumber, bUseAsyncIo);
		if (g_hWrite == INVALID_HANDLE_VALUE)
		{
			DebugOpen 	= 	-3;
			//cerr << "Error opening driver" << endl;
			return false;
		}

		// WINUSB device: Copy same handle to read handle
		g_hRead = g_hWrite;
	}
	else
	{
		DebugOpen 	= 	-4;
	}
	LstErr 			= 	GetLastError();
	DebugLstErr  	= 	(int)LstErr;	
	return true;
}

// Closes the handles
int32_t CloseGlobalHandles(void)
{
	int 				Sts;
	int32_t 			RetVal;
	DWORD 				LstErr;
	WINUSB_DEV_INFO		*pDev;

	RetVal 		= 	0;

	if (g_hRead && (g_hRead != INVALID_HANDLE_VALUE))
	{
		pDev 	= 	(WINUSB_DEV_INFO*)g_hWrite;
		Sts 	= 	WinUsb_Free(pDev->winUSBHandle);
		/* Global handle needs to be closed: Handle is stored as global variable */
		CloseHandle(hDevGlob);		
		if (Sts == 0)
		{
			RetVal 	+= 4;
		}
	}

	LstErr 			= 	GetLastError();
	DebugLstErr  	= 	(int)LstErr;
	return RetVal;
}

bool UsbWriteCmd(int len, uint32_t cmd[])
{
	if (g_hWrite != INVALID_HANDLE_VALUE)
	{
		uint16_t 	Loop;
		uint16_t 	PayLoadIndex;
		char		*pcOutBuff		= NULL;			// output buffer
		EMGUSBCB	*pusbcb			= NULL;				// USB command block pointer
		ULONG		nActualBytes;				// actual bytes transferred
		int			nRetVal			= OPERATION_PASSED;
		BOOL		IoStatus		= TRUE;			// IO status
		pcOutBuff					= new char[sizeof(EMGUSBCB)];
		pusbcb						= (EMGUSBCB*)pcOutBuff;

		PayLoadIndex = 0;

		for (Loop = 0; Loop < len; Loop++)
		{
			pusbcb->Payload[PayLoadIndex + 3]	= (cmd[Loop] >> 24) & 0xFF;
			pusbcb->Payload[PayLoadIndex + 2]	= (cmd[Loop] >> 16) & 0xFF;
			pusbcb->Payload[PayLoadIndex + 1]	= (cmd[Loop] >> 8) & 0xFF;
			pusbcb->Payload[PayLoadIndex]		= cmd[Loop] & 0xFF;

			PayLoadIndex += 4;
		}
		pusbcb->u16_NumberofBytesInPayload = PayLoadIndex;

		IoStatus = WritePipe(g_hWrite, pusbcb, sizeof(EMGUSBCB), &nActualBytes);

		// check for error
		if (!IoStatus)
		{
			//cerr << "Error writing usbcb" << endl;
			nRetVal = IO_WRITE_USBCB_FAILED;
			return false;
		}
		if (pcOutBuff)
		{
			delete[] pcOutBuff;
		}
		return true;
	}
	else
	{
		return false;
	}
}

int UsbRead(int len, uint32_t cmd[])
{
	ULONG nCountCurrent = 0;

	if (g_hRead != INVALID_HANDLE_VALUE)
	{
		ReadPipe(g_hRead, cmd, sizeof(char) * len, &nCountCurrent);
	}

	return nCountCurrent;
}

