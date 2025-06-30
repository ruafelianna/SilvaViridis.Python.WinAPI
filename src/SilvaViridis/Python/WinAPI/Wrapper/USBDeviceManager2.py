import re

from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from .Exceptions import (
    NoMoreItems,
    InvalidData,
)
from .IO import (
    create_file,
    close_file,
)
from .IOAPISet import (
    ioctl_get_hcd_driver_key_name,
    ioctl_get_usb_controller_info,
    ioctl_get_root_hub_name,
    ioctl_get_usb_node_info,
    ioctl_get_usb_hub_extra_info,
    ioctl_get_usb_hub_capabilities_ex,
    ioctl_get_usb_port_connector_props,
    ioctl_get_usb_node_connection_info_ex_v2,
    ioctl_get_usb_node_connection_info_ex,
    ioctl_get_usb_node_connection_driver_key_name,
    ioctl_get_node_connection_name,
)
from .SetupAPI import (
    get_class_devs,
    next_device_info,
    get_device_property,
    get_device_interface,
    get_device_interface_devpath,
    get_device_instance_id,
    free_device_list,
)
from .Types import (
    GenericRights,
    ShareModes,
    CreationModes,
    USBControllerFlavors,
    HCFeatureFlags,
    USBDevInterfaceGuids,
    IncludedInfoFlags,
    DevProperties,
    USBHubNodeInformation,
    USB30HubInformation,
    USBConnectionStatuses,
    USBDeviceSpeeds,
)

class USBNodeInfo:
    pass

class USBDeviceInfo(USBNodeInfo):
    pass

@dataclass
class USBPortInfo:
    index : int
    companion_index : int
    companion_port : int
    companion_name : str
    is_user_connectable : bool
    is_debug_capable : bool
    has_multiple_companions : bool
    is_type_c : bool
    is_usb_110_supported : bool
    is_usb_200_supported : bool
    is_usb_300_supported : bool
    is_device_operating_at_super_speed_or_higher : bool
    is_device_super_speed_capable_or_higher : bool
    is_device_operating_at_super_speed_plus_or_higher : bool
    is_device_super_speed_plus_capable_or_higher : bool
    speed : USBDeviceSpeeds
    device_is_hub : bool
    device_address : int
    connection_status : USBConnectionStatuses
    connected_device_driver_key : str | None
    external_hub_name : str | None

@dataclass
class USBHubInfo(USBNodeInfo):
    ports : list[USBPortInfo]
    is_high_speed_capable : bool
    is_high_speed : bool
    is_multi_tt_capable : bool
    is_multi_tt : bool
    is_root : bool
    is_armed_wake_on_connect : bool
    is_bus_powered : bool
    number_of_ports : int
    hub_characteristics : int
    power_on_to_power_good : int
    hub_control_current : int
    remove_and_power_mask : list[int]
    highest_port_number : int
    hub_packet_header_decode_latency : int | None = None
    hub_delay : int | None = None
    device_removable : int | None = None

@dataclass
class USBHostControllerInfo(USBNodeInfo):
    driver_key_name : str
    vendor_id : str
    device_id : str
    sub_sys_id : str
    revision : str
    pci_vendor_id : int
    pci_device_id : int
    pci_revision : int
    number_of_root_ports : int
    controller_flavor : USBControllerFlavors
    hc_feature_flags : HCFeatureFlags
    root_hub_name : str

@dataclass
class USBNode:
    class_guid : UUID
    interface_class_guid : UUID
    devpath : str
    devid : str
    props : dict[DevProperties, str | int | bytes | None]
    devinfo : USBNodeInfo

