from __future__ import annotations

import ctypes as C
import re

from collections.abc import Generator, Iterable
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Literal

from .DeviceManager import (
    Device,
    enumerate_devices,
)

from .IO import (
    create_file,
    close_file,
)

from .IOAPISet import (
    ioctl_get_hcd_driver_key_name,
    ioctl_get_root_hub_name,
    ioctl_get_usb_controller_info,
    ioctl_get_usb_hub_capabilities_ex,
    ioctl_get_usb_hub_extra_info,
    ioctl_get_usb_node_connection_driver_key_name,
    ioctl_get_usb_node_connection_info_ex,
    ioctl_get_usb_node_connection_info_ex_v2,
    ioctl_get_node_connection_name,
    ioctl_get_usb_node_info,
    ioctl_get_usb_port_connector_props,
)

from .Types import (
    ControllerInfo,
    CreationModes,
    DevProperties,
    GenericRights,
    ShareModes,
    USB30HubInformation,
    USBConnectorProps,
    USBConnectionStatuses,
    USBControllerDevIDInfo,
    DevInterfaceGuids,
    USBHubCapabilities,
    USBHubInformation,
    USBHubNodeInformation,
    USBNodeConnectionInfoEx,
    USBNodeConnectionInfoExV2,
)

class USBHostController(Device):
    @contextmanager
    def open_file(
        self,
    ) -> Generator[C.c_void_p]:
        hcfd = create_file(
            self.path,
            GenericRights.WRITE,
            ShareModes.WRITE,
            CreationModes.OPEN_EXISTING,
        )
        try:
            yield hcfd
        finally:
            close_file(hcfd)

    def get_root_hub_name(
        self,
        hcfd : C.c_void_p,
    ) -> str | None:
        try:
            return ioctl_get_root_hub_name(hcfd)
        except:
            return None

    def get_driver_key_name(
        self,
        hcfd : C.c_void_p,
    ) -> str | None:
        try:
            return ioctl_get_hcd_driver_key_name(hcfd)
        except:
            return None

    def get_controller_info(
        self,
        hcfd : C.c_void_p,
    ) -> ControllerInfo | None:
        try:
            return ioctl_get_usb_controller_info(hcfd)
        except:
            return None

    hc_devid_pattern = re.compile(r"^PCI\\VEN_(.+)&DEV_(.+)&SUBSYS_(.+)&REV_(.+)\\.+$")

    def parse_devid(
        self,
    ) -> USBControllerDevIDInfo:
        m = self.hc_devid_pattern.match(self.id)

        if m is None:
            raise ValueError("Incorrect HC DeviceID")

        ven, dev, subsys, rev = m.groups()

        return USBControllerDevIDInfo(
            vendor_id = ven,
            device_id = dev,
            sub_sys_id = subsys,
            revision = rev,
        )

class USBHub(Device):
    @contextmanager
    def open_file(
        self,
    ) -> Generator[C.c_void_p]:
        hubfd = create_file(
            self.path,
            GenericRights.WRITE,
            ShareModes.WRITE,
            CreationModes.OPEN_EXISTING,
        )
        try:
            yield hubfd
        finally:
            close_file(hubfd)

    def get_node_info(
        self,
        hubfd : C.c_void_p,
    ) -> USBHubNodeInformation | None:
        try:
            info = ioctl_get_usb_node_info(hubfd)

            if not isinstance(info, USBHubNodeInformation):
                raise ValueError("The USB node is not a hub")

            return info
        except:
            return None

    def get_hub_info(
        self,
        hubfd : C.c_void_p,
    ) -> USBHubInformation | USB30HubInformation | None:
        try:
            return ioctl_get_usb_hub_extra_info(hubfd)
        except:
            return None

    def get_capabilities(
        self,
        hubfd : C.c_void_p,
    ) -> USBHubCapabilities | None:
        try:
            return ioctl_get_usb_hub_capabilities_ex(hubfd)
        except:
            return None

