import ctypes as C

class GUID(C.Structure):
    _fields_ = [
        ("Data1", C.c_ulong),
        ("Data2", C.c_ushort),
        ("Data3", C.c_ushort),
        ("Data4", C.c_ubyte * 8),
    ]

    def __str__(self):
        return f"{self.Data1:08x}-{self.Data2:04x}-{self.Data3:04x}-{"".join([f"{b:02x}" for b in self.Data4])}"

LPGUID = C.POINTER(GUID)
