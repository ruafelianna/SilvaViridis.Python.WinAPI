import ctypes
from ctypes import wintypes

BOOL = wintypes.INT
DWORD = wintypes.DWORD
HGLOBAL = wintypes.HANDLE
PBYTE = ctypes.POINTER(wintypes.BYTE)
PDWORD = ctypes.POINTER(DWORD)
UINT = ctypes.c_uint

FALSE = 0
TRUE = 1
