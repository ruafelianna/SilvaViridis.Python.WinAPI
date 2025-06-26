import ctypes as C
import ctypes.wintypes as W

from collections.abc import Callable

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

def _ioctl[T : C.Structure, O](
    fd : W.HANDLE,
    code : CtlCodes,
    create : Callable[[], T],
    get_result : Callable[[tuple[C.c_void_p, int] | T], O],
    require_alloc : bool = False,
    get_n_bytes : Callable[[T], int] | None = None,
    init_ptr : Callable[[C.c_void_p], None] | None = None,
) -> O:
    data = create()
    n_bytes = W.DWORD(0)

    success = DeviceIoControl(
        fd,
        code.value,
        C.byref(data),
        C.sizeof(data),
        C.byref(data),
        C.sizeof(data),
        C.byref(n_bytes),
        None,
    )

    if success == FALSE:
        raise_ex(C.GetLastError())

    if require_alloc:
        if get_n_bytes is None:
            raise ValueError("Not all required parameters are set")

        n_bytes = get_n_bytes(data)

        data_ptr = alloc(n_bytes)

        if data_ptr is None:
            raise MemAllocError()

        if init_ptr is not None:
            init_ptr(data_ptr)

        success = DeviceIoControl(
            fd,
            code.value,
            data_ptr,
            n_bytes,
            data_ptr,
            n_bytes,
            None,
            None,
        )

        if success == FALSE:
            raise_ex(C.GetLastError())

        result = get_result((data_ptr, n_bytes))

        free(data_ptr)

        return result
    else:
        return get_result(data)

def _extract_str(
    ptr : C.c_void_p,
    n_bytes : int,
    types_to_skip : list[type[C._SimpleCData | C.Structure | C.Union]], # type: ignore
) -> str:
    not_str_len = sum([C.sizeof(t) for t in types_to_skip]) # type: ignore

    return ptr_to_str(
        int(ptr) + not_str_len,
        n_bytes - not_str_len,
    )

def ioctl_get_hcd_driver_key_name(
    fd : W.HANDLE,
) -> str:
    def get_result(
        data : tuple[C.c_void_p, int] | USB_HCD_DRIVERKEY_NAME,
    ) -> str:
        if isinstance(data, tuple):
            ptr, n_bytes = data
            return _extract_str(ptr, n_bytes, [W.ULONG])
        raise NotImplementedError()

    return _ioctl(
        fd,
        CtlCodes.GET_HCD_DRIVERKEY_NAME,
        lambda: USB_HCD_DRIVERKEY_NAME(),
        get_result,
        require_alloc = True,
        get_n_bytes = lambda data: data.ActualLength,
    )

def ioctl_get_usb_controller_info(
    fd : W.HANDLE,
) -> ControllerInfo:
    def create():
        data  = USBUSER_CONTROLLER_INFO_0()
        data.Header.UsbUserRequest = USBUserRequestCodes.GET_CONTROLLER_INFO_0.value
        data.Header.RequestBufferLength = C.sizeof(data)
        return data

    def get_result(
        data : tuple[C.c_void_p, int] | USBUSER_CONTROLLER_INFO_0,
    ) -> ControllerInfo:
        if isinstance(data, tuple):
            raise NotImplementedError()
        info = data.Info0
        return ControllerInfo(
            pci_vendor_id = info.PciVendorId,
            pci_device_id = info.PciDeviceId,
            pci_revision = info.PciRevision,
            number_of_root_ports = info.NumberOfRootPorts,
            controller_flavor = USBControllerFlavors(info.ControllerFlavor),
            hc_feature_flags = HCFeatureFlags(info.HcFeatureFlags),
        )

    return _ioctl(
        fd,
        CtlCodes.USB_USER_REQUEST,
        create,
        get_result,
    )

def ioctl_get_root_hub_name(
    fd : W.HANDLE,
) -> str:
    def get_result(
        data : tuple[C.c_void_p, int] | USB_ROOT_HUB_NAME,
    ) -> str:
        if isinstance(data, tuple):
            ptr, n_bytes = data
            return _extract_str(ptr, n_bytes, [W.ULONG])
        raise NotImplementedError()

    return _ioctl(
        fd,
        CtlCodes.USB_GET_ROOT_HUB_NAME,
        lambda: USB_ROOT_HUB_NAME(),
        get_result,
        require_alloc = True,
        get_n_bytes = lambda data: data.ActualLength,
    )

