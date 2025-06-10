import ctypes as C

from uuid import UUID

from ..guiddef import GUID

def uuid_to_guid(uuid : UUID) -> GUID:
    guid = GUID()
    guid.Data1 = uuid.fields[0]
    guid.Data2 = uuid.fields[1]
    guid.Data3 = uuid.fields[2]
    guid.Data4 = (C.c_ubyte * 8)(*uuid.bytes[8:])
    return guid

def guid_to_uuid(guid : GUID) -> UUID:
    return UUID(str(guid))

def str_to_ptr(data : str) -> C.c_wchar_p:
    return C.c_wchar_p(data)

def ptr_to_str(ptr : C.c_void_p | int, length : int) -> str:
    if isinstance(ptr, C.c_void_p):
        if ptr.value is None:
            return ""
        ptr = ptr.value

    return (C.c_wchar * (length // 2)).from_address(ptr).value
