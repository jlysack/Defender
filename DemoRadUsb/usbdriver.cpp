/*********************************************************************************

Copyright(c) 2005 Analog Devices, Inc. All Rights Reserved.

This software is proprietary and confidential.  By using this software you agree
to the terms of the associated Analog Devices License Agreement.

*********************************************************************************/
#include "stdafx.h"

#include <windows.h>
#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include "adiguid.h"
#include "usbdriver.h"



// choose whether to display (1) or supress (0) printf debug information in this file
#if 0
	#define NOISY(_x_) printf _x_ ;
#else
	#define NOISY(_x_) ;
#endif

extern 	HANDLE  hDevGlob;


BOOL g_bUseAsyncIo = TRUE;							// flag indicating if we're using ASYNC (TRUE) or SYNC (FALSE) IO
HANDLE g_hReadEvent = INVALID_HANDLE_VALUE;			// read event handle for ASYNC IO
HANDLE g_hWriteEvent = INVALID_HANDLE_VALUE;		// write event handle for ASYNC IO
OVERLAPPED g_ReadOverlapped;						// for asynchronous IO reads for ASYNC IO
OVERLAPPED g_WriteOverlapped;						// for asynchronous IO writes for ASYNC IO
char ComStringbuffer[MAX_COM_PORTS][80];        	// String buffer to hold the allocated COM ports name
WINUSB_DEV_INFO devInfo;
WINUSB_PIPE_INFORMATION pipeInfo;

static int ConfigureComPort( char *pcComName, HANDLE *phCOMPort);
static void SetBaud (HANDLE hComPort, DWORD baud);
BOOL Initialize_WinUsbDevice(HANDLE g_hWrite, WINUSB_DEV_INFO *winUsbDeviceInfo);
/******************************************************************************
Routine Description:

    Given the HardwareDeviceInfo, representing a handle to the plug and
    play information, and deviceInfoData, representing a specific usb device,
    open that device and fill in all the relevant information in the given
    USB_DEVICE_DESCRIPTOR structure.

Arguments:

    HardwareDeviceInfo:  handle to info obtained from Pnp mgr via SetupDiGetClassDevs()
    DeviceInfoData:      ptr to info obtained via SetupDiEnumInterfaceDevice()

Return Value:

    return HANDLE if the open and initialization was successfull,
	else INVLAID_HANDLE_VALUE.

******************************************************************************/
HANDLE OpenOneDevice (
    IN       HDEVINFO                    HardwareDeviceInfo,
    IN       PSP_INTERFACE_DEVICE_DATA   DeviceInfoData,
	IN		 WCHAR * devName
    )
{
    PSP_INTERFACE_DEVICE_DETAIL_DATA     functionClassDeviceData = NULL;
    ULONG                                predictedLength = 0;
    ULONG                                requiredLength = 0;
	HANDLE								 hOut = INVALID_HANDLE_VALUE;

    //
    // allocate a function class device data structure to receive the
    // goods about this particular device.
    //
    SetupDiGetInterfaceDeviceDetail (
            HardwareDeviceInfo,
            DeviceInfoData,
            NULL,			// probing so no output buffer yet
            0,				// probing so output buffer length of zero
            &requiredLength,
            NULL);			// not interested in the specific dev-node


    predictedLength = requiredLength;

    functionClassDeviceData = (PSP_INTERFACE_DEVICE_DETAIL_DATA )malloc (predictedLength);
	if(NULL == functionClassDeviceData) {
        return INVALID_HANDLE_VALUE;
    }
    functionClassDeviceData->cbSize = sizeof (SP_INTERFACE_DEVICE_DETAIL_DATA);

    //
    // Retrieve the information from Plug and Play.
    //
    if (! SetupDiGetInterfaceDeviceDetail (
               HardwareDeviceInfo,
               DeviceInfoData,
               functionClassDeviceData,
               predictedLength,
               &requiredLength,
               NULL)) {
		free( functionClassDeviceData );
        return INVALID_HANDLE_VALUE;
    }

	wcscpy_s(devName, sizeof(devName), (const WCHAR *)functionClassDeviceData->DevicePath) ;
	NOISY(( "Attempting to open %s\n", devName ));

    hOut = CreateFile (
                  functionClassDeviceData->DevicePath,
                  GENERIC_READ | GENERIC_WRITE,
                  FILE_SHARE_READ | FILE_SHARE_WRITE,
                  NULL,				// no SECURITY_ATTRIBUTES structure
                  OPEN_EXISTING,	// No special create flags
                  0,				// No special attributes
                  NULL);			// No template file

    if (INVALID_HANDLE_VALUE == hOut) {
		printf( "FAILED to open %ls\n", devName );
    }
	free( functionClassDeviceData );
	return hOut;
}