def ioctl_get_usb_node_info(
    fd : W.HANDLE,
) -> USBHubNodeInformation | USBMIParentNodeInformation:
    def get_result(
        data : tuple[C.c_void_p, int] | USB_NODE_INFORMATION,
    ) -> USBHubNodeInformation | USBMIParentNodeInformation:
        if isinstance(data, tuple):
            raise NotImplementedError()
        if data.NodeType == USBHubNodeTypes.UsbHub.value:
            hub_info = data.u.HubInformation
            return USBHubNodeInformation(
                is_bus_powered = bool(hub_info.HubIsBusPowered),
                number_of_ports = hub_info.HubDescriptor.bNumberOfPorts,
                hub_characteristics = hub_info.HubDescriptor.wHubCharacteristics,
                power_on_to_power_good = hub_info.HubDescriptor.bPowerOnToPowerGood,
                hub_control_current = hub_info.HubDescriptor.bHubControlCurrent,
                remove_and_power_mask = list(hub_info.HubDescriptor.bRemoveAndPowerMask),
            )
        elif data.NodeType == USBHubNodeTypes.UsbMIParent.value:
            mi_info = data.u.MiParentInformation
            return USBMIParentNodeInformation(
                number_of_interfaces = mi_info.NumberOfInterfaces,
            )
        else:
            raise NotImplementedError()

    return _ioctl(
        fd,
        CtlCodes.USB_GET_NODE_INFORMATION,
        lambda: USB_NODE_INFORMATION(),
        get_result,
    )

def ioctl_get_usb_hub_extra_info(
    fd : W.HANDLE,
) -> USBHubInformation | USB30HubInformation:
    def get_result(
        data : tuple[C.c_void_p, int] | USB_HUB_INFORMATION_EX,
    ) -> USB30HubInformation | USBHubInformation:
        if isinstance(data, tuple):
            raise NotImplementedError()
        if data.HubType == USBHubTypes.Usb30Hub.value:
            hub_info = data.u.Usb30HubDescriptor
            return USB30HubInformation(
                highest_port_number = data.HighestPortNumber,
                number_of_ports = hub_info.bNumberOfPorts,
                hub_characteristics = hub_info.wHubCharacteristics,
                power_on_to_power_good = hub_info.bPowerOnToPowerGood,
                hub_control_current = hub_info.bHubControlCurrent,
                hub_packet_header_decode_latency = hub_info.bHubHdrDecLat,
                hub_delay = hub_info.wHubDelay,
                device_removable = hub_info.DeviceRemovable,
            )
        elif data.HubType in [USBHubTypes.UsbRootHub.value, USBHubTypes.Usb20Hub.value]:
            hub_info = data.u.UsbHubDescriptor
            return USBHubInformation(
                highest_port_number = data.HighestPortNumber,
                number_of_ports = hub_info.bNumberOfPorts,
                hub_characteristics = hub_info.wHubCharacteristics,
                power_on_to_power_good = hub_info.bPowerOnToPowerGood,
                hub_control_current = hub_info.bHubControlCurrent,
                remove_and_power_mask = list(hub_info.bRemoveAndPowerMask),
            )
        else:
            raise NotImplementedError()

    return _ioctl(
        fd,
        CtlCodes.USB_GET_HUB_INFORMATION_EX,
        lambda: USB_HUB_INFORMATION_EX(),
        get_result,
    )

def ioctl_get_usb_hub_capabilities_ex(
    fd : W.HANDLE,
) -> USBHubCapabilities:
    def get_result(
        data : tuple[C.c_void_p, int] | USB_HUB_CAPABILITIES_EX,
    ) -> USBHubCapabilities:
        if isinstance(data, tuple):
            raise NotImplementedError()
        bits = data.CapabilityFlags.bits
        return USBHubCapabilities(
            is_high_speed_capable = bool(bits.HubIsHighSpeedCapable),
            is_high_speed = bool(bits.HubIsHighSpeed),
            is_multi_tt_capable = bool(bits.HubIsMultiTtCapable),
            is_multi_tt = bool(bits.HubIsMultiTt),
            is_root = bool(bits.HubIsRoot),
            is_armed_wake_on_connect = bool(bits.HubIsArmedWakeOnConnect),
            is_bus_powered = bool(bits.HubIsBusPowered),
        )

    return _ioctl(
        fd,
        CtlCodes.USB_GET_HUB_CAPABILITIES_EX,
        lambda: USB_HUB_CAPABILITIES_EX(),
        get_result,
    )

