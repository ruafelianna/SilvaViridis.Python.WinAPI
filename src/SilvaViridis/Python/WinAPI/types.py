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

# usbspec.h

class USB_HUB_DESCRIPTOR(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("bDescriptorLength", C.c_ubyte),
        ("bDescriptorType", C.c_ubyte),
        ("bNumberOfPorts", C.c_ubyte),
        ("wHubCharacteristics", W.USHORT),
        ("bPowerOnToPowerGood", C.c_ubyte),
        ("bHubControlCurrent", C.c_ubyte),
        ("bRemoveAndPowerMask", C.c_ubyte * 64),
    ]

PUSB_HUB_DESCRIPTOR = C.POINTER(USB_HUB_DESCRIPTOR)

class USB_30_HUB_DESCRIPTOR(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("bLength", C.c_ubyte),
        ("bDescriptorType", C.c_ubyte),
        ("bNumberOfPorts", C.c_ubyte),
        ("wHubCharacteristics", W.USHORT),
        ("bPowerOnToPowerGood", C.c_ubyte),
        ("bHubControlCurrent", C.c_ubyte),
        ("bHubHdrDecLat", C.c_ubyte),
        ("wHubDelay", W.USHORT),
        ("DeviceRemovable", W.USHORT),
    ]

PUSB_30_HUB_DESCRIPTOR = C.POINTER(USB_30_HUB_DESCRIPTOR)

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

class USB_HUB_INFORMATION(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("HubDescriptor", USB_HUB_DESCRIPTOR),
        ("HubIsBusPowered", W.BOOLEAN),
    ]

class USB_MI_PARENT_INFORMATION(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("NumberOfInterfaces", W.ULONG),
    ]

class USB_NODE_INFORMATION_u(C.Union):
    _pack_ = 1
    _fields_ = [
        ("HubInformation", USB_HUB_INFORMATION),
        ("MiParentInformation", USB_MI_PARENT_INFORMATION),
    ]

class USB_NODE_INFORMATION(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("NodeType", C.c_int),
        ("u", USB_NODE_INFORMATION_u),
    ]

PUSB_NODE_INFORMATION = C.POINTER(USB_NODE_INFORMATION)

class USB_HUB_INFORMATION_EX_u(C.Union):
    _pack_ = 1
    _fields_ = [
        ("UsbHubDescriptor", USB_HUB_DESCRIPTOR),
        ("Usb30HubDescriptor", USB_30_HUB_DESCRIPTOR),
    ]

class USB_HUB_INFORMATION_EX(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("HubType", C.c_int),
        ("HighestPortNumber", W.USHORT),
        ("u", USB_HUB_INFORMATION_EX_u),
    ]

PUSB_HUB_INFORMATION_EX = C.POINTER(USB_HUB_INFORMATION_EX)

class USB_HUB_CAP_FLAGS_BITS(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("HubIsHighSpeedCapable", W.ULONG, 1),
        ("HubIsHighSpeed", W.ULONG, 1),
        ("HubIsMultiTtCapable", W.ULONG, 1),
        ("HubIsMultiTt", W.ULONG, 1),
        ("HubIsRoot", W.ULONG, 1),
        ("HubIsArmedWakeOnConnect", W.ULONG, 1),
        ("HubIsBusPowered", W.ULONG, 1),
        ("ReservedMBZ", W.ULONG, 25),
    ]

class USB_HUB_CAP_FLAGS(C.Union):
    _pack_ = 1
    _fields_ = [
        ("ul", W.ULONG),
        ("bits", USB_HUB_CAP_FLAGS_BITS),
    ]

class USB_HUB_CAPABILITIES_EX(C.Structure):
    _pack_ = 1
    _fields_ = [
        ("CapabilityFlags", USB_HUB_CAP_FLAGS),
    ]

PUSB_HUB_CAPABILITIES_EX = C.POINTER(USB_HUB_CAPABILITIES_EX)

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