/******************************************************************************
Routine Description:

   Do the required PnP things in order to find
   the next available proper device in the system at this time.

Arguments:

    pGuid:      ptr to GUID registered by the driver itself
    outNameBuf: the generated name for this device

Return Value:

    return HANDLE if the open and initialization was successful,
	else INVLAID_HANDLE_VALUE.
******************************************************************************/

/******************************************************************************
Routine Description:

    Returns the number of devices attached to the system based on supplied GUID.

Arguments:

	pClassGuid:	ptr to GUID registered by the driver itself

Return Value:

    Number of devices attached to system

******************************************************************************/
DWORD QueryNumDevices( LPGUID pGuid )
{
	DWORD nDevices = 0;

	HDEVINFO hdInfo = SetupDiGetClassDevs( pGuid, NULL, NULL,
										 DIGCF_PRESENT | DIGCF_DEVICEINTERFACE );

	if( hdInfo == INVALID_HANDLE_VALUE )
	{
		return( -1 );
	}

	for( nDevices=0; ; nDevices++ )
	{
		SP_INTERFACE_DEVICE_DATA ifData;
		ifData.cbSize = sizeof(ifData);

		if( !SetupDiEnumInterfaceDevice( hdInfo, NULL, pGuid, nDevices, &ifData ) )
		{
			if( GetLastError() == ERROR_NO_MORE_ITEMS ){
				//printf("ERROR_NO_MORE_ITEMS\n");
				break;
			}
			else
			{
				SetupDiDestroyDeviceInfoList( hdInfo );
				return( -1 );
			}
		}
		else
		{

			DWORD dwNameLength = 0;

			// find out how many bytes to malloc for the DeviceName.
			SetupDiGetInterfaceDeviceDetail( hdInfo, &ifData, NULL, 0, &dwNameLength, NULL );

			// we need to account for the pipe name so add to the length here
			dwNameLength += 32;

			PSP_INTERFACE_DEVICE_DETAIL_DATA detail = (PSP_INTERFACE_DEVICE_DETAIL_DATA)malloc( dwNameLength );

			if( !detail )
			{
				NOISY(("Failed to OpenDeviceHandle\n", GetLastError()));
				SetupDiDestroyDeviceInfoList( hdInfo );
				return( -1 );
			}

			detail->cbSize = sizeof( SP_INTERFACE_DEVICE_DETAIL_DATA );

			// get the DeviceName
			if( !SetupDiGetInterfaceDeviceDetail( hdInfo, &ifData, detail, dwNameLength, NULL, NULL ) )
			{
				NOISY(("Failed to OpenDeviceHandle\n", GetLastError()));
				free( (PVOID)detail );
				SetupDiDestroyDeviceInfoList( hdInfo );
				return( -1 );
			}

			WCHAR szDeviceName[MAX_PATH];
			wcsncpy_s( szDeviceName, (const WCHAR *)detail->DevicePath, sizeof(szDeviceName) );
				
			//printf("szDeviceName - %s\n", szDeviceName);
			free( (PVOID) detail );
		}
	}
	
	SetupDiDestroyDeviceInfoList( hdInfo );

	return( nDevices );
}


/******************************************************************************
Routine Description:

    Opens a pipe handle based on the GUID and device number.

Arguments:

	pGuid:			points to the GUID that identifies the interface class
    nPipeType:		indicates which pipe we want to open
	dwDeviceNumber:	specifies which instance of the enumerated devices to open
	bUseAsyncIo:	specifies if we should use ASYNC (TRUE) or SYNC (FALSE) IO

Return Value:

    Device handle on success else NULL

******************************************************************************/
HANDLE OpenDeviceHandle( LPGUID pGuid, _PIPE_TYPE nPipeType, DWORD dwDeviceNumber, BOOL bUseAsyncIo)
{
	DWORD dwError = ERROR_SUCCESS;
	HANDLE hDev = INVALID_HANDLE_VALUE;
	g_bUseAsyncIo = bUseAsyncIo;
	WCHAR szDeviceName[MAX_PATH];
	DWORD dwAttribs;

	/* Error check for GUID input s*/
	if( (pGuid != (LPGUID)&GUID_CLASS_BF_USB_WINUSB) )
	{
		NOISY(("Invalid GUID\n"));
		return INVALID_HANDLE_VALUE;
	}

	if( (pGuid == (LPGUID)&GUID_CLASS_BF_USB_WINUSB) )
	{
		// see if there are of these attached to the system
		HDEVINFO hdInfo = SetupDiGetClassDevs( pGuid, NULL, NULL,
											   DIGCF_PRESENT | DIGCF_DEVICEINTERFACE );

		if( hdInfo == INVALID_HANDLE_VALUE )
		{
			NOISY(("Failed to OpenDeviceHandle\n", GetLastError()));
			return INVALID_HANDLE_VALUE;
		}

		SP_INTERFACE_DEVICE_DATA ifData;
		ifData.cbSize = sizeof(ifData);

		// see if the device with the corresponding DeviceNumber is present
		if( !SetupDiEnumInterfaceDevice( hdInfo, NULL, pGuid, dwDeviceNumber, &ifData ) )
		{
			NOISY(("Failed to OpenDeviceHandle\n", GetLastError()));
			SetupDiDestroyDeviceInfoList( hdInfo );
			return INVALID_HANDLE_VALUE;
		}

		DWORD dwNameLength = 0;

		// find out how many bytes to malloc for the DeviceName.
		SetupDiGetInterfaceDeviceDetail( hdInfo, &ifData, NULL, 0, &dwNameLength, NULL );

		// we need to account for the pipe name so add to the length here
		dwNameLength += 32;

		PSP_INTERFACE_DEVICE_DETAIL_DATA detail = (PSP_INTERFACE_DEVICE_DETAIL_DATA)malloc( dwNameLength );

		if( !detail )
		{
			NOISY(("Failed to OpenDeviceHandle\n", GetLastError()));
			SetupDiDestroyDeviceInfoList( hdInfo );
			return INVALID_HANDLE_VALUE;
		}

		detail->cbSize = sizeof( SP_INTERFACE_DEVICE_DETAIL_DATA );

		// get the DeviceName
		if( !SetupDiGetInterfaceDeviceDetail( hdInfo, &ifData, detail, dwNameLength, NULL, NULL ) )
		{
			NOISY(("Failed to OpenDeviceHandle\n", GetLastError()));
			free( (PVOID)detail );
			SetupDiDestroyDeviceInfoList( hdInfo );
			return INVALID_HANDLE_VALUE;
		}

		
		wcsncpy_s( szDeviceName, (const WCHAR *)detail->DevicePath, sizeof(szDeviceName) );
		free( (PVOID) detail );
		SetupDiDestroyDeviceInfoList( hdInfo );
	}

	// WinUsb/USBSER: Both Read and Write events
	if (READ_WRITE_PIPE == nPipeType)
	{
		if ( bUseAsyncIo )
		{
			g_hReadEvent = CreateEvent(	NULL,    // no security attribute
										FALSE,    // manual-reset event
										FALSE,    // initial state = signaled
										NULL);   // unnamed event object

			g_ReadOverlapped.hEvent = g_hReadEvent;

			g_hWriteEvent = CreateEvent(NULL,    // no security attribute
										FALSE,    // manual-reset event
										FALSE,    // initial state = signaled
										NULL);   // unnamed event object

			g_WriteOverlapped.hEvent = g_hWriteEvent;
		}
	}
	// else unsupported pipe
	else
	{
		NOISY(("Unsupported pipe\n"));
		return INVALID_HANDLE_VALUE;
	}

	// determine the attributes
	if(pGuid == (LPGUID)&GUID_CLASS_BF_USB_WINUSB)
	{
		// NOTE: For WinUsb implementation bUseAsyncIo is not used. Need to be implemented.
		dwAttribs = FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OVERLAPPED;
	}

	if( (pGuid == (LPGUID)&GUID_CLASS_BF_USB_WINUSB)  )
	{
		// open the driver with this DeviceName
		hDev = CreateFile(	(LPCSTR)szDeviceName,
							GENERIC_READ | GENERIC_WRITE,
							FILE_SHARE_READ | FILE_SHARE_WRITE,
							NULL,
							OPEN_EXISTING,
							dwAttribs,
							NULL);
	}

	if (hDev == INVALID_HANDLE_VALUE)
	{
		NOISY(("Failed to open device\n"));
	}

	/* Initialize the WinUsb device */
	if(pGuid == (LPGUID)&GUID_CLASS_BF_USB_WINUSB)
	{
		if ( !Initialize_WinUsbDevice(hDev,&devInfo) )
		{
			NOISY(("Initialize_WinUsbDevice Failed\n"));
			return INVALID_HANDLE_VALUE;
		}
		hDevGlob 	= 	hDev;
		hDev 		= 	(HANDLE)&devInfo;
		
	}

	// return handle
	return hDev;
}

