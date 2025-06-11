from __future__ import annotations

import ctypes as C

from dataclasses import dataclass
from enum import Enum, Flag
from uuid import UUID

from .Utils import (
    uuid_to_guid,
    guid_to_uuid,
)

from ..types import (
    SP_DEVINFO_DATA,
    SP_DEVICE_INTERFACE_DATA,
)

INVALID_HANDLE_VALUE = -1

TRUE = 1
FALSE = 0

class ValueTypes(Enum):
    NONE = 0
    SZ = 1
    EXPAND_SZ = 2
    BINARY = 3
    DWORD = 4
    DWORD_LITTLE_ENDIAN = 4
    DWORD_BIG_ENDIAN = 5
    LINK = 6
    MULTI_SZ = 7
    RESOURCE_LIST = 8
    FULL_RESOURCE_DESCRIPTOR = 9
    RESOURCE_REQUIREMENTS_LIST = 10
    QWORD = 11
    QWORD_LITTLE_ENDIAN = 11

class GenericRights(Flag):
    READ = 0x80000000
    WRITE = 0x40000000
    EXECUTE = 0x20000000
    ALL = 0x10000000

class ShareModes(Flag):
    READ = 0x00000001
    WRITE = 0x00000002
    DELETE = 0x00000004

class CreationModes(Enum):
    CREATE_NEW = 1
    CREATE_ALWAYS = 2
    OPEN_EXISTING = 3
    OPEN_ALWAYS = 4
    TRUNCATE_EXISTING = 5

class DeviceTypes(Enum):
    BEEP = 0x00000001
    CD_ROM = 0x00000002
    CD_ROM_FILE_SYSTEM = 0x00000003
    CONTROLLER = 0x00000004
    DATALINK = 0x00000005
    DFS = 0x00000006
    DISK = 0x00000007
    DISK_FILE_SYSTEM = 0x00000008
    FILE_SYSTEM = 0x00000009
    INPORT_PORT = 0x0000000a
    KEYBOARD = 0x0000000b
    MAILSLOT = 0x0000000c
    MIDI_IN = 0x0000000d
    MIDI_OUT = 0x0000000e
    MOUSE = 0x0000000f
    MULTI_UNC_PROVIDER = 0x00000010
    NAMED_PIPE = 0x00000011
    NETWORK = 0x00000012
    NETWORK_BROWSER = 0x00000013
    NETWORK_FILE_SYSTEM = 0x00000014
    NULL = 0x00000015
    PARALLEL_PORT = 0x00000016
    PHYSICAL_NETCARD = 0x00000017
    PRINTER = 0x00000018
    SCANNER = 0x00000019
    SERIAL_MOUSE_PORT = 0x0000001a
    SERIAL_PORT = 0x0000001b
    SCREEN = 0x0000001c
    SOUND = 0x0000001d
    STREAMS = 0x0000001e
    TAPE = 0x0000001f
    TAPE_FILE_SYSTEM = 0x00000020
    TRANSPORT = 0x00000021
    UNKNOWN = 0x00000022
    USB = UNKNOWN
    VIDEO = 0x00000023
    VIRTUAL_DISK = 0x00000024
    WAVE_IN = 0x00000025
    WAVE_OUT = 0x00000026
    PORT_8042 = 0x00000027
    NETWORK_REDIRECTOR = 0x00000028
    BATTERY = 0x00000029
    BUS_EXTENDER = 0x0000002a
    MODEM = 0x0000002b
    VDM = 0x0000002c
    MASS_STORAGE = 0x0000002d
    SMB = 0x0000002e
    KS = 0x0000002f
    CHANGER = 0x00000030
    SMARTCARD = 0x00000031
    ACPI = 0x00000032
    DVD = 0x00000033
    FULLSCREEN_VIDEO = 0x00000034
    DFS_FILE_SYSTEM = 0x00000035
    DFS_VOLUME = 0x00000036
    SERENUM = 0x00000037
    TERMSRV = 0x00000038
    KSEC = 0x00000039
    FIPS = 0x0000003A
    INFINIBAND = 0x0000003B
    VMBUS = 0x0000003E
    CRYPT_PROVIDER = 0x0000003F
    WPD = 0x00000040
    BLUETOOTH = 0x00000041
    MT_COMPOSITE = 0x00000042
    MT_TRANSPORT = 0x00000043
    BIOMETRIC = 0x00000044
    PMI = 0x00000045
    EHSTOR = 0x00000046
    DEVAPI = 0x00000047
    GPIO = 0x00000048
    USBEX = 0x00000049
    CONSOLE = 0x00000050
    NFP = 0x00000051
    SYSENV = 0x00000052
    VIRTUAL_BLOCK = 0x00000053
    POINT_OF_SERVICE = 0x00000054
    STORAGE_REPLICATION = 0x00000055
    TRUST_ENV = 0x00000056
    UCM = 0x00000057
    UCMTCPCI = 0x00000058
    PERSISTENT_MEMORY = 0x00000059
    NVDIMM = 0x0000005a
    HOLOGRAPHIC = 0x0000005b
    SDFXHCI = 0x0000005c
    UCMUCSI = 0x0000005d
    PRM = 0x0000005e
    EVENT_COLLECTOR = 0x0000005f
    USB4 = 0x00000060
    SOUNDWIRE = 0x00000061

