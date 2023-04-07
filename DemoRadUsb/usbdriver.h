/*********************************************************************************

Copyright(c) 2005 Analog Devices, Inc. All Rights Reserved.

This software is proprietary and confidential.  By using this software you agree
to the terms of the associated Analog Devices License Agreement.

*********************************************************************************/

#ifndef _USBDRIVER_H_
#define _USBDRIVER_H_

#include "winusb.h"
#include <setupapi.h>

/* Setup Device Request Types 2.0 specification pg 248
 * below macros define the bits of bmRequestType */
#define USB_DIR_HOST_TO_DEVICE (0 << 7) /* 7th bit is 0 */
#define USB_DIR_DEVICE_TO_HOST (1 << 7) /* 7th bit is 1 */

#define USB_TYPE_STANDARD      ((0 << 5) | (0<<6)) /* 0 (5th,6th bit positions) */
#define USB_TYPE_CLASS         ((1 << 5) | (0<<6)) /* 1 (5th,6th bit positions) */
#define USB_TYPE_VENDOR        ((0 << 5) | (1<<6)) /* 2 (5th,6th bit positions) */
#define USB_TYPE_RESERVED      ((1 << 5) | (1<<6)) /* 3 (5th,6th bit positions) */

#define USB_RECIPIENT_DEVICE      (0)              /* bits 0-4)  */
#define USB_RECIPIENT_INTERFACE   (1 << 0)         /* bits 0-4)  */
#define USB_RECIPIENT_ENDPOINT    (1 << 1)         /* bits 0-4)  */
#define USB_RECIPIENT_OTHER       ((1 << 1) | (1<< 0))  /* bits 0-4)  */

/* Request types (bRequest of Setup Packet)  pg 250 & 251 of USB 2.0 specification */

#define USB_STD_RQST_GET_STATUS         0x00
#define USB_STD_RQST_CLEAR_FEATURE      0x01
#define USB_STD_RQST_SET_FEATURE        0x03   /* 0x2 is reserved */
#define USB_STD_RQST_SET_ADDRESS        0x05   /* 0x4 is reserved */
#define USB_STD_RQST_GET_DESCRIPTOR     0x06
#define USB_STD_RQST_SET_DESCRIPTOR     0x07
#define USB_STD_RQST_GET_CONFIGURATION      0x08
#define USB_STD_RQST_SET_CONFIGURATION      0x09
#define USB_STD_RQST_GET_INTERFACE      0x0A
#define USB_STD_RQST_SET_INTERFACE      0x0B
#define USB_STD_RQST_SYNCH_FRAME        0x0C

BOOL SendControlRequest(HANDLE hDeviceHandle, UCHAR bRequestType, UCHAR bRequest, USHORT wValue, USHORT wIndex, USHORT wLength, UCHAR *pData);
BOOL SendSetFeatureEndpointHalt(HANDLE hDeviceHandle, int EpNum);
BOOL SendClearFeatureEndpointHalt(HANDLE hDeviceHandle, int EpNum);


#define MAX_IO_WAIT					10000		// timeout for USB transfers in msecs
#define MAX_COM_PORTS				4 /* Max num of supported Virtual Com ports (configurable according to requirements) */
// pipe types
enum _PIPE_TYPE
{
	READ_PIPE,
	WRITE_PIPE,
	READ_WRITE_PIPE // For WinUsb device
};
enum _USBDEVICE_TYPE
{
	BULKADI_DEVICE,
	WINUSB_DEVICE,
	USBSER_DEVICE
};

extern char ComStringbuffer[MAX_COM_PORTS][80];
extern _USBDEVICE_TYPE usbDeviceType;
/*
// need a rough USB_DEVICE_DESCRIPTOR structure for opening a USB device
typedef struct UsbDevDesc
{
	char usbdevdesc[18];
}USB_DEVICE_DESCRIPTOR, *PUSB_DEVICE_DESCRIPTOR;
*/

// prototypes
HANDLE OpenOneDevice( HDEVINFO, PSP_INTERFACE_DEVICE_DATA, WCHAR * );
HANDLE OpenUsbDevice( LPGUID, WCHAR);
BOOL GetUsbDeviceFileName( LPGUID, WCHAR);
DWORD QueryNumDevices( LPGUID pGuid );
HANDLE OpenDeviceHandle( LPGUID pGuid, _PIPE_TYPE nPipeType, DWORD dwDeviceNumber, BOOL bUseAsyncIo);
BOOL ReadPipe(HANDLE hRead, LPVOID lpBuffer, DWORD nNumberOfBytesToRead, LPDWORD lpNumberOfBytesRead);
BOOL WritePipe(HANDLE hWrite, LPCVOID lpBuffer, DWORD nNumberOfBytesToWrite, LPDWORD lpNumberOfBytesWritten);

typedef struct WINUSB_DEV_INFO {
    WINUSB_INTERFACE_HANDLE winUSBHandle;
    UCHAR   speed;
    UCHAR   bulkInPipe;
    UCHAR   bulkOutPipe;
    USHORT  interruptPipe;
}WINUSB_DEV_INFO;

typedef struct _EMGUSBCB
{
	unsigned short u16_NumberofBytesInPayload;
	unsigned char  Payload[2048 - 2];
} EMGUSBCB;

enum _ERROR_VALUES			/* error values */
{
	OPERATION_PASSED = 0,
	UNSUPPORTED_COMMAND,
	IO_WRITE_USBCB_FAILED,
	IO_READ_USBCB_FAILED,
	IO_READ_DATA_FAILED,
	IO_WRITE_DATA_FAILED,
	OUT_OF_MEMORY_ON_HOST,
	ERROR_OPENING_FILE,
	ERROR_READING_FILE,
	NO_AVAILABLE_FILE_PTRS,
	COULD_NOT_CONNECT,
};

#endif // _USBDRIVER_H_