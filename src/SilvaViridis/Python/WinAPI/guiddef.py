import ctypes

class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    def __str__(self):
        return f"{self.Data1:08x}-{self.Data2:04x}-{self.Data3:04x}-{"".join([f"{b:02x}" for b in self.Data4])}"

LPGUID = ctypes.POINTER(GUID)
