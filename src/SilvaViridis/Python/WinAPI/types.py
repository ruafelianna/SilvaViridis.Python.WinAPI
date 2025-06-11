import ctypes as C
import ctypes.wintypes as W

# usbuser.h

class USBUSER_REQUEST_HEADER(C.Structure):
    _fields_ = [
        ("UsbUserRequest", W.ULONG),
        ("UsbUserStatusCode", C.c_int),
        ("RequestBufferLength", W.ULONG),
        ("ActualBufferLength", W.ULONG),
    ]

class USB_CONTROLLER_INFO_0(C.Structure):
    _fields_ = [
        ("PciVendorId", W.ULONG),
        ("PciDeviceId", W.ULONG),
        ("PciRevision", W.ULONG),
        ("NumberOfRootPorts", W.ULONG),
        ("ControllerFlavor", C.c_int),
        ("HcFeatureFlags", W.ULONG),
    ]

class USBUSER_CONTROLLER_INFO_0(C.Structure):
    _fields_ = [
        ("Header", USBUSER_REQUEST_HEADER),
        ("Info0", USB_CONTROLLER_INFO_0),
    ]
