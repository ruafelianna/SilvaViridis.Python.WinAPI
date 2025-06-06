import ctypes

from .errhandlingapi import GetLastError
from .guiddef import GUID
from .handleapi import INVALID_HANDLE_VALUE
from .minwindef import DWORD, TRUE, FALSE, HGLOBAL
from .setupapi import (
    DIGCF_DEVICEINTERFACE,
    DIGCF_PRESENT,
    HDEVINFO,
    SP_DEVINFO_DATA,
    SetupDiEnumDeviceInfo,
    SetupDiGetClassDevs,
    SetupDiGetDeviceRegistryProperty,
)
from .winbase import GPTR, GlobalAlloc, GlobalFree
from .winerror import (
    ERROR_INSUFFICIENT_BUFFER,
    ERROR_NO_MORE_ITEMS,
)

def get_string(pointer : HGLOBAL, length : int) -> str:
    return (ctypes.c_wchar * (length // 2)).from_address(int(pointer)).value

def enumerate_devices(guid : GUID) -> tuple[HDEVINFO | None, list[SP_DEVINFO_DATA]]:
    hdevinfo = SetupDiGetClassDevs(
        ctypes.byref(guid),
        None,
        None,
        DIGCF_PRESENT | DIGCF_DEVICEINTERFACE,
    )

    if hdevinfo == INVALID_HANDLE_VALUE:
        return None, []

    index = 0
    error = 0
    result : list[SP_DEVINFO_DATA] = []

    while error != ERROR_NO_MORE_ITEMS:
        devinfo = SP_DEVINFO_DATA()
        devinfo.cbSize = ctypes.sizeof(SP_DEVINFO_DATA)

        success = SetupDiEnumDeviceInfo(
            hdevinfo,
            index,
            devinfo,
        )

        index += 1

        if success == TRUE:
            result.append(devinfo)
        else:
            error = GetLastError()

            if error != ERROR_NO_MORE_ITEMS:
                raise Exception(f"WinAPI error: {error}")

    return hdevinfo, result

def get_device_property(
    hdevinfo : HDEVINFO,
    devinfo : SP_DEVINFO_DATA,
    property : DWORD,
) -> str:
    required_length = DWORD(0)

    success = SetupDiGetDeviceRegistryProperty(
        hdevinfo,
        ctypes.byref(devinfo),
        property,
        None,
        None,
        0,
        ctypes.byref(required_length),
    )

    last_error = GetLastError()

    if (
        required_length.value == 0
        or (
            success == TRUE
            and last_error != ERROR_INSUFFICIENT_BUFFER
        )
    ):
        raise Exception(f"Cannot get a length for the property: {property}")

    buffer = GlobalAlloc(GPTR, required_length.value)

    if buffer is None:
        raise Exception(f"Cannot allocate memory for the buffer")

    byte_array = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))

    success = SetupDiGetDeviceRegistryProperty(
        hdevinfo,
        ctypes.byref(devinfo),
        property,
        None,
        byte_array,
        required_length,
        None,
    )

    if success == FALSE:
        GlobalFree(buffer)
        raise Exception(f"Cannot get the property: {property}")

    prop = get_string(buffer, required_length.value)
    GlobalFree(buffer)

    return prop
