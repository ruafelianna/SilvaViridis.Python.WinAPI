import ctypes

from .basetsd import ULONG_PTR
from .guiddef import GUID, LPGUID
from .minwindef import BOOL, DWORD, PBYTE, PDWORD
from .windef import HWND
from .winnt import PCWSTR

setupapi = ctypes.windll.LoadLibrary("SetupAPI.dll")

HDEVINFO = ctypes.c_void_p

DIGCF_PRESENT = 0x00000002
DIGCF_DEVICEINTERFACE = 0x00000010

SPDRP_DEVICEDESC = DWORD(0x00000000)
SPDRP_DRIVER = DWORD(0x00000009)

class SP_DEVINFO_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", DWORD),
        ("ClassGuid", GUID),
        ("DevInst", DWORD),
        ("Reserved", ULONG_PTR),
    ]

PSP_DEVINFO_DATA = ctypes.POINTER(SP_DEVINFO_DATA)

SetupDiEnumDeviceInfo = setupapi.SetupDiEnumDeviceInfo
SetupDiEnumDeviceInfo.argtypes = [
    HDEVINFO, # DeviceInfoSet
    DWORD, # MemberIndex
    PSP_DEVINFO_DATA, # DeviceInfoData
]
SetupDiEnumDeviceInfo.restype = BOOL

SetupDiGetClassDevs = setupapi.SetupDiGetClassDevsW
SetupDiGetClassDevs.argtypes = [
    LPGUID, # ClassGuid
    PCWSTR, # Enumerator
    HWND, # hwndParent
    DWORD, # Flags
]
SetupDiGetClassDevs.restype = HDEVINFO

SetupDiGetDeviceRegistryProperty = setupapi.SetupDiGetDeviceRegistryPropertyW
SetupDiGetDeviceRegistryProperty.argtypes = [
    HDEVINFO, # DeviceInfoSet
    PSP_DEVINFO_DATA, # DeviceInfoData
    DWORD, # Property
    PDWORD, # PropertyRegDataType
    PBYTE, # PropertyBuffer
    DWORD, # PropertyBufferSize
    PDWORD, # RequiredSize
]
SetupDiGetDeviceRegistryProperty.restype = BOOL
