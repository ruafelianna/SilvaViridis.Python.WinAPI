from __future__ import annotations

import ctypes as C
import ctypes.wintypes as W

from dataclasses import dataclass
from enum import Enum, Flag
from uuid import UUID

from .Consts import INVALID_HANDLE_VALUE, FALSE
from .Exceptions import raise_ex, InsufficientBuffer, MemAllocError
from .Memory import alloc, free
from .Types import ValueType
from .Utils import (
    str_to_ptr,
    ptr_to_str,
    uuid_to_guid,
    guid_to_uuid,
)

from ..setupapi import (
    SP_DEVINFO_DATA,
    SP_DEVICE_INTERFACE_DATA,
    SP_DEVICE_INTERFACE_DETAIL_DATA_W,
    PSP_DEVICE_INTERFACE_DETAIL_DATA_W,
    SetupDiEnumDeviceInfo,
    SetupDiEnumDeviceInterfaces,
    SetupDiGetClassDevs,
    SetupDiGetDeviceRegistryProperty,
    SetupDiGetDeviceInterfaceDetail,
)

class IncludedInfoFlags(Flag):
    DEFAULT = 0x00000001
    PRESENT = 0x00000002
    ALLCLASSES = 0x00000004
    PROFILE = 0x00000008
    DEVICEINTERFACE = 0x00000010

class DevProperties(Enum):
	DEVICEDESC = 0x00000000
	HARDWAREID = 0x00000001
	COMPATIBLEIDS = 0x00000002
	UNUSED0 = 0x00000003
	SERVICE = 0x00000004
	UNUSED1 = 0x00000005
	UNUSED2 = 0x00000006
	CLASS = 0x00000007
	CLASSGUID = 0x00000008
	DRIVER = 0x00000009
	CONFIGFLAGS = 0x0000000a
	MFG = 0x0000000b
	FRIENDLYNAME = 0x0000000c
	LOCATION_INFORMATION = 0x0000000d
	PHYSICAL_DEVICE_OBJECT_NAME = 0x0000000e
	CAPABILITIES = 0x0000000f
	UI_NUMBER = 0x00000010
	UPPERFILTERS = 0x00000011
	LOWERFILTERS = 0x00000012
	BUSTYPEGUID = 0x00000013
	LEGACYBUSTYPE = 0x00000014
	BUSNUMBER = 0x00000015
	ENUMERATOR_NAME = 0x00000016
	SECURITY = 0x00000017
	SECURITY_SDS = 0x00000018
	DEVTYPE = 0x00000019
	EXCLUSIVE = 0x0000001a
	CHARACTERISTICS = 0x0000001b
	ADDRESS = 0x0000001c
	UI_NUMBER_DESC_FORMAT = 0X0000001d
	DEVICE_POWER_DATA = 0x0000001e
	REMOVAL_POLICY = 0x0000001f
	REMOVAL_POLICY_HW_DEFAULT = 0x00000020
	REMOVAL_POLICY_OVERRIDE = 0x00000021
	INSTALL_STATE = 0x00000022
	LOCATION_PATHS = 0x00000023
	BASE_CONTAINERID = 0x00000024
	MAXIMUM_PROPERTY = 0x00000025

class DevInterfaceFlags(Flag):
    ACTIVE = 0x00000001
    DEFAULT = 0x00000002
    REMOVED = 0x00000004

@dataclass
class DevInfoData:
    class_guid : UUID
    dev_inst_handle : int
    reserved : C.c_void_p

    def to_internal(self) -> SP_DEVINFO_DATA:
        data = SP_DEVINFO_DATA.create()
        data.ClassGuid = uuid_to_guid(self.class_guid)
        data.DevInst = self.dev_inst_handle
        data.Reserved = self.reserved
        return data

    @staticmethod
    def create(data : SP_DEVINFO_DATA) -> DevInfoData:
        return DevInfoData(
            class_guid = guid_to_uuid(data.ClassGuid),
            dev_inst_handle = data.DevInst,
            reserved = data.Reserved,
        )

@dataclass
class DevInterfaceData:
    interface_class_guid : UUID
    flags : DevInterfaceFlags
    reserved : C.c_void_p

    def to_internal(self) -> SP_DEVICE_INTERFACE_DATA:
        data = SP_DEVICE_INTERFACE_DATA.create()
        data.InterfaceClassGuid = uuid_to_guid(self.interface_class_guid)
        data.Flags = self.flags.value
        data.Reserved = self.reserved
        return data

    @staticmethod
    def create(data : SP_DEVICE_INTERFACE_DATA) -> DevInterfaceData:
        return DevInterfaceData(
            interface_class_guid = guid_to_uuid(data.InterfaceClassGuid),
            flags = DevInterfaceFlags(data.Flags),
            reserved = data.Reserved,
        )