class BufferPassMethods(Enum):
    BUFFERED = 0
    IN_DIRECT = 1
    OUT_DIRECT = 2
    NEITHER = 3

class FileAccesses(Enum):
    ANY = 0
    SPECIAL = ANY
    READ = 0x0001
    WRITE = 0x0002

class UserModeIOCTLFunctionCodes(Enum):
    HCD_GET_STATS_1 = 255
    HCD_DIAGNOSTIC_MODE_ON = 256
    HCD_DIAGNOSTIC_MODE_OFF = 257
    HCD_GET_ROOT_HUB_NAME = 258
    HCD_GET_DRIVERKEY_NAME = 265
    HCD_GET_STATS_2 = 266
    HCD_DISABLE_PORT = 268
    HCD_ENABLE_PORT = 269
    HCD_USER_REQUEST = 270
    HCD_TRACE_READ_REQUEST = 275
    USB_GET_NODE_INFORMATION = 258
    USB_GET_NODE_CONNECTION_INFORMATION = 259
    USB_GET_DESCRIPTOR_FROM_NODE_CONNECTION = 260
    USB_GET_NODE_CONNECTION_NAME = 261
    USB_DIAG_IGNORE_HUBS_ON = 262
    USB_DIAG_IGNORE_HUBS_OFF = 263
    USB_GET_NODE_CONNECTION_DRIVERKEY_NAME = 264
    USB_GET_HUB_CAPABILITIES = 271
    USB_GET_NODE_CONNECTION_ATTRIBUTES = 272
    USB_HUB_CYCLE_PORT = 273
    USB_GET_NODE_CONNECTION_INFORMATION_EX = 274
    USB_RESET_HUB = 275
    USB_GET_HUB_CAPABILITIES_EX = 276
    USB_GET_HUB_INFORMATION_EX = 277
    USB_GET_PORT_CONNECTOR_PROPERTIES = 278
    USB_GET_NODE_CONNECTION_INFORMATION_EX_V2 = 279
    USB_GET_TRANSPORT_CHARACTERISTICS = 281
    USB_REGISTER_FOR_TRANSPORT_CHARACTERISTICS_CHANGE = 282
    USB_NOTIFY_ON_TRANSPORT_CHARACTERISTICS_CHANGE = 283
    USB_UNREGISTER_FOR_TRANSPORT_CHARACTERISTICS_CHANGE = 284
    USB_START_TRACKING_FOR_TIME_SYNC = 285
    USB_GET_FRAME_NUMBER_AND_QPC_FOR_TIME_SYNC = 286
    USB_STOP_TRACKING_FOR_TIME_SYNC = 287
    USB_GET_DEVICE_CHARACTERISTICS = 288

def ctl_code(
    dev_type : DeviceTypes,
    function : UserModeIOCTLFunctionCodes,
    method : BufferPassMethods,
    access : FileAccesses,
) -> int:
    return (dev_type.value << 16) \
        | (access.value << 14) \
        | (function.value << 2) \
        | method.value

def usb_ctl(
    func : UserModeIOCTLFunctionCodes,
) -> int:
    return ctl_code(
        DeviceTypes.USB,
        func,
        BufferPassMethods.BUFFERED,
        FileAccesses.ANY,
    )

