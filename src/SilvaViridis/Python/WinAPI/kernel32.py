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

class OVERLAPPED_DUMMYSTRUCT(C.Structure):
    _fields_ = [
        ("Offset", W.DWORD),
        ("OffsetHigh", W.DWORD),
    ]

class OVERLAPPED_DUMMYUNION(C.Union):
    _fields_ = [
        ("DUMMYSTRUCTNAME", OVERLAPPED_DUMMYSTRUCT),
        ("Pointer", C.c_void_p),
    ]

class OVERLAPPED(C.Structure):
    _fields_ = [
        ("Internal", C.c_void_p),
        ("InternalHigh", C.c_void_p),
        ("DUMMYUNIONNAME", OVERLAPPED_DUMMYUNION),
        ("hEvent", W.HANDLE),
    ]

LPOVERLAPPED = C.POINTER(OVERLAPPED)

class USB_HCD_DRIVERKEY_NAME(C.Structure):
    _fields_ = [
        ("ActualLength", W.ULONG),
        ("DriverKeyName", W.WCHAR * 1),
    ]

PUSB_HCD_DRIVERKEY_NAME = C.POINTER(USB_HCD_DRIVERKEY_NAME)

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

DeviceIoControl = _kernel32.DeviceIoControl
DeviceIoControl.argtypes = [
    W.HANDLE, # hDevice
    W.DWORD, # dwIoControlCode
    W.LPVOID, # lpInBuffer
    W.DWORD, # nInBufferSize
    W.LPVOID, # lpOutBuffer
    W.DWORD, # nOutBufferSize
    W.LPDWORD, # lpBytesReturned
    LPOVERLAPPED, # lpOverlapped
]
DeviceIoControl.restype = W.BOOL