/******************************************************************************
Routine Description:

    Reads data from the pipe

Arguments:

	hRead:					handle to read pipe
    lpBuffer:				pointer to buffer for data
	nNumberOfBytesToRead:	number of bytes we want to read
	lpNumberOfBytesRead:	number of bytes we read

Return Value:

    Status of operation

******************************************************************************/
BOOL ReadPipe(HANDLE hRead, LPVOID lpBuffer, DWORD nNumberOfBytesToRead, LPDWORD lpNumberOfBytesRead)
{
	BOOL status = TRUE;
	WINUSB_DEV_INFO *winUsbdevInfo;

	//g_bUseAsyncIo = FALSE;
	// if ASYNC
	if (g_bUseAsyncIo)
	{
		if(WINUSB_DEVICE == usbDeviceType)
		{

			winUsbdevInfo = (WINUSB_DEV_INFO *)hRead;
			WinUsb_ReadPipe(winUsbdevInfo->winUSBHandle,
							 winUsbdevInfo->bulkInPipe,
							 (PUCHAR)lpBuffer,
							 nNumberOfBytesToRead,
							 lpNumberOfBytesRead,
							 &g_ReadOverlapped);
		} 
		else
		{
			NOISY(("winUsbdevInfo not initialized\n"));
			return FALSE;
		}

		if(GetLastError() != ERROR_IO_PENDING)
		{
			if(GetLastError() == ERROR_SUCCESS) /* In case of Virtual COM device, this condition will get TRUE */
			{
				// make sure we read all the data we wanted to
				if ((*lpNumberOfBytesRead > 0) && (*lpNumberOfBytesRead != nNumberOfBytesToRead))
				{
					NOISY(( "DATA not received fully\n"));
					return FALSE;
				}
				else
				{
					return TRUE;
				}
			}
			else
			{
				NOISY(( "ReadPipe failed\n" ));
				status = FALSE;
			}
		}
		// wait for the event
		else if (WaitForSingleObject(g_hReadEvent, MAX_IO_WAIT) != WAIT_OBJECT_0)
		{
			NOISY(( "WaitForSingleObject failed\n" ));
			status = FALSE;
		}

		if(WINUSB_DEVICE == usbDeviceType)
		{
			// get the result of the operation
			if(!GetOverlappedResult(winUsbdevInfo->winUSBHandle, &g_ReadOverlapped, lpNumberOfBytesRead, FALSE))
			{
				NOISY(( "GetOverlappedResult failed\n" ));
				status = FALSE;
			}
		}
		else if (!GetOverlappedResult(hRead, &g_ReadOverlapped, lpNumberOfBytesRead, FALSE))
		{
			status = FALSE;
		}

		// if we failed, cancel all I/O for this handle in this thread
		if (!status)
			CancelIo(hRead);

		// make sure we read all the data we wanted to
		if ((*lpNumberOfBytesRead > 0) && (*lpNumberOfBytesRead != nNumberOfBytesToRead))
			status = FALSE;
	}

	// else SYNC
	else
	{
		ULONG ulCountRecv = 0;			// received byte count
		if ( WINUSB_DEVICE == usbDeviceType)
		{
			winUsbdevInfo = (WINUSB_DEV_INFO *)hRead;
			do	/* In case of SYNC, it may happen that required number of bytes transfer may not happen,
				   hence loop is used */
			{
				status = WinUsb_ReadPipe(winUsbdevInfo->winUSBHandle,
										 winUsbdevInfo->bulkInPipe,
										 (PUCHAR)lpBuffer+ulCountRecv,
										 nNumberOfBytesToRead,
										 lpNumberOfBytesRead,
										 NULL);
				if (!status)
				{
					break;
				}
				ulCountRecv += *lpNumberOfBytesRead;
			} while ( ulCountRecv < nNumberOfBytesToRead);

		}
	}

	return status;
}