class CtlCodes(Enum):
    GET_HCD_DRIVERKEY_NAME = usb_ctl(UserModeIOCTLFunctionCodes.HCD_GET_DRIVERKEY_NAME,)
    USB_USER_REQUEST = usb_ctl(UserModeIOCTLFunctionCodes.HCD_USER_REQUEST)

class USBUserRequestCodes(Enum):
    GET_CONTROLLER_INFO_0 = 0x00000001
    GET_CONTROLLER_DRIVER_KEY = 0x00000002
    PASS_THRU = 0x00000003
    GET_POWER_STATE_MAP = 0x00000004
    GET_BANDWIDTH_INFORMATION = 0x00000005
    GET_BUS_STATISTICS_0 = 0x00000006
    GET_ROOTHUB_SYMBOLIC_NAME = 0x00000007
    GET_USB_DRIVER_VERSION = 0x00000008
    GET_USB2_HW_VERSION = 0x00000009
    USB_REFRESH_HCT_REG = 0x0000000a
    OP_SEND_ONE_PACKET = 0x10000001
    OP_RAW_RESET_PORT = 0x20000001
    OP_OPEN_RAW_DEVICE = 0x20000002
    OP_CLOSE_RAW_DEVICE = 0x20000003
    OP_SEND_RAW_COMMAND = 0x20000004
    SET_ROOTPORT_FEATURE = 0x20000005
    CLEAR_ROOTPORT_FEATURE = 0x20000006
    GET_ROOTPORT_STATUS = 0x20000007
    INVALID_REQUEST = 0xFFFFFFF0
    OP_MASK_DEVONLY_API = 0x10000000
    OP_MASK_HCTEST_API = 0x20000000

class HCFeatureFlags(Flag):
    PORT_POWER_SWITCHING = 0x00000001
    SEL_SUSPEND = 0x00000002
    LEGACY_BIOS = 0x00000004
    TIME_SYNC_API = 0x00000008

class USBControllerFlavors(Enum):
    USB_HcGeneric = 0
    OHCI_Generic = 100
    OHCI_Hydra = 101
    OHCI_NEC = 102
    UHCI_Generic = 200
    UHCI_Piix4 = 201
    UHCI_Piix3 = 202
    UHCI_Ich2 = 203
    UHCI_Reserved204 = 204
    UHCI_Ich1 = 205
    UHCI_Ich3m = 206
    UHCI_Ich4 = 207
    UHCI_Ich5 = 208
    UHCI_Ich6 = 209
    UHCI_Intel = 249
    UHCI_VIA = 250
    UHCI_VIA_x01 = 251
    UHCI_VIA_x02 = 252
    UHCI_VIA_x03 = 253
    UHCI_VIA_x04 = 254
    UHCI_VIA_x0E_FIFO = 264
    EHCI_Generic = 1000
    EHCI_NEC = 2000
    EHCI_Lucent = 3000
    EHCI_NVIDIA_Tegra2 = 4000
    EHCI_NVIDIA_Tegra3 = 4001
    EHCI_Intel_Medfield = 5001

class USBUserErrorCodes(Enum):
    Success = 0
    NotSupported = 1
    InvalidRequestCode = 2
    FeatureDisabled = 3
    InvalidHeaderParameter = 4
    InvalidParameter = 5
    MiniportError = 6
    BufferTooSmall = 7
    ErrorNotMapped = 8
    DeviceNotStarted = 9
    NoDeviceConnected = 10

@dataclass
class ControllerInfo:
    pci_vendor_id : int
    pci_device_id : int
    pci_revision : int
    number_of_root_ports : int
    controller_flavor : USBControllerFlavors
    hc_feature_flags : HCFeatureFlags

class GMems(Flag):
    FIXED = 0x0000
    MOVEABLE = 0x0002
    NOCOMPACT = 0x0010
    NODISCARD = 0x0020
    ZEROINIT = 0x0040
    MODIFY = 0x0080
    DISCARDABLE = 0x0100
    NOT_BANKED = 0x1000
    SHARE = 0x2000
    DDESHARE = 0x2000
    NOTIFY = 0x4000
    LOWER = NOT_BANKED
    VALID_FLAGS = 0x7F72
    INVALID_HANDLE = 0x8000

