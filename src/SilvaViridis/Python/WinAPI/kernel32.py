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
    W.UINT, # uFlags
    C.c_size_t, # dwBytes
]
GlobalAlloc.restype = W.HGLOBAL

GlobalFree = _kernel32.GlobalFree
GlobalFree.argtypes = [
    W.HGLOBAL, # hMem
]
GlobalFree.restype = W.HGLOBAL

CreateFile = _kernel32.CreateFileW
CreateFile.argtypes = [
    W.LPWSTR, # lpFileName
    W.DWORD, # dwDesiredAccess
    W.DWORD, # dwShareMode
    LPSECURITY_ATTRIBUTES, # lpSecurityAttributes
    W.DWORD, # dwCreationDisposition
    W.DWORD, # dwFlagsAndAttributes
    W.HANDLE, # hTemplateFile
]
CreateFile.restype = W.HANDLE

CloseHandle = _kernel32.CloseHandle
CloseHandle.argtypes = [
    W.HANDLE,
]
CloseHandle.restype = W.BOOL
