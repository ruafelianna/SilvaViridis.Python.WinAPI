import ctypes as C
import ctypes.wintypes as W

from .Exceptions import (
    ERROR_SUCCESS,
    InsufficientBuffer,
    MemAllocError,
    raise_ex,
)

from .Memory import (
    alloc,
    free,
)

from .Utils import (
    ptr_to_str,
)

from ..advapi32 import (
    RegCloseKey,
    RegQueryValueEx,
)

def free_regkey(
    regkey_ptr : C.c_void_p,
) -> None:
    RegCloseKey(regkey_ptr)

def get_registry_key_value(
    regkey_ptr : C.c_void_p,
    field_name : str,
) -> str:
    regtype = W.DWORD(0)
    required_size = W.DWORD(0)

    status = RegQueryValueEx(
        regkey_ptr,
        field_name,
        None,
        C.byref(regtype),
        None,
        C.byref(required_size)
    )

    try:
        raise_ex(status)
    except InsufficientBuffer:
        pass

    buffer = alloc(required_size.value)

    if buffer is None:
        raise MemAllocError()

    buffer_ptr = C.cast(buffer, C.POINTER(C.c_ubyte))

    status = RegQueryValueEx(
        regkey_ptr,
        field_name,
        None,
        C.byref(regtype),
        buffer_ptr,
        C.byref(required_size)
    )

    if status != ERROR_SUCCESS:
        free(buffer)
        raise_ex(status)

    # TODO: could be not a string, check prop_type
    prop_value = ptr_to_str(buffer, required_size.value * 2)

    free(buffer)

    return prop_value