GHND = GMems.MOVEABLE | GMems.ZEROINIT
GPTR = GMems.FIXED | GMems.ZEROINIT

class USBDevInterfaceGuids(Enum):
    DEVICE = UUID("a5dcbf10-6530-11d2-901f-00c04fb951ed")
    HUB = UUID("f18a0e88-c30c-11d0-8815-00a0c906bed8")
    HOST_CONTROLLER = UUID("3abf6f2d-71c4-462a-8a92-1e6861e6af27")

class IncludedInfoFlags(Flag):
    DEFAULT = 0x00000001
    PRESENT = 0x00000002
    ALLCLASSES = 0x00000004
    PROFILE = 0x00000008
    DEVICEINTERFACE = 0x00000010

class DevProperties(Enum):
	DEVICEDESC = 0x00000000
	HARDWAREID = 0x00000001
	COMPATIBLEIDS = 0x00000002
	UNUSED0 = 0x00000003
	SERVICE = 0x00000004
	UNUSED1 = 0x00000005
	UNUSED2 = 0x00000006
	CLASS = 0x00000007
	CLASSGUID = 0x00000008
	DRIVER = 0x00000009
	CONFIGFLAGS = 0x0000000a
	MFG = 0x0000000b
	FRIENDLYNAME = 0x0000000c
	LOCATION_INFORMATION = 0x0000000d
	PHYSICAL_DEVICE_OBJECT_NAME = 0x0000000e
	CAPABILITIES = 0x0000000f
	UI_NUMBER = 0x00000010
	UPPERFILTERS = 0x00000011
	LOWERFILTERS = 0x00000012
	BUSTYPEGUID = 0x00000013
	LEGACYBUSTYPE = 0x00000014
	BUSNUMBER = 0x00000015
	ENUMERATOR_NAME = 0x00000016
	SECURITY = 0x00000017
	SECURITY_SDS = 0x00000018
	DEVTYPE = 0x00000019
	EXCLUSIVE = 0x0000001a
	CHARACTERISTICS = 0x0000001b
	ADDRESS = 0x0000001c
	UI_NUMBER_DESC_FORMAT = 0X0000001d
	DEVICE_POWER_DATA = 0x0000001e
	REMOVAL_POLICY = 0x0000001f
	REMOVAL_POLICY_HW_DEFAULT = 0x00000020
	REMOVAL_POLICY_OVERRIDE = 0x00000021
	INSTALL_STATE = 0x00000022
	LOCATION_PATHS = 0x00000023
	BASE_CONTAINERID = 0x00000024
	MAXIMUM_PROPERTY = 0x00000025

class DevInterfaceFlags(Flag):
    ACTIVE = 0x00000001
    DEFAULT = 0x00000002
    REMOVED = 0x00000004

@dataclass
class DevInfoData:
    class_guid : UUID
    dev_inst_handle : int
    reserved : C.c_void_p

    def to_internal(self) -> SP_DEVINFO_DATA:
        data = SP_DEVINFO_DATA.create()
        data.ClassGuid = uuid_to_guid(self.class_guid)
        data.DevInst = self.dev_inst_handle
        data.Reserved = self.reserved
        return data

    @staticmethod
    def create(data : SP_DEVINFO_DATA) -> DevInfoData:
        return DevInfoData(
            class_guid = guid_to_uuid(data.ClassGuid),
            dev_inst_handle = data.DevInst,
            reserved = data.Reserved,
        )

@dataclass
class DevInterfaceData:
    interface_class_guid : UUID
    flags : DevInterfaceFlags
    reserved : C.c_void_p

    def to_internal(self) -> SP_DEVICE_INTERFACE_DATA:
        data = SP_DEVICE_INTERFACE_DATA.create()
        data.InterfaceClassGuid = uuid_to_guid(self.interface_class_guid)
        data.Flags = self.flags.value
        data.Reserved = self.reserved
        return data

    @staticmethod
    def create(data : SP_DEVICE_INTERFACE_DATA) -> DevInterfaceData:
        return DevInterfaceData(
            interface_class_guid = guid_to_uuid(data.InterfaceClassGuid),
            flags = DevInterfaceFlags(data.Flags),
            reserved = data.Reserved,
        )
