import ctypes as C

from enum import Flag

from ..kernel32 import GlobalAlloc, GlobalFree

class GMEM(Flag):
    FIXED = 0x0000
    MOVEABLE = 0x0002
    NOCOMPACT = 0x0010
    NODISCARD = 0x0020
    ZEROINIT = 0x0040
    MODIFY = 0x0080
    DISCARDABLE = 0x0100
    NOT_BANKED = 0x1000
    SHARE = 0x2000
    DDESHARE = 0x2000
    NOTIFY = 0x4000
    LOWER = NOT_BANKED
    VALID_FLAGS = 0x7F72
    INVALID_HANDLE = 0x8000

GHND = GMEM.MOVEABLE | GMEM.ZEROINIT
GPTR = GMEM.FIXED | GMEM.ZEROINIT

def alloc(n_bytes : int) -> C.c_void_p | None:
    return GlobalAlloc(GPTR.value, n_bytes)

def free(ptr : C.c_void_p) -> None:
    GlobalFree(ptr)
