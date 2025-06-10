import ctypes as C
import ctypes.wintypes as W

BOOL = W.INT
DWORD = W.DWORD
HGLOBAL = W.HANDLE
PBYTE = C.POINTER(W.BYTE)
PDWORD = C.POINTER(DWORD)
UINT = C.c_uint

FALSE = 0
TRUE = 1
