#ifndef USBDEV_H
#define USBDEV_H


#define VERS_MAJOR		0
#define VERS_MINOR		1
#define VERS_FIX		0


typedef unsigned int       	uint32_t;
typedef unsigned long int   uint64_t;
typedef signed int         	int32_t;
typedef unsigned short      uint16_t;
typedef signed short       	int16_t;
typedef unsigned char       uint8_t;
typedef signed char         int8_t;


int 	GetVersMajor(void);
int		GetVersMinor(void);
int 	GetVersFix(void);
bool 	ConnectToDevice(bool bUseAsyncIo);
int32_t CloseGlobalHandles(void);

int 	UsbRead(int len, uint32_t cmd[]);

bool 	UsbWriteCmd(int len, uint32_t cmd[]);


#endif