from __future__ import annotations

import ctypes as C
import ctypes.wintypes as W

from .types import (
    LPGUID,
    HDEVINFO,
    PSP_DEVINFO_DATA,
    PSP_DEVICE_INTERFACE_DATA,
    PSP_DEVICE_INTERFACE_DETAIL_DATA,
    PDEVPROPKEY,
)

_setupapi = C.windll.LoadLibrary("SetupAPI.dll")

SetupDiEnumDeviceInfo = _setupapi.SetupDiEnumDeviceInfo
SetupDiEnumDeviceInfo.argtypes = [
    HDEVINFO, # DeviceInfoSet
    W.DWORD, # MemberIndex
    PSP_DEVINFO_DATA, # DeviceInfoData
]
SetupDiEnumDeviceInfo.restype = W.BOOL

SetupDiEnumDeviceInterfaces = _setupapi.SetupDiEnumDeviceInterfaces
SetupDiEnumDeviceInterfaces.argtypes = [
    HDEVINFO, # DeviceInfoSet
    PSP_DEVINFO_DATA, # DeviceInfoData
    LPGUID, # InterfaceClassGuid
    W.DWORD, # MemberIndex
    PSP_DEVICE_INTERFACE_DATA, # DeviceInterfaceData
]
SetupDiEnumDeviceInterfaces.restype = W.BOOL

SetupDiGetClassDevs = _setupapi.SetupDiGetClassDevsW
SetupDiGetClassDevs.argtypes = [
    LPGUID, # ClassGuid
    W.PWCHAR, # Enumerator
    W.HWND, # hwndParent
    W.DWORD, # Flags
]
SetupDiGetClassDevs.restype = HDEVINFO

SetupDiGetDeviceInterfaceDetail = _setupapi.SetupDiGetDeviceInterfaceDetailW
SetupDiGetDeviceInterfaceDetail.argtypes = [
    HDEVINFO, # DeviceInfoSet
    PSP_DEVICE_INTERFACE_DATA, # DeviceInterfaceData
    PSP_DEVICE_INTERFACE_DETAIL_DATA, # DeviceInterfaceDetailData
    W.DWORD, # DeviceInterfaceDetailDataSize
    W.PDWORD, # RequiredSize
    PSP_DEVINFO_DATA, # DeviceInfoData
]
SetupDiGetDeviceInterfaceDetail.restype = W.BOOL

SetupDiGetDeviceRegistryProperty = _setupapi.SetupDiGetDeviceRegistryPropertyW
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

SetupDiDestroyDeviceInfoList = _setupapi.SetupDiDestroyDeviceInfoList
SetupDiDestroyDeviceInfoList.argtypes = [
    HDEVINFO, # DeviceInfoSet
]
SetupDiDestroyDeviceInfoList.restype = W.BOOL

SetupDiGetDeviceInstanceId = _setupapi.SetupDiGetDeviceInstanceIdW
SetupDiGetDeviceInstanceId.argtypes = [
    HDEVINFO, # DeviceInfoSet
    PSP_DEVINFO_DATA, # DeviceInfoData
    W.PWCHAR, # DeviceInstanceId
    W.DWORD, # DeviceInstanceIdSize
    W.PDWORD, # RequiredSize
]
SetupDiGetDeviceInstanceId.restype = W.BOOL

SetupDiGetDeviceProperty = _setupapi.SetupDiGetDevicePropertyW
SetupDiGetDeviceProperty.argtypes = [
    HDEVINFO, # DeviceInfoSet
    PSP_DEVINFO_DATA, # DeviceInfoData
    PDEVPROPKEY, # PropertyKey
    W.PULONG, # PropertyType
    W.PBYTE, # PropertyBuffer
    W.DWORD, # PropertyBufferSize
    W.PDWORD, # RequiredSize
    W.DWORD, # Flags
]
SetupDiGetDeviceProperty.restype = W.BOOL
