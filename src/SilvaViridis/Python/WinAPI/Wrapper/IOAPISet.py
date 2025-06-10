import ctypes as C
import ctypes.wintypes as W

from .Consts import FALSE
from .Exceptions import MemAllocError, raise_ex
from .Memory import alloc, free
from .IO import CtlCodes
from .Utils import ptr_to_str

from ..kernel32 import (
    USB_HCD_DRIVERKEY_NAME,
    DeviceIoControl,
)

def ioctl_get_hcd_driver_key_name(
    fd : W.HANDLE,
):
    driver_key_name = USB_HCD_DRIVERKEY_NAME()
    nBytes = W.ULONG(0)

    success = DeviceIoControl(
        fd,
        CtlCodes.IOCTL_GET_HCD_DRIVERKEY_NAME.value,
        C.byref(driver_key_name),
        C.sizeof(driver_key_name),
        C.byref(driver_key_name),
        C.sizeof(driver_key_name),
        C.byref(nBytes),
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    nBytes = driver_key_name.ActualLength

    driver_key_name_ptr = alloc(nBytes)

    if driver_key_name_ptr is None:
        raise MemAllocError()

    success = DeviceIoControl(
        fd,
        CtlCodes.IOCTL_GET_HCD_DRIVERKEY_NAME.value,
        driver_key_name_ptr,
        nBytes,
        driver_key_name_ptr,
        nBytes,
        None,
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    not_str_len = C.sizeof(W.ULONG)

    driver_key_name = ptr_to_str(
        int(driver_key_name_ptr) + not_str_len,
        nBytes - not_str_len,
    )

    free(driver_key_name_ptr)

    return driver_key_name
