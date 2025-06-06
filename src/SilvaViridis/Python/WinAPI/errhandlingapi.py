import ctypes

from .minwindef import DWORD

kernel32 = ctypes.windll.LoadLibrary("Kernel32.dll")

GetLastError = kernel32.GetLastError
GetLastError.argtypes = []
GetLastError.restype = DWORD
