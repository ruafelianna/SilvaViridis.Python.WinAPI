import ctypes as C

from ..advapi32 import (
    RegCloseKey,
)

def free_regkey(
    regkey_ptr : C.c_void_p,
) -> None:
    RegCloseKey(regkey_ptr)
