import ctypes as C
import ctypes.wintypes as W

_advapi32 = C.windll.LoadLibrary("Advapi32.dll")

RegCloseKey = _advapi32.RegCloseKey
RegCloseKey.argtypes = [
    W.HKEY, # hKey
]
RegCloseKey.restype = W.LONG