def get_class_devs(
    guid : UUID,
    enumerator : str | None,
    parent_hwnd : W.HWND | None,
    flags : IncludedInfoFlags,
) -> C.c_void_p:
    hdevinfo = SetupDiGetClassDevs(
        C.byref(uuid_to_guid(guid)),
        None if enumerator is None else str_to_ptr(enumerator),
        parent_hwnd,
        flags.value,
    )

    if hdevinfo == INVALID_HANDLE_VALUE:
        error = C.GetLastError()
        raise Exception(f"Cannot get class devs handle, err: {error}")

    return hdevinfo

def next_device_info(
    hdevinfo : C.c_void_p,
    index : int,
) -> DevInfoData:
    data = SP_DEVINFO_DATA.create()

    success = SetupDiEnumDeviceInfo(
        hdevinfo,
        index,
        C.byref(data),
    )

    if success == FALSE:
        error = C.GetLastError()
        raise_ex(error)

    return DevInfoData.create(data)

def get_device_property(
    hdevinfo : C.c_void_p,
    devinfo : DevInfoData,
    property : DevProperties,
) -> str | int | bytes | None:
    required_length = W.DWORD(0)
    devinfo_ptr = C.byref(devinfo.to_internal())

    SetupDiGetDeviceRegistryProperty(
        hdevinfo,
        devinfo_ptr,
        property.value,
        None,
        None,
        0,
        C.byref(required_length),
    )

    try:
        raise_ex(C.GetLastError())
    except InsufficientBuffer:
        pass

    buffer = alloc(required_length.value)

    if buffer is None:
        raise MemAllocError()

    byte_array = C.cast(buffer, C.POINTER(C.c_ubyte))
    prop_type = W.DWORD(0)

    success = SetupDiGetDeviceRegistryProperty(
        hdevinfo,
        devinfo_ptr,
        property.value,
        C.byref(prop_type),
        byte_array,
        required_length,
        None,
    )

    if success == FALSE:
        free(buffer)
        raise_ex(C.GetLastError())

    prop_type = ValueType(prop_type.value)

    if prop_type == ValueType.NONE:
        prop = None
    elif prop_type in [
        ValueType.SZ,
        ValueType.EXPAND_SZ,
        ValueType.MULTI_SZ,
        ValueType.LINK,
    ]:
        prop = ptr_to_str(buffer, required_length.value)
    elif prop_type in [
        ValueType.DWORD,
        ValueType.DWORD_LITTLE_ENDIAN,
    ]:
        prop = W.DWORD.from_address(int(buffer)).value
    elif prop_type == ValueType.DWORD_BIG_ENDIAN:
        prop = W.DWORD.from_address(int(buffer)).value # TODO: big endian
    elif prop_type in [
        ValueType.QWORD,
        ValueType.QWORD_LITTLE_ENDIAN,
    ]:
        prop = C.c_int64.from_address(int(buffer)).value
    else:
        prop = C.string_at(buffer)

    free(buffer)

    return prop

def get_device_interface(
    hdevinfo : C.c_void_p,
    guid : UUID,
    index : int,
) -> DevInterfaceData:
    data = SP_DEVICE_INTERFACE_DATA.create()

    success = SetupDiEnumDeviceInterfaces(
        hdevinfo,
        None,
        C.byref(uuid_to_guid(guid)),
        index,
        C.byref(data),
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    return DevInterfaceData.create(data)

def get_device_interface_devpath(
    hdevinfo : C.c_void_p,
    interface_data : DevInterfaceData,
) -> str:
    required_length = W.DWORD(0)
    interface_data_ptr = C.byref(interface_data.to_internal())

    success = SetupDiGetDeviceInterfaceDetail(
        hdevinfo,
        interface_data_ptr,
        None,
        0,
        C.byref(required_length),
        None,
    )

    try:
        raise_ex(C.GetLastError())
    except InsufficientBuffer:
        pass

    details_buffer = alloc(required_length.value)

    if details_buffer is None:
        raise MemAllocError()

    details = C.cast(details_buffer, PSP_DEVICE_INTERFACE_DETAIL_DATA_W)

    details.contents.cbSize = C.sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA_W)

    success = SetupDiGetDeviceInterfaceDetail(
        hdevinfo,
        interface_data_ptr,
        details,
        required_length.value,
        C.byref(required_length),
        None,
    )

    if success == FALSE:
        free(details_buffer)
        raise_ex(C.GetLastError())

    devpath = ptr_to_str(
        C.c_void_p(int(details_buffer) + C.sizeof(W.DWORD)),
        required_length.value - C.sizeof(W.DWORD)
    )

    return devpath
