from __future__ import annotations

import ctypes as C
import ctypes.wintypes as W

# guiddef.h

class GUID(C.Structure):
    _fields_ = [
        ("Data1", C.c_ulong),
        ("Data2", C.c_ushort),
        ("Data3", C.c_ushort),
        ("Data4", C.c_ubyte * 8),
    ]

    def __str__(self):
        return f"{self.Data1:08x}-{self.Data2:04x}-{self.Data3:04x}-{"".join([f"{b:02x}" for b in self.Data4])}"

LPGUID = C.POINTER(GUID)

# minwinbase.h

class OVERLAPPED_DUMMYSTRUCT(C.Structure):
    _fields_ = [
        ("Offset", W.DWORD),
        ("OffsetHigh", W.DWORD),
    ]

class OVERLAPPED_DUMMYUNION(C.Union):
    _fields_ = [
        ("DUMMYSTRUCTNAME", OVERLAPPED_DUMMYSTRUCT),
        ("Pointer", C.c_void_p),
    ]

class OVERLAPPED(C.Structure):
    _fields_ = [
        ("Internal", C.c_void_p),
        ("InternalHigh", C.c_void_p),
        ("DUMMYUNIONNAME", OVERLAPPED_DUMMYUNION),
        ("hEvent", W.HANDLE),
    ]

LPOVERLAPPED = C.POINTER(OVERLAPPED)

# setupapi.h

HDEVINFO = C.c_void_p

class SP_DEVINFO_DATA(C.Structure):
    _fields_ = [
        ("cbSize", W.DWORD),
        ("ClassGuid", GUID),
        ("DevInst", W.DWORD),
        ("Reserved", C.c_void_p),
    ]

    @staticmethod
    def create() -> SP_DEVINFO_DATA:
        data = SP_DEVINFO_DATA()
        data.cbSize = C.sizeof(SP_DEVINFO_DATA)
        return data

PSP_DEVINFO_DATA = C.POINTER(SP_DEVINFO_DATA)

class SP_DEVICE_INTERFACE_DATA(C.Structure):
    _fields_ = [
        ("cbSize", W.DWORD),
        ("InterfaceClassGuid", GUID),
        ("Flags", W.DWORD),
        ("Reserved", C.c_void_p),
    ]

    @staticmethod
    def create() -> SP_DEVICE_INTERFACE_DATA:
        data = SP_DEVICE_INTERFACE_DATA()
        data.cbSize = C.sizeof(SP_DEVICE_INTERFACE_DATA)
        return data

PSP_DEVICE_INTERFACE_DATA = C.POINTER(SP_DEVICE_INTERFACE_DATA)

class SP_DEVICE_INTERFACE_DETAIL_DATA(C.Structure):
    _fields_ = [
        ("cbSize", W.DWORD),
        ("DevicePath", W.WCHAR * 1),
    ]

PSP_DEVICE_INTERFACE_DETAIL_DATA = C.POINTER(SP_DEVICE_INTERFACE_DETAIL_DATA)

# usbioctl.h

class USB_HCD_DRIVERKEY_NAME(C.Structure):
    _fields_ = [
        ("ActualLength", W.ULONG),
        ("DriverKeyName", W.WCHAR * 1),
    ]

PUSB_HCD_DRIVERKEY_NAME = C.POINTER(USB_HCD_DRIVERKEY_NAME)

class USB_ROOT_HUB_NAME(C.Structure):
    _fields_ = [
        ("ActualLength", W.ULONG),
        ("RootHubName", W.WCHAR * 1),
    ]

PUSB_ROOT_HUB_NAME = C.POINTER(USB_ROOT_HUB_NAME)

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

# wtypesbase.h

class SECURITY_ATTRIBUTES(C.Structure):
    _fields_ = [
        ("nLength", W.DWORD),
        ("lpSecurityDescriptor", W.LPVOID),
        ("bInheritHandle", W.BOOL),
    ]

LPSECURITY_ATTRIBUTES = C.POINTER(SECURITY_ATTRIBUTES)
