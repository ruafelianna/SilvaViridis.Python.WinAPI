from __future__ import annotations

import ctypes as C
import ctypes.wintypes as W

from .guiddef import GUID, LPGUID

setupapi = C.windll.LoadLibrary("SetupAPI.dll")

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

class SP_DEVICE_INTERFACE_DETAIL_DATA_W(C.Structure):
    _fields_ = [
        ("cbSize", W.DWORD),
        ("DevicePath", W.WCHAR * 1),
    ]

PSP_DEVICE_INTERFACE_DETAIL_DATA_W = C.POINTER(SP_DEVICE_INTERFACE_DETAIL_DATA_W)

SetupDiEnumDeviceInfo = setupapi.SetupDiEnumDeviceInfo
SetupDiEnumDeviceInfo.argtypes = [
    HDEVINFO, # DeviceInfoSet
    W.DWORD, # MemberIndex
    PSP_DEVINFO_DATA, # DeviceInfoData
]
SetupDiEnumDeviceInfo.restype = W.BOOL

SetupDiEnumDeviceInterfaces = setupapi.SetupDiEnumDeviceInterfaces
SetupDiEnumDeviceInterfaces.argtypes = [
    HDEVINFO, # DeviceInfoSet
    PSP_DEVINFO_DATA, # DeviceInfoData
    LPGUID, # InterfaceClassGuid
    W.DWORD, # MemberIndex
    PSP_DEVICE_INTERFACE_DATA, # DeviceInterfaceData
]
SetupDiEnumDeviceInterfaces.restype = W.BOOL

SetupDiGetClassDevs = setupapi.SetupDiGetClassDevsW
SetupDiGetClassDevs.argtypes = [
    LPGUID, # ClassGuid
    W.PWCHAR, # Enumerator
    W.HWND, # hwndParent
    W.DWORD, # Flags
]
SetupDiGetClassDevs.restype = HDEVINFO

SetupDiGetDeviceInterfaceDetail = setupapi.SetupDiGetDeviceInterfaceDetailW
SetupDiGetDeviceInterfaceDetail.argtypes = [
    HDEVINFO, # DeviceInfoSet
    PSP_DEVICE_INTERFACE_DATA, # DeviceInterfaceData
    PSP_DEVICE_INTERFACE_DETAIL_DATA_W, # DeviceInterfaceDetailData
    W.DWORD, # DeviceInterfaceDetailDataSize
    W.PDWORD, # RequiredSize
    PSP_DEVINFO_DATA, # DeviceInfoData
]
SetupDiGetDeviceInterfaceDetail.restype = W.BOOL

SetupDiGetDeviceRegistryProperty = setupapi.SetupDiGetDeviceRegistryPropertyW
SetupDiGetDeviceRegistryProperty.argtypes = [
    HDEVINFO, # DeviceInfoSet
    PSP_DEVINFO_DATA, # DeviceInfoData
    W.DWORD, # Property
    W.PDWORD, # PropertyRegDataType
    W.PBYTE, # PropertyBuffer
    W.DWORD, # PropertyBufferSize
    W.PDWORD, # RequiredSize
]
SetupDiGetDeviceRegistryProperty.restype = W.BOOL
