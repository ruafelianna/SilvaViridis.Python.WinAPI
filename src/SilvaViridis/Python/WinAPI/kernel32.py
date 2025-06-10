import ctypes as C
import ctypes.wintypes as W

_kernel32 = C.windll.LoadLibrary("Kernel32.dll")

class SECURITY_ATTRIBUTES(C.Structure):
    _fields_ = [
        ("nLength", W.DWORD),
        ("lpSecurityDescriptor", W.LPVOID),
        ("bInheritHandle", W.BOOL),
    ]

LPSECURITY_ATTRIBUTES = C.POINTER(SECURITY_ATTRIBUTES)

GlobalAlloc = _kernel32.GlobalAlloc
GlobalAlloc.argtypes = [
    C.c_uint, # uFlags
    C.c_size_t, # dwBytes
]
GlobalAlloc.restype = C.c_void_p

GlobalFree = _kernel32.GlobalFree
GlobalFree.argtypes = [
    C.c_void_p, # hMem
]
GlobalFree.restype = C.c_void_p

CreateFile = _kernel32.CreateFileW
CreateFile.argtypes = [
    W.LPWSTR, # lpFileName
    W.DWORD, # dwDesiredAccess
    W.DWORD, # dwShareMode
    LPSECURITY_ATTRIBUTES, # lpSecurityAttributes
    W.DWORD, # dwCreationDisposition
    W.DWORD, # dwFlagsAndAttributes
    C.c_void_p, # hTemplateFile
]
CreateFile.restype = C.c_void_p

CloseHandle = _kernel32.CloseHandle
CloseHandle.argtypes = [
    C.c_void_p,
]
CloseHandle.restype = W.BOOL