class USBDeviceManager:
    def build_tree(
        self,
    ):
        devs = self.enumerate_devices(USBDevInterfaceGuids.DEVICE)
        hcs = self.enumerate_devices(USBDevInterfaceGuids.HOST_CONTROLLER)
        hubs = self.enumerate_devices(USBDevInterfaceGuids.HUB)

        for dev in devs:
            self.print_device(dev)

        def _print_tree(nodes : list[tuple[USBNode | None, str]], level : int):
            for dev, prefix in nodes:
                begin = f"{"  " * level}[{prefix}]"
                if dev is None:
                    print(begin)
                    continue
                print(f"{begin} {dev.devpath}")
                if isinstance(dev.devinfo, USBHostControllerInfo):
                    try:
                        root_hub = next(r for r in hubs if dev.devinfo.root_hub_name.lower() == r.devpath[4:].lower())
                        _print_tree([(root_hub, "HUB")], level + 1)
                    except StopIteration:
                        pass
                elif isinstance(dev.devinfo, USBHubInfo):
                    connected_devices : list[tuple[USBNode | None, str]] = []

                    for p in dev.devinfo.ports:
                        try:
                            if p.device_is_hub and p.external_hub_name is not None:
                                cd = next(h for h in hubs if h.devpath[4:].lower() == p.external_hub_name.lower())
                            elif p.connected_device_driver_key is not None:
                                cd = next(d for d in devs if d.props[DevProperties.DRIVER] == p.connected_device_driver_key)
                            else:
                                cd = None
                        except StopIteration:
                            cd = None

                        if cd is None:
                            pr = "NONE"
                        elif p.device_is_hub:
                            pr = "HUB"
                        else:
                            pr = "DEV"

                        connected_devices.append((cd, f"PORT {p.index:02}][{pr}"))

                    _print_tree(connected_devices, level + 1)

        _print_tree([(hc, "HC") for hc in hcs], 0)

    def print_device(self, device : USBNode) -> None:
        print(f"Class GUID: {device.class_guid}")
        print(f"Interface Class GUID: {device.interface_class_guid}")
        print(f"Device Path: {device.devpath}")
        print(f"Device ID: {device.devid}")

        if isinstance(device.devinfo, USBDeviceInfo):
            pass
        elif isinstance(device.devinfo, USBHubInfo):
            print(f"Is High Speed Capable: {device.devinfo.is_high_speed_capable}")
            print(f"Is High Speed: {device.devinfo.is_high_speed}")
            print(f"Is Multi Transaction Translations Capable: {device.devinfo.is_multi_tt_capable}")
            print(f"Is Multi Transaction Translations: {device.devinfo.is_multi_tt}")
            print(f"Is Root: {device.devinfo.is_root}")
            print(f"Is Armed Wake On Connect: {device.devinfo.is_armed_wake_on_connect}")
            print(f"Is Bus Powered: {device.devinfo.is_bus_powered}")
            print(f"Number of Ports: {device.devinfo.number_of_ports}")
            print(f"Hub Characteristics: {device.devinfo.hub_characteristics}")
            print(f"Power On to Power Good: {device.devinfo.power_on_to_power_good}")
            print(f"Hub Control Current: {device.devinfo.hub_control_current}")
            print(f"Remove And Power Mask: {device.devinfo.remove_and_power_mask}")
            print(f"Highest Port Number: {device.devinfo.highest_port_number}")
            print(f"Packet Header Decode Latency: {device.devinfo.hub_packet_header_decode_latency}")
            print(f"Hub Delay: {device.devinfo.hub_delay}")
            print(f"Device Removable: {device.devinfo.device_removable}")
        elif isinstance(device.devinfo, USBHostControllerInfo):
            print(f"HC Driver Key Name: {device.devinfo.driver_key_name}")
            print(f"HC Vendor ID: {device.devinfo.vendor_id}")
            print(f"HC Device ID: {device.devinfo.device_id}")
            print(f"HC SubSys ID: {device.devinfo.sub_sys_id}")
            print(f"HC Revision: {device.devinfo.revision}")
            print(f"PCI Vendor ID: {device.devinfo.pci_vendor_id}")
            print(f"PCI Device ID: {device.devinfo.pci_device_id}")
            print(f"PCI Revision: {device.devinfo.pci_revision}")
            print(f"Number of Root Ports: {device.devinfo.number_of_root_ports}")
            print(f"Controller Flavor: {device.devinfo.controller_flavor}")
            print(f"Features: {device.devinfo.hc_feature_flags}")
            print(f"Root Hub Name: {device.devinfo.root_hub_name}")
        else:
            raise NotImplementedError()

        for prop, value in device.props.items():
            print(f"[{prop.value:02}] {prop.name} = {value}")

    def enumerate_devices(
        self,
        guid : USBDevInterfaceGuids,
        properties : Iterable[DevProperties] | None = None,
    ) -> list[USBNode]:
        result : list[USBNode] = []

        hdevinfo = get_class_devs(
            guid.value,
            None,
            None,
            IncludedInfoFlags.PRESENT | IncludedInfoFlags.DEVICEINTERFACE,
        )

        try:
            index = 0
            while True:
                try:
                    devinfo = next_device_info(hdevinfo, index)
                except NoMoreItems:
                    break

                interfaceinfo = get_device_interface(hdevinfo, guid.value, index)

                devpath = get_device_interface_devpath(hdevinfo, interfaceinfo)

                devid = get_device_instance_id(hdevinfo, devinfo)

                props : dict[DevProperties, str | int | bytes | None] = {}

                for prop_name in DevProperties if properties is None else properties:
                    try:
                        prop = get_device_property(hdevinfo, devinfo, prop_name)
                        props[prop_name] = prop
                    except InvalidData:
                        props[prop_name] = "N/A"
                    except Exception as ex:
                        props[prop_name] = f"Error: {ex}"

                info : USBNodeInfo
                if guid == USBDevInterfaceGuids.DEVICE:
                    info = self.get_device_info()
                elif guid == USBDevInterfaceGuids.HUB:
                    info = self.get_hub_info(devpath)
                elif guid == USBDevInterfaceGuids.HOST_CONTROLLER:
                    info = self.get_hc_info(devpath, devid)
                else:
                    raise NotImplementedError()

                result.append(USBNode(
                    class_guid = devinfo.class_guid,
                    interface_class_guid = interfaceinfo.interface_class_guid,
                    devpath = devpath,
                    devid = devid,
                    props = props,
                    devinfo = info,
                ))

                index += 1
        finally:
            free_device_list(hdevinfo)

        return result

    def get_device_info(
        self,
    ) -> USBDeviceInfo:
        return USBDeviceInfo()

    def get_hub_info(
        self,
        devpath : str,
    ) -> USBHubInfo:
        hubfd = create_file(
            devpath,
            GenericRights.WRITE,
            ShareModes.WRITE,
            CreationModes.OPEN_EXISTING,
        )
        try:
            node_info = ioctl_get_usb_node_info(hubfd)

            if not isinstance(node_info, USBHubNodeInformation):
                raise ValueError("The USB node is not a hub")

            hub_info = ioctl_get_usb_hub_extra_info(hubfd)
            capabilities = ioctl_get_usb_hub_capabilities_ex(hubfd)

            ports : list[USBPortInfo] = []

            for i in range(node_info.number_of_ports):
                connector_props = ioctl_get_usb_port_connector_props(hubfd, i)
                connection_info_2 = ioctl_get_usb_node_connection_info_ex_v2(hubfd, i)
                connection_info = ioctl_get_usb_node_connection_info_ex(hubfd, i)

                if (
                    connection_info.speed == USBDeviceSpeeds.UsbHighSpeed
                    and (
                        connection_info_2.is_device_operating_at_super_speed_or_higher
                        or connection_info_2.is_device_operating_at_super_speed_plus_or_higher
                    )
                ):
                    connection_info.speed = USBDeviceSpeeds.UsbSuperSpeed

                driver_key_name = None \
                    if connection_info.connection_status == USBConnectionStatuses.NoDeviceConnected \
                    else ioctl_get_usb_node_connection_driver_key_name(hubfd, i)

                external_hub_name = ioctl_get_node_connection_name(hubfd, i) \
                    if connection_info.device_is_hub \
                    else None

                ports.append(USBPortInfo(
                    index = connector_props.connection_index,
                    companion_index = connector_props.companion_index,
                    companion_port = connector_props.companion_port_number,
                    companion_name = connector_props.companion_hub_symlink,
                    is_user_connectable = connector_props.port_is_user_connectable,
                    is_debug_capable = connector_props.port_is_debug_capable,
                    has_multiple_companions = connector_props.port_has_multiple_companions,
                    is_type_c = connector_props.port_connector_is_type_c,
                    is_usb_110_supported = connection_info_2.is_usb_110_supported,
                    is_usb_200_supported = connection_info_2.is_usb_200_supported,
                    is_usb_300_supported = connection_info_2.is_usb_300_supported,
                    is_device_operating_at_super_speed_or_higher = connection_info_2.is_device_operating_at_super_speed_or_higher,
                    is_device_super_speed_capable_or_higher = connection_info_2.is_device_super_speed_capable_or_higher,
                    is_device_operating_at_super_speed_plus_or_higher = connection_info_2.is_device_operating_at_super_speed_plus_or_higher,
                    is_device_super_speed_plus_capable_or_higher = connection_info_2.is_device_super_speed_plus_capable_or_higher,
                    speed = connection_info.speed,
                    device_is_hub = connection_info.device_is_hub,
                    device_address = connection_info.device_address,
                    connection_status = connection_info.connection_status,
                    connected_device_driver_key = driver_key_name,
                    external_hub_name = external_hub_name,
                ))

        finally:
            close_file(hubfd)

        result = USBHubInfo(
            ports = ports,
            is_high_speed_capable = capabilities.is_high_speed_capable,
            is_high_speed = capabilities.is_high_speed,
            is_multi_tt_capable = capabilities.is_multi_tt_capable,
            is_multi_tt = capabilities.is_multi_tt,
            is_root = capabilities.is_root,
            is_armed_wake_on_connect = capabilities.is_armed_wake_on_connect,
            is_bus_powered = node_info.is_bus_powered,
            number_of_ports = node_info.number_of_ports,
            hub_characteristics = node_info.hub_characteristics,
            power_on_to_power_good = node_info.power_on_to_power_good,
            hub_control_current = node_info.hub_control_current,
            remove_and_power_mask = node_info.remove_and_power_mask,
            highest_port_number = hub_info.highest_port_number
        )

        if isinstance(hub_info, USB30HubInformation):
            result.hub_packet_header_decode_latency = hub_info.hub_packet_header_decode_latency
            result.hub_delay = hub_info.hub_delay
            result.device_removable = hub_info.device_removable

        return result

    hc_devid_pattern = re.compile(r"^PCI\\VEN_(.+)&DEV_(.+)&SUBSYS_(.+)&REV_(.+)\\.+$")

    def get_hc_info(
        self,
        devpath : str,
        devid : str,
    ) -> USBHostControllerInfo:
        hcfd = create_file(
            devpath,
            GenericRights.WRITE,
            ShareModes.WRITE,
            CreationModes.OPEN_EXISTING,
        )

        try:
            driver_key_name = ioctl_get_hcd_driver_key_name(hcfd)
            controller_info = ioctl_get_usb_controller_info(hcfd)
            root_hub_name = ioctl_get_root_hub_name(hcfd)
        finally:
            close_file(hcfd)

        m = self.hc_devid_pattern.match(devid)

        if m is None:
            raise ValueError("Incorrect HC DeviceID")

        ven, dev, subsys, rev = m.groups()

        return USBHostControllerInfo(
            driver_key_name = driver_key_name,
            vendor_id = ven,
            device_id = dev,
            sub_sys_id = subsys,
            revision = rev,
            pci_vendor_id = controller_info.pci_vendor_id,
            pci_device_id = controller_info.pci_device_id,
            pci_revision = controller_info.pci_revision,
            number_of_root_ports = controller_info.number_of_root_ports,
            controller_flavor = controller_info.controller_flavor,
            hc_feature_flags = controller_info.hc_feature_flags,
            root_hub_name = root_hub_name,
        )
