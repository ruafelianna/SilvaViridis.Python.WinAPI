from __future__ import annotations

import ctypes

from .basetsd import ULONG_PTR
from .guiddef import GUID, LPGUID
from .minwindef import BOOL, DWORD, PBYTE, PDWORD
from .windef import HWND
from .winnt import PCWSTR, WCHAR

setupapi = ctypes.windll.LoadLibrary("SetupAPI.dll")

HDEVINFO = ctypes.c_void_p

DIGCF_PRESENT = 0x00000002
DIGCF_DEVICEINTERFACE = 0x00000010

SPDRP_DEVICEDESC = DWORD(0x00000000)
SPDRP_DRIVER = DWORD(0x00000009)

class SP_DEVINFO_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("ClassGuid", GUID),
        ("DevInst", DWORD),
        ("Reserved", ULONG_PTR),
    ]

    @staticmethod
    def create() -> SP_DEVINFO_DATA:
        data = SP_DEVINFO_DATA()
        data.cbSize = ctypes.sizeof(SP_DEVINFO_DATA)
        return data

PSP_DEVINFO_DATA = ctypes.POINTER(SP_DEVINFO_DATA)

class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("InterfaceClassGuid", GUID),
        ("Flags", DWORD),
        ("Reserved", ULONG_PTR),
    ]

    @staticmethod
    def create() -> SP_DEVICE_INTERFACE_DATA:
        data = SP_DEVICE_INTERFACE_DATA()
        data.cbSize = ctypes.sizeof(SP_DEVICE_INTERFACE_DATA)
        return data

PSP_DEVICE_INTERFACE_DATA = ctypes.POINTER(SP_DEVICE_INTERFACE_DATA)

class SP_DEVICE_INTERFACE_DETAIL_DATA_W(ctypes.Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("DevicePath", WCHAR * 1),
    ]

PSP_DEVICE_INTERFACE_DETAIL_DATA_W = ctypes.POINTER(SP_DEVICE_INTERFACE_DETAIL_DATA_W)

SetupDiEnumDeviceInfo = setupapi.SetupDiEnumDeviceInfo
SetupDiEnumDeviceInfo.argtypes = [
    HDEVINFO, # DeviceInfoSet
    DWORD, # MemberIndex
    PSP_DEVINFO_DATA, # DeviceInfoData
]
SetupDiEnumDeviceInfo.restype = BOOL

SetupDiEnumDeviceInterfaces = setupapi.SetupDiEnumDeviceInterfaces
SetupDiEnumDeviceInterfaces.argtypes = [
    HDEVINFO, # DeviceInfoSet
    PSP_DEVINFO_DATA, # DeviceInfoData
    LPGUID, # InterfaceClassGuid
    DWORD, # MemberIndex
    PSP_DEVICE_INTERFACE_DATA, # DeviceInterfaceData
]
SetupDiEnumDeviceInterfaces.restype = BOOL

SetupDiGetClassDevs = setupapi.SetupDiGetClassDevsW
SetupDiGetClassDevs.argtypes = [
    LPGUID, # ClassGuid
    PCWSTR, # Enumerator
    HWND, # hwndParent
    DWORD, # Flags
]
SetupDiGetClassDevs.restype = HDEVINFO

SetupDiGetDeviceInterfaceDetail = setupapi.SetupDiGetDeviceInterfaceDetailW
SetupDiGetDeviceInterfaceDetail.argtypes = [
    HDEVINFO, # DeviceInfoSet
    PSP_DEVICE_INTERFACE_DATA, # DeviceInterfaceData
    PSP_DEVICE_INTERFACE_DETAIL_DATA_W, # DeviceInterfaceDetailData
    DWORD, # DeviceInterfaceDetailDataSize
    PDWORD, # RequiredSize
    PSP_DEVINFO_DATA, # DeviceInfoData
]
SetupDiGetDeviceInterfaceDetail.restype = BOOL

SetupDiGetDeviceRegistryProperty = setupapi.SetupDiGetDeviceRegistryPropertyW
SetupDiGetDeviceRegistryProperty.argtypes = [
    HDEVINFO, # DeviceInfoSet
    PSP_DEVINFO_DATA, # DeviceInfoData
    DWORD, # Property
    PDWORD, # PropertyRegDataType
    PBYTE, # PropertyBuffer
    DWORD, # PropertyBufferSize
    PDWORD, # RequiredSize
]
SetupDiGetDeviceRegistryProperty.restype = BOOL
