import ctypes as C

kernel32 = C.windll.LoadLibrary("Kernel32.dll")

GlobalAlloc = kernel32.GlobalAlloc
GlobalAlloc.argtypes = [
    C.c_uint, # uFlags
    C.c_size_t, # dwBytes
]
GlobalAlloc.restype = C.c_void_p

GlobalFree = kernel32.GlobalFree
GlobalFree.argtypes = [
    C.c_void_p, # hMem
]
GlobalFree.restype = C.c_void_p
