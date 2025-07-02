from __future__ import annotations

import ctypes as C
import ctypes.wintypes as W

from uuid import UUID

from .Exceptions import (
    raise_ex,
    InsufficientBuffer,
    MemAllocError,
)
from .Memory import (
    alloc,
    free,
)
from .Types import (
    INVALID_HANDLE_VALUE,
    FALSE,
    ValueTypes,
    DevInfoData,
    DevInterfaceData,
    DevProperties,
    IncludedInfoFlags,
    DevPropKeys,
)
from .Utils import (
    str_to_ptr,
    ptr_to_str,
    uuid_to_guid,
)

from ..setupapi import (
    SetupDiEnumDeviceInfo,
    SetupDiEnumDeviceInterfaces,
    SetupDiGetClassDevs,
    SetupDiGetDeviceRegistryProperty,
    SetupDiGetDeviceInterfaceDetail,
    SetupDiDestroyDeviceInfoList,
    SetupDiGetDeviceInstanceId,
    SetupDiGetDeviceProperty,
)
from ..types import (
    SP_DEVINFO_DATA,
    SP_DEVICE_INTERFACE_DATA,
    SP_DEVICE_INTERFACE_DETAIL_DATA,
    PSP_DEVICE_INTERFACE_DETAIL_DATA,
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

def get_device_registry_property(
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

    prop_type = ValueTypes(prop_type.value)

    if prop_type == ValueTypes.NONE:
        prop = None
    elif prop_type in [
        ValueTypes.SZ,
        ValueTypes.EXPAND_SZ,
        ValueTypes.MULTI_SZ,
        ValueTypes.LINK,
    ]:
        prop = ptr_to_str(buffer, required_length.value)
    elif prop_type in [
        ValueTypes.DWORD,
        ValueTypes.DWORD_LITTLE_ENDIAN,
    ]:
        prop = W.DWORD.from_address(int(buffer)).value
    elif prop_type == ValueTypes.DWORD_BIG_ENDIAN:
        prop = W.DWORD.from_address(int(buffer)).value # TODO: big endian
    elif prop_type in [
        ValueTypes.QWORD,
        ValueTypes.QWORD_LITTLE_ENDIAN,
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

    details = C.cast(details_buffer, PSP_DEVICE_INTERFACE_DETAIL_DATA)

    details.contents.cbSize = C.sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA)

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
        int(details_buffer) + C.sizeof(W.DWORD),
        required_length.value - C.sizeof(W.DWORD)
    )

    return devpath

def free_device_list(
    hdevinfo : C.c_void_p,
) -> None:
    SetupDiDestroyDeviceInfoList(hdevinfo)

def get_device_instance_id(
    hdevinfo : C.c_void_p,
    devinfo : DevInfoData,
) -> str:
    required_length = W.DWORD(0)
    devinfo_ptr = C.byref(devinfo.to_internal())

    SetupDiGetDeviceInstanceId(
        hdevinfo,
        devinfo_ptr,
        None,
        0,
        C.byref(required_length),
    )

    try:
        raise_ex(C.GetLastError())
    except InsufficientBuffer:
        pass

    devid_ptr = alloc(required_length.value * 2)

    if devid_ptr is None:
        raise MemAllocError()

    devid_array = C.cast(devid_ptr, C.c_wchar_p)

    success = SetupDiGetDeviceInstanceId(
        hdevinfo,
        devinfo_ptr,
        devid_array,
        required_length,
        C.byref(required_length),
    )

    if success == FALSE:
        free(devid_ptr)
        raise_ex(C.GetLastError())

    devid = ptr_to_str(devid_ptr, required_length.value * 2)

    free(devid_ptr)

    return devid

def get_device_property(
    hdevinfo : C.c_void_p,
    devinfo : DevInfoData,
    prop_key : DevPropKeys,
):
    prop_key_ptr = C.byref(prop_key.value.to_internal())
    devinfo_ptr = C.byref(devinfo.to_internal())
    prop_type = W.ULONG(0)
    required_size = W.DWORD(0)

    success = SetupDiGetDeviceProperty(
        hdevinfo,
        devinfo_ptr,
        prop_key_ptr,
        C.byref(prop_type),
        None,
        0,
        C.byref(required_size),
        0,
    )

    try:
        raise_ex(C.GetLastError())
    except InsufficientBuffer:
        pass

    buffer = alloc(required_size.value)

    if buffer is None:
        raise MemAllocError()

    buffer_ptr = C.cast(buffer, C.POINTER(C.c_ubyte))

    success = SetupDiGetDeviceProperty(
        hdevinfo,
        devinfo_ptr,
        prop_key_ptr,
        C.byref(prop_type),
        buffer_ptr,
        required_size,
        None,
        0,
    )

    if success == FALSE:
        free(buffer)
        raise_ex(C.GetLastError())

    prop_value = ptr_to_str(buffer, required_size.value * 2)

    free(buffer)

    return prop_value
