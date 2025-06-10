import ctypes as C

_kernel32 = C.windll.LoadLibrary("Kernel32.dll")

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
