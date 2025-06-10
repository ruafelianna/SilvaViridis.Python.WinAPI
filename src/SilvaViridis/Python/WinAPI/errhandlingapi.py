import ctypes as C

from .minwindef import DWORD

kernel32 = C.windll.LoadLibrary("Kernel32.dll")

GetLastError = kernel32.GetLastError
GetLastError.argtypes = []
GetLastError.restype = DWORD