/******************************************************************************
Routine Description:

    Writes data to the pipe

Arguments:

	hWrite:					handle to write pipe
    lpBuffer:				pointer to buffer for data
	nNumberOfBytesToWrite:	number of bytes we want to write
	lpNumberOfBytesWritten:	number of bytes we wrote

Return Value:

    Status of operation

******************************************************************************/
BOOL WritePipe(HANDLE hWrite, LPCVOID lpBuffer, DWORD nNumberOfBytesToWrite, LPDWORD lpNumberOfBytesWritten)
{
	BOOL status = TRUE;
	WINUSB_DEV_INFO *winUsbdevInfo;

	//g_bUseAsyncIo = FALSE;
	// if ASYNC
	if (g_bUseAsyncIo)
	{
		if(WINUSB_DEVICE == usbDeviceType)
		{

			winUsbdevInfo = (WINUSB_DEV_INFO *)hWrite;
			WinUsb_WritePipe(winUsbdevInfo->winUSBHandle,
							 winUsbdevInfo->bulkOutPipe,
							 (PUCHAR)lpBuffer,
							 nNumberOfBytesToWrite,
							 lpNumberOfBytesWritten,
							 &g_WriteOverlapped);
		}
		else
		{
			NOISY(("winUsbdevInfo not initialized\n"));
			return FALSE;
		}

        if(GetLastError() != ERROR_IO_PENDING)
		{
			if(GetLastError() == ERROR_SUCCESS) /* In case of Virtual COM device, this condition will get TRUE */
			{	
				// make sure we wrote all the data we wanted to
				if (*lpNumberOfBytesWritten != nNumberOfBytesToWrite)
				{
					NOISY(( "DATA not sent fully\n"));
					return FALSE;
				}
				else
				{
					return TRUE;
				}
			}
			else
			{
				NOISY(( "GetLastError: %d\n", GetLastError()));
				NOISY(( "WritePipe failed\n" ));
				status = FALSE;
			}
		}
		// wait for the event
		else if (WaitForSingleObject(g_hWriteEvent, MAX_IO_WAIT) != WAIT_OBJECT_0)
		{
			NOISY(( "WaitForSingleObject failed\n" ));
			status = FALSE;
		}

		if(WINUSB_DEVICE == usbDeviceType)
		{
			// get the result of the operation
			if(!GetOverlappedResult(winUsbdevInfo->winUSBHandle, &g_WriteOverlapped, lpNumberOfBytesWritten, FALSE))
			{
				NOISY(( "GetOverlappedResult failed\n" ));
				status = FALSE;
			}
		}
		else if (!GetOverlappedResult(hWrite, &g_WriteOverlapped, lpNumberOfBytesWritten, FALSE))
		{
			status = FALSE;	
		}

		// if we failed, cancel all I/O for this handle in this thread
		if (!status)
			CancelIo(hWrite);

		// make sure we wrote all the data we wanted to
		if (*lpNumberOfBytesWritten != nNumberOfBytesToWrite)
			status = FALSE;
	}

	// else SYNC
	else
	{

		ULONG ulCountSent = 0;							// received byte count

		// write file
		if ( WINUSB_DEVICE == usbDeviceType)
		{
			winUsbdevInfo = (WINUSB_DEV_INFO *)hWrite;
			do  /* In case of SYNC, it may happen that required number of bytes transfer may not happen,
				   hence loop is used */
			{
				status = WinUsb_WritePipe(winUsbdevInfo->winUSBHandle,
										 winUsbdevInfo->bulkOutPipe,
										 (PUCHAR)lpBuffer + ulCountSent,
										 nNumberOfBytesToWrite,
										 lpNumberOfBytesWritten,
										 NULL);
				if (!status)
				{
					break;
				}
				ulCountSent += *lpNumberOfBytesWritten;
			} while ( ulCountSent < nNumberOfBytesToWrite);

		}
	}

	return status;
}



