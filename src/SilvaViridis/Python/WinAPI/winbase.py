import ctypes

from .basetsd import SIZE_T
from .minwindef import HGLOBAL, UINT

kernel32 = ctypes.windll.LoadLibrary("Kernel32.dll")

GMEM_FIXED = 0x0000
GMEM_ZEROINIT = 0x0040

GPTR = GMEM_FIXED | GMEM_ZEROINIT

GlobalAlloc = kernel32.GlobalAlloc
GlobalAlloc.argtypes = [
    UINT, # uFlags
    SIZE_T, # dwBytes
]
GlobalAlloc.restype = HGLOBAL

GlobalFree = kernel32.GlobalFree
GlobalFree.argtypes = [
    HGLOBAL, # hMem
]
GlobalFree.restype = HGLOBAL
