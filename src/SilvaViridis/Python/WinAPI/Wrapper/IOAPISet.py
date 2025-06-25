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
    USBHubTypes,
    USBHubInformation,
    USB30HubInformation,
    USBHubCapabilities,
    USBConnectorProps,
    USBNodeConnectionInfoExV2,
    USBNodeConnectionInfoEx,
    USBConnectionStatuses,
    USBDeviceSpeeds,
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
    USB_HUB_INFORMATION_EX,
    USB_HUB_CAPABILITIES_EX,
    USB_PORT_CONNECTOR_PROPERTIES,
    USB_PORT_PROPERTIES,
    PUSB_PORT_CONNECTOR_PROPERTIES,
    USB_NODE_CONNECTION_INFORMATION_EX_V2,
    USB_NODE_CONNECTION_INFORMATION_EX,
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

def ioctl_get_usb_hub_extra_info(
    fd : W.HANDLE,
) -> USBHubInformation | USB30HubInformation:
    hub_descriptor = USB_HUB_INFORMATION_EX()
    nBytes = W.DWORD(0)

    success = DeviceIoControl(
        fd,
        CtlCodes.USB_GET_HUB_INFORMATION_EX.value,
        C.byref(hub_descriptor),
        C.sizeof(USB_HUB_INFORMATION_EX),
        C.byref(hub_descriptor),
        C.sizeof(USB_HUB_INFORMATION_EX),
        C.byref(nBytes),
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    if hub_descriptor.HubType == USBHubTypes.Usb30Hub.value:
        hub_info = hub_descriptor.u.Usb30HubDescriptor
        return USB30HubInformation(
            highest_port_number = hub_descriptor.HighestPortNumber,
            number_of_ports = hub_info.bNumberOfPorts,
            hub_characteristics = hub_info.wHubCharacteristics,
            power_on_to_power_good = hub_info.bPowerOnToPowerGood,
            hub_control_current = hub_info.bHubControlCurrent,
            hub_packet_header_decode_latency = hub_info.bHubHdrDecLat,
            hub_delay = hub_info.wHubDelay,
            device_removable = hub_info.DeviceRemovable,
        )
    elif hub_descriptor.HubType in [USBHubTypes.UsbRootHub.value, USBHubTypes.Usb20Hub.value]:
        hub_info = hub_descriptor.u.UsbHubDescriptor
        return USBHubInformation(
            highest_port_number = hub_descriptor.HighestPortNumber,
            number_of_ports = hub_info.bNumberOfPorts,
            hub_characteristics = hub_info.wHubCharacteristics,
            power_on_to_power_good = hub_info.bPowerOnToPowerGood,
            hub_control_current = hub_info.bHubControlCurrent,
            remove_and_power_mask = list(hub_info.bRemoveAndPowerMask),
        )
    else:
        raise NotImplementedError()

def ioctl_get_usb_hub_capabilities_ex(
    fd : W.HANDLE,
) -> USBHubCapabilities:
    capabilities = USB_HUB_CAPABILITIES_EX()
    nBytes = W.DWORD(0)

    success = DeviceIoControl(
        fd,
        CtlCodes.USB_GET_HUB_CAPABILITIES_EX.value,
        C.byref(capabilities),
        C.sizeof(USB_HUB_INFORMATION_EX),
        C.byref(capabilities),
        C.sizeof(USB_HUB_INFORMATION_EX),
        C.byref(nBytes),
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    return USBHubCapabilities(
        is_high_speed_capable = bool(capabilities.CapabilityFlags.bits.HubIsHighSpeedCapable),
        is_high_speed = bool(capabilities.CapabilityFlags.bits.HubIsHighSpeed),
        is_multi_tt_capable = bool(capabilities.CapabilityFlags.bits.HubIsMultiTtCapable),
        is_multi_tt = bool(capabilities.CapabilityFlags.bits.HubIsMultiTt),
        is_root = bool(capabilities.CapabilityFlags.bits.HubIsRoot),
        is_armed_wake_on_connect = bool(capabilities.CapabilityFlags.bits.HubIsArmedWakeOnConnect),
        is_bus_powered = bool(capabilities.CapabilityFlags.bits.HubIsBusPowered),
    )

def ioctl_get_usb_port_connector_props(
    fd : W.HANDLE,
    connection_index : int,
) -> USBConnectorProps:
    props = USB_PORT_CONNECTOR_PROPERTIES()
    nBytes = W.DWORD(0)

    props.ConnectionIndex = connection_index + 1

    success = DeviceIoControl(
        fd,
        CtlCodes.USB_GET_PORT_CONNECTOR_PROPERTIES.value,
        C.byref(props),
        C.sizeof(props),
        C.byref(props),
        C.sizeof(props),
        C.byref(nBytes),
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    nBytes = props.ActualLength

    props_ptr = alloc(nBytes)

    if props_ptr is None:
        raise MemAllocError()

    p = C.cast(props_ptr, PUSB_PORT_CONNECTOR_PROPERTIES)[0]
    p.ConnectionIndex = connection_index + 1

    success = DeviceIoControl(
        fd,
        CtlCodes.USB_GET_PORT_CONNECTOR_PROPERTIES.value,
        props_ptr,
        nBytes,
        props_ptr,
        nBytes,
        None,
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    not_str_len = C.sizeof(W.ULONG) * 2 + C.sizeof(W.USHORT) * 2 + C.sizeof(USB_PORT_PROPERTIES)

    result = USBConnectorProps(
        connection_index = props.ConnectionIndex,
        companion_index = props.CompanionIndex,
        companion_port_number = props.CompanionPortNumber,
        companion_hub_symlink = ptr_to_str(
            int(props_ptr) + not_str_len,
            nBytes - not_str_len,
        ),
        port_is_user_connectable = bool(props.UsbPortProperties.bits.PortIsUserConnectable),
        port_is_debug_capable = bool(props.UsbPortProperties.bits.PortIsDebugCapable),
        port_has_multiple_companions = bool(props.UsbPortProperties.bits.PortHasMultipleCompanions),
        port_connector_is_type_c = bool(props.UsbPortProperties.bits.PortConnectorIsTypeC),
    )

    free(props_ptr)

    return result

def ioctl_get_usb_node_connection_info_ex_v2(
    fd : W.HANDLE,
    connection_index : int,
) -> USBNodeConnectionInfoExV2:
    info = USB_NODE_CONNECTION_INFORMATION_EX_V2()
    nBytes = W.DWORD(0)

    info.ConnectionIndex = connection_index + 1
    info.Length = C.sizeof(USB_NODE_CONNECTION_INFORMATION_EX_V2)
    info.SupportedUsbProtocols.bits.Usb300 = 1

    success = DeviceIoControl(
        fd,
        CtlCodes.USB_GET_NODE_CONNECTION_INFORMATION_EX_V2.value,
        C.byref(info),
        C.sizeof(USB_NODE_CONNECTION_INFORMATION_EX_V2),
        C.byref(info),
        C.sizeof(USB_NODE_CONNECTION_INFORMATION_EX_V2),
        C.byref(nBytes),
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    return USBNodeConnectionInfoExV2(
        connection_index = info.ConnectionIndex,
        is_usb_110_supported = bool(info.SupportedUsbProtocols.bits.Usb110),
        is_usb_200_supported = bool(info.SupportedUsbProtocols.bits.Usb200),
        is_usb_300_supported = bool(info.SupportedUsbProtocols.bits.Usb300),
        is_device_operating_at_super_speed_or_higher = bool(info.Flags.bits.DeviceIsOperatingAtSuperSpeedOrHigher),
        is_device_super_speed_capable_or_higher = bool(info.Flags.bits.DeviceIsSuperSpeedCapableOrHigher),
        is_device_operating_at_super_speed_plus_or_higher = bool(info.Flags.bits.DeviceIsOperatingAtSuperSpeedPlusOrHigher),
        is_device_super_speed_plus_capable_or_higher = bool(info.Flags.bits.DeviceIsSuperSpeedPlusCapableOrHigher),
    )

def ioctl_get_usb_node_connection_info_ex(
    fd : W.HANDLE,
    connection_index : int,
) -> USBNodeConnectionInfoEx:
    info = USB_NODE_CONNECTION_INFORMATION_EX()
    nBytes = W.DWORD(0)

    info.ConnectionIndex = connection_index + 1

    success = DeviceIoControl(
        fd,
        CtlCodes.USB_GET_NODE_CONNECTION_INFORMATION_EX.value,
        C.byref(info),
        C.sizeof(USB_NODE_CONNECTION_INFORMATION_EX),
        C.byref(info),
        C.sizeof(USB_NODE_CONNECTION_INFORMATION_EX),
        C.byref(nBytes),
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    return USBNodeConnectionInfoEx(
        connection_index = info.ConnectionIndex,
        speed = USBDeviceSpeeds(info.Speed),
        device_is_hub = bool(info.DeviceIsHub),
        device_address = info.DeviceAddress,
        connection_status = USBConnectionStatuses(info.ConnectionStatus),
    )