BOOL Initialize_WinUsbDevice(HANDLE g_hWrite, WINUSB_DEV_INFO *winUsbDeviceInfo)
{
	BOOL bResult;
	WINUSB_INTERFACE_HANDLE usbHandle;
	USB_INTERFACE_DESCRIPTOR ifaceDescriptor;
	UCHAR speed;
	ULONG length;

	bResult = WinUsb_Initialize(g_hWrite, &usbHandle);

	if(bResult)
	{
	winUsbDeviceInfo->winUSBHandle = usbHandle;
	length = sizeof(UCHAR);
	bResult = WinUsb_QueryDeviceInformation(winUsbDeviceInfo->winUSBHandle,
											DEVICE_SPEED,
											&length,
											&speed);
	}

	if(bResult)
	{
	winUsbDeviceInfo->speed = speed;
	bResult = WinUsb_QueryInterfaceSettings(winUsbDeviceInfo->winUSBHandle,
											0,
											&ifaceDescriptor);
	}

	if(bResult)
	{
	for(int i=0;i<ifaceDescriptor.bNumEndpoints;i++)
	{

		bResult = WinUsb_QueryPipe(winUsbDeviceInfo->winUSBHandle,
								 0,
								 (UCHAR) i,
								 &pipeInfo);


		if(pipeInfo.PipeType == UsbdPipeTypeBulk &&
					  USB_ENDPOINT_DIRECTION_IN(pipeInfo.PipeId))
		  {
			winUsbDeviceInfo->bulkInPipe = pipeInfo.PipeId;
		  }
		  else if(pipeInfo.PipeType == UsbdPipeTypeBulk &&
					  USB_ENDPOINT_DIRECTION_OUT(pipeInfo.PipeId))
		  {
			winUsbDeviceInfo->bulkOutPipe = pipeInfo.PipeId;
		  }
		  else if(pipeInfo.PipeType == UsbdPipeTypeInterrupt)
		  {
			winUsbDeviceInfo->interruptPipe = pipeInfo.PipeId;
		  }
		  else
		  {
			bResult = FALSE;
			break;
		  }
	   }
    }
	ULONG timeout = 500000; // ms
	WinUsb_SetPipePolicy(winUsbDeviceInfo->winUSBHandle, winUsbDeviceInfo->bulkInPipe, PIPE_TRANSFER_TIMEOUT, sizeof(ULONG), &timeout);
	WinUsb_SetPipePolicy(winUsbDeviceInfo->winUSBHandle, winUsbDeviceInfo->bulkOutPipe, PIPE_TRANSFER_TIMEOUT, sizeof(ULONG), &timeout);
#if 0
    static UCHAR bZLP = true;
    bResult = WinUsb_SetPipePolicy(
                            winUsbDeviceInfo->winUSBHandle,
                            winUsbDeviceInfo->bulkOutPipe,
                            SHORT_PACKET_TERMINATE,
                            sizeof(UCHAR*),
                            &bZLP
                        );
#endif
	return bResult;
}
