
disp('Compile 64-Bit mex version')

mex     DemoRadUsb.cpp usbdev.cpp usbdriver.cpp  ...
        WinDDK/lib/win7/amd64/winusb.lib WinDDK/lib/win7/amd64/setupapi.lib  ...
        -IWinDDK/inc/ddk -I. -IWinDDK/inc/api