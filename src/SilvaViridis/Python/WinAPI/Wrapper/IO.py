import ctypes as C

from enum import Enum, Flag

from .Consts import INVALID_HANDLE_VALUE
from .Exceptions import raise_ex
from .Utils import str_to_ptr

from ..kernel32 import CreateFile, CloseHandle

class GenericRights(Flag):
    READ = 0x80000000
    WRITE = 0x40000000
    EXECUTE = 0x20000000
    ALL = 0x10000000

class ShareModes(Flag):
    READ = 0x00000001
    WRITE = 0x00000002
    DELETE = 0x00000004

class CreationModes(Enum):
    CREATE_NEW = 1
    CREATE_ALWAYS = 2
    OPEN_EXISTING = 3
    OPEN_ALWAYS = 4
    TRUNCATE_EXISTING = 5

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
