import ctypes as C
import ctypes.wintypes as W

from .Exceptions import MemAllocError, raise_ex
from .Memory import alloc, free
from .Types import (
    FALSE,
    CtlCodes,
    USBUserRequestCodes,
    ControllerInfo,
    USBControllerFlavors,
    HCFeatureFlags,
    USBHubNodeInformation,
    USBMIParentNodeInformation,
    USBHubNodeTypes,
)
from .Utils import ptr_to_str

from ..kernel32 import (
    DeviceIoControl,
)
from ..types import (
    USBUSER_CONTROLLER_INFO_0,
    USB_HCD_DRIVERKEY_NAME,
    USB_ROOT_HUB_NAME,
    USB_NODE_INFORMATION,
)

def ioctl_get_hcd_driver_key_name(
    fd : W.HANDLE,
) -> str:
    driver_key_name = USB_HCD_DRIVERKEY_NAME()
    nBytes = W.ULONG(0)

    success = DeviceIoControl(
        fd,
        CtlCodes.GET_HCD_DRIVERKEY_NAME.value,
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
        CtlCodes.GET_HCD_DRIVERKEY_NAME.value,
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
) -> ControllerInfo:
    controller_info = USBUSER_CONTROLLER_INFO_0()
    controller_info.Header.UsbUserRequest = USBUserRequestCodes.GET_CONTROLLER_INFO_0.value
    controller_info.Header.RequestBufferLength = C.sizeof(controller_info)
    nBytes = W.DWORD(0)

    success = DeviceIoControl(
        fd,
        CtlCodes.USB_USER_REQUEST.value,
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
        controller_flavor = USBControllerFlavors(controller_info.Info0.ControllerFlavor),
        hc_feature_flags = HCFeatureFlags(controller_info.Info0.HcFeatureFlags),
    )

def ioctl_get_root_hub_name(
    fd : W.HANDLE,
) -> str:
    root_hub_name = USB_ROOT_HUB_NAME()
    nBytes = W.DWORD(0)

    success = DeviceIoControl(
        fd,
        CtlCodes.USB_GET_ROOT_HUB_NAME.value,
        None,
        0,
        C.byref(root_hub_name),
        C.sizeof(root_hub_name),
        C.byref(nBytes),
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    nBytes = root_hub_name.ActualLength

    root_hub_name_ptr = alloc(nBytes)

    if root_hub_name_ptr is None:
        raise MemAllocError()

    success = DeviceIoControl(
        fd,
        CtlCodes.USB_GET_ROOT_HUB_NAME.value,
        None,
        0,
        root_hub_name_ptr,
        nBytes,
        None,
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    not_str_len = C.sizeof(W.ULONG)

    root_hub_name = ptr_to_str(
        int(root_hub_name_ptr) + not_str_len,
        nBytes - not_str_len,
    )

    free(root_hub_name_ptr)

    return root_hub_name

def ioctl_get_usb_node_info(
    fd : W.HANDLE,
) -> USBHubNodeInformation | USBMIParentNodeInformation:
    node_info = USB_NODE_INFORMATION()
    nBytes = W.DWORD(0)

    success = DeviceIoControl(
        fd,
        CtlCodes.USB_GET_NODE_INFORMATION.value,
        C.byref(node_info),
        C.sizeof(USB_NODE_INFORMATION),
        C.byref(node_info),
        C.sizeof(USB_NODE_INFORMATION),
        C.byref(nBytes),
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    if node_info.NodeType == USBHubNodeTypes.UsbHub.value:
        hub_info = node_info.u.HubInformation
        return USBHubNodeInformation(
            is_bus_powered = bool(hub_info.HubIsBusPowered),
            number_of_ports = hub_info.HubDescriptor.bNumberOfPorts,
            hub_characteristics = hub_info.HubDescriptor.wHubCharacteristics,
            power_on_to_power_good = hub_info.HubDescriptor.bPowerOnToPowerGood,
            hub_control_current = hub_info.HubDescriptor.bHubControlCurrent,
            remove_and_power_mask = list(hub_info.HubDescriptor.bRemoveAndPowerMask),
        )
    elif node_info.NodeType == USBHubNodeTypes.UsbMIParent.value:
        mi_info = node_info.u.MiParentInformation
        return USBMIParentNodeInformation(
            number_of_interfaces = mi_info.NumberOfInterfaces,
        )
    else:
        raise NotImplementedError()
