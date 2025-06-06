import ctypes

from .errhandlingapi import GetLastError
from .guiddef import GUID
from .handleapi import INVALID_HANDLE_VALUE
from .minwindef import TRUE
from .setupapi import (
    DIGCF_DEVICEINTERFACE,
    DIGCF_PRESENT,
    SP_DEVINFO_DATA,
    SetupDiEnumDeviceInfo,
    SetupDiGetClassDevs,
)
from .winerror import ERROR_NO_MORE_ITEMS

def enumerate_devices(guid : GUID) -> list[SP_DEVINFO_DATA]:
    hdevinfo = SetupDiGetClassDevs(
        ctypes.byref(guid),
        None,
        None,
        DIGCF_PRESENT | DIGCF_DEVICEINTERFACE,
    )

    if hdevinfo == INVALID_HANDLE_VALUE:
        return []

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

    return result