def ioctl_get_usb_port_connector_props(
    fd : W.HANDLE,
    connection_index : int,
) -> USBConnectorProps:
    def create():
        data = USB_PORT_CONNECTOR_PROPERTIES()
        data.ConnectionIndex = connection_index + 1
        return data

    def get_result(
        data : tuple[C.c_void_p, int] | USB_PORT_CONNECTOR_PROPERTIES,
    ) -> USBConnectorProps:
        if isinstance(data, tuple):
            ptr, n_bytes = data
            p = C.cast(ptr, PUSB_PORT_CONNECTOR_PROPERTIES)[0]
            port_bits = p.UsbPortProperties.bits
            return USBConnectorProps(
                connection_index = p.ConnectionIndex,
                companion_index = p.CompanionIndex,
                companion_port_number = p.CompanionPortNumber,
                companion_hub_symlink = _extract_str(ptr, n_bytes, [
                    W.ULONG,
                    W.ULONG,
                    W.USHORT,
                    W.USHORT,
                    USB_PORT_PROPERTIES,
                ]),
                port_is_user_connectable = bool(port_bits.PortIsUserConnectable),
                port_is_debug_capable = bool(port_bits.PortIsDebugCapable),
                port_has_multiple_companions = bool(port_bits.PortHasMultipleCompanions),
                port_connector_is_type_c = bool(port_bits.PortConnectorIsTypeC),
            )
        raise NotImplementedError()

    def init_ptr(
        data_ptr : C.c_void_p,
    ):
        p = C.cast(data_ptr, PUSB_PORT_CONNECTOR_PROPERTIES)[0]
        p.ConnectionIndex = connection_index + 1

    return _ioctl(
        fd,
        CtlCodes.USB_GET_PORT_CONNECTOR_PROPERTIES,
        create,
        get_result,
        require_alloc = True,
        get_n_bytes = lambda data: data.ActualLength,
        init_ptr = init_ptr,
    )

def ioctl_get_usb_node_connection_info_ex_v2(
    fd : W.HANDLE,
    connection_index : int,
) -> USBNodeConnectionInfoExV2:
    def create():
        data = USB_NODE_CONNECTION_INFORMATION_EX_V2()
        data.ConnectionIndex = connection_index + 1
        data.Length = C.sizeof(USB_NODE_CONNECTION_INFORMATION_EX_V2)
        data.SupportedUsbProtocols.bits.Usb300 = 1
        return data

    def get_result(
        data : tuple[C.c_void_p, int] | USB_NODE_CONNECTION_INFORMATION_EX_V2,
    ) -> USBNodeConnectionInfoExV2:
        if isinstance(data, tuple):
            raise NotImplementedError()
        sbits = data.SupportedUsbProtocols.bits
        fbits = data.Flags.bits
        return USBNodeConnectionInfoExV2(
            connection_index = data.ConnectionIndex,
            is_usb_110_supported = bool(sbits.Usb110),
            is_usb_200_supported = bool(sbits.Usb200),
            is_usb_300_supported = bool(sbits.Usb300),
            is_device_operating_at_super_speed_or_higher = bool(fbits.DeviceIsOperatingAtSuperSpeedOrHigher),
            is_device_super_speed_capable_or_higher = bool(fbits.DeviceIsSuperSpeedCapableOrHigher),
            is_device_operating_at_super_speed_plus_or_higher = bool(fbits.DeviceIsOperatingAtSuperSpeedPlusOrHigher),
            is_device_super_speed_plus_capable_or_higher = bool(fbits.DeviceIsSuperSpeedPlusCapableOrHigher),
        )

    return _ioctl(
        fd,
        CtlCodes.USB_GET_NODE_CONNECTION_INFORMATION_EX_V2,
        create,
        get_result,
    )

def ioctl_get_usb_node_connection_info_ex(
    fd : W.HANDLE,
    connection_index : int,
) -> USBNodeConnectionInfoEx:
    def create():
        data = USB_NODE_CONNECTION_INFORMATION_EX()
        data.ConnectionIndex = connection_index + 1
        return data

    def get_result(
        data : tuple[C.c_void_p, int] | USB_NODE_CONNECTION_INFORMATION_EX,
    ) -> USBNodeConnectionInfoEx:
        if isinstance(data, tuple):
            raise NotImplementedError()
        return USBNodeConnectionInfoEx(
            connection_index = data.ConnectionIndex,
            speed = USBDeviceSpeeds(data.Speed),
            device_is_hub = bool(data.DeviceIsHub),
            device_address = data.DeviceAddress,
            connection_status = USBConnectionStatuses(data.ConnectionStatus),
        )

    return _ioctl(
        fd,
        CtlCodes.USB_GET_NODE_CONNECTION_INFORMATION_EX,
        create,
        get_result,
    )
