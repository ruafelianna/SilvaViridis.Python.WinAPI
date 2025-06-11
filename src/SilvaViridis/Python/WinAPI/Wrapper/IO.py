import ctypes as C

from .Exceptions import raise_ex
from .Types import (
    INVALID_HANDLE_VALUE,
    GenericRights,
    ShareModes,
    CreationModes,
)
from .Utils import str_to_ptr

from ..kernel32 import CreateFile, CloseHandle

def create_file(
    path : str,
    access : GenericRights,
    share_mode : ShareModes,
    creation_mode : CreationModes,
) -> C.c_void_p:
    fd = CreateFile(
        str_to_ptr(path),
        access.value,
        share_mode.value,
        None,
        creation_mode.value,
        0,
        None,
    )

    if int(fd) == INVALID_HANDLE_VALUE:
        raise_ex(C.GetLastError())

    return fd

def close_file(
    fd : C.c_void_p,
) -> None:
    CloseHandle(fd)
