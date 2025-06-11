import ctypes as C

from .Types import GPTR

from ..kernel32 import GlobalAlloc, GlobalFree

def alloc(n_bytes : int) -> C.c_void_p | None:
    return GlobalAlloc(GPTR.value, n_bytes)

def free(ptr : C.c_void_p) -> None:
    GlobalFree(ptr)
