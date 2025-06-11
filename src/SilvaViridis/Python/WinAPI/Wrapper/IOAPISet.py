import ctypes as C
import ctypes.wintypes as W

from dataclasses import dataclass
from enum import Enum, Flag

from .Consts import FALSE
from .Exceptions import MemAllocError, raise_ex
from .Memory import alloc, free
from .IO import CtlCodes
from .Utils import ptr_to_str

from ..kernel32 import (
    USB_HCD_DRIVERKEY_NAME,
    DeviceIoControl,
)
from ..types import (
    USBUSER_CONTROLLER_INFO_0,
)

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

class USBControllerFlavor(Enum):
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

class USBUserErrorCode(Enum):
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
    controller_flavor : USBControllerFlavor
    hc_feature_flags : HCFeatureFlags

def ioctl_get_hcd_driver_key_name(
    fd : W.HANDLE,
):
    driver_key_name = USB_HCD_DRIVERKEY_NAME()
    nBytes = W.ULONG(0)

    success = DeviceIoControl(
        fd,
        CtlCodes.IOCTL_GET_HCD_DRIVERKEY_NAME.value,
        C.byref(driver_key_name),
        C.sizeof(driver_key_name),
        C.byref(driver_key_name),
        C.sizeof(driver_key_name),
        C.byref(nBytes),
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    nBytes = driver_key_name.ActualLength

    driver_key_name_ptr = alloc(nBytes)

    if driver_key_name_ptr is None:
        raise MemAllocError()

    success = DeviceIoControl(
        fd,
        CtlCodes.IOCTL_GET_HCD_DRIVERKEY_NAME.value,
        driver_key_name_ptr,
        nBytes,
        driver_key_name_ptr,
        nBytes,
        None,
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    not_str_len = C.sizeof(W.ULONG)

    driver_key_name = ptr_to_str(
        int(driver_key_name_ptr) + not_str_len,
        nBytes - not_str_len,
    )

    free(driver_key_name_ptr)

    return driver_key_name

def ioctl_get_usb_controller_info(
    fd : W.HANDLE,
):
    controller_info = USBUSER_CONTROLLER_INFO_0()
    controller_info.Header.UsbUserRequest = USBUserRequestCodes.GET_CONTROLLER_INFO_0.value
    controller_info.Header.RequestBufferLength = C.sizeof(controller_info)
    nBytes = W.DWORD(0)

    success = DeviceIoControl(
        fd,
        CtlCodes.IOCTL_USB_USER_REQUEST.value,
        C.byref(controller_info),
        C.sizeof(controller_info),
        C.byref(controller_info),
        C.sizeof(controller_info),
        C.byref(nBytes),
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    return ControllerInfo(
        pci_vendor_id = controller_info.Info0.PciVendorId,
        pci_device_id = controller_info.Info0.PciDeviceId,
        pci_revision = controller_info.Info0.PciRevision,
        number_of_root_ports = controller_info.Info0.NumberOfRootPorts,
        controller_flavor = USBControllerFlavor(controller_info.Info0.ControllerFlavor),
        hc_feature_flags = HCFeatureFlags(controller_info.Info0.HcFeatureFlags),
    )