class USBPort:
    def __init__(
        self,
        index : int,
    ):
        self.index = index

    def get_connector_props(
        self,
        hubfd : C.c_void_p,
    ) -> USBConnectorProps | None:
        try:
            return ioctl_get_usb_port_connector_props(hubfd, self.index)
        except:
            return None

    def get_connection_info(
        self,
        hubfd : C.c_void_p,
    ) -> USBNodeConnectionInfoEx | None:
        try:
            return ioctl_get_usb_node_connection_info_ex(hubfd, self.index)
        except:
            return None

    def get_connection_info_2(
        self,
        hubfd : C.c_void_p,
    ) -> USBNodeConnectionInfoExV2 | None:
        try:
            return ioctl_get_usb_node_connection_info_ex_v2(hubfd, self.index)
        except:
            return None

    def get_connection_driver_key_name(
        self,
        hubfd : C.c_void_p,
    ) -> str | None:
        try:
            return ioctl_get_usb_node_connection_driver_key_name(hubfd, self.index)
        except:
            return None

    def get_connection_name(
        self,
        hubfd : C.c_void_p,
    ) -> str | None:
        try:
            return ioctl_get_node_connection_name(hubfd, self.index)
        except:
            return None

class USBDevice(Device):
    pass

@dataclass
class USBNode:
    level : int
    parent : USBNode | None
    device : USBHostController | USBHub | USBPort | USBDevice
    children : list[USBNode] = field(default_factory = list["USBNode"])

def enumerate_usb_host_controllers(
    properties : Iterable[DevProperties] | Literal["all"] = [],
) -> Generator[USBHostController]:
    return enumerate_devices(
        DevInterfaceGuids.USB_HOST_CONTROLLER,
        USBHostController,
        properties,
    )

def enumerate_usb_hubs(
    properties : Iterable[DevProperties] | Literal["all"] = [],
) -> Generator[USBHub]:
    return enumerate_devices(
        DevInterfaceGuids.USB_HUB,
        USBHub,
        properties,
    )

def enumerate_usb_devices(
    properties : Iterable[DevProperties] | Literal["all"] = [],
) -> Generator[USBDevice]:
    return enumerate_devices(
        DevInterfaceGuids.USB_DEVICE,
        USBDevice,
        properties,
    )

def build_usb_tree(
) -> list[USBNode]:
    hcs = enumerate_usb_host_controllers([
        DevProperties.DEVICEDESC,
    ])
    hubs = list(enumerate_usb_hubs([
        DevProperties.DRIVER,
        DevProperties.DEVICEDESC,
    ]))
    devs = list(enumerate_usb_devices([
        DevProperties.DRIVER,
        DevProperties.DEVICEDESC,
    ]))

    def _enumerate_hub(
        level : int,
        hub : USBHub,
        parent : USBNode | None,
    ) -> USBNode:
        node = USBNode(
            level = level,
            parent = parent,
            device = hub,
        )

        with hub.open_file() as hubfd:
            hub_node_info = hub.get_node_info(hubfd)

            if hub_node_info is not None:
                for i in range(hub_node_info.number_of_ports):
                    port = USBPort(i)
                    node_port = USBNode(
                        level = level + 1,
                        parent = node,
                        device = port,
                    )
                    node.children.append(node_port)

                    connection_info = port.get_connection_info(hubfd)
                    connection_dkn = port.get_connection_driver_key_name(hubfd)

                    if (
                        connection_info is not None
                        and connection_info.connection_status != USBConnectionStatuses.NoDeviceConnected
                    ):
                        connection_options = hubs \
                            if connection_info.device_is_hub \
                            else devs

                        connected_dev = next(
                            (
                                dev for dev in connection_options \
                                    if dev.properties[DevProperties.DRIVER] == connection_dkn
                            ),
                            None,
                        )

                        if connected_dev is not None:
                            if (
                                connection_info.device_is_hub
                                and isinstance(connected_dev, USBHub)
                            ):
                                node_connected_dev = _enumerate_hub(
                                    level + 2,
                                    connected_dev,
                                    node_port,
                                )
                            else:
                                node_connected_dev = USBNode(
                                    level = level + 2,
                                    parent = node_port,
                                    device = connected_dev,
                                )

                            node_port.children.append(node_connected_dev)

        return node

    nodes : list[USBNode] = []

    for hc in hcs:
        node = USBNode(
            level = 0,
            parent = None,
            device = hc,
        )

        with hc.open_file() as hcfd:
            root_hub_name = hc.get_root_hub_name(hcfd)

        if root_hub_name is not None:
            root_hub = next(
                (
                    hub for hub in hubs \
                        if hub.path[4:].lower() == root_hub_name.lower()
                ),
                None,
            )

            if root_hub is not None:
                node.children.append(
                    _enumerate_hub(1, root_hub, None),
                )

        nodes.append(node)

    return nodes
