from collections.abc import Generator, Iterable
from typing import Literal
from uuid import UUID

from .DeviceManager import (
    enumerate_devices,
)

from .Types import (
    DevProperties,
    USBDevInterfaceGuids,
)

class USBNode:
    pass

class USBDeviceNode(USBNode):
    def __init__(
        self,
        class_guid : UUID,
        interface_class_guid : UUID,
        path : str,
        id : str,
        properties : dict[DevProperties, str | int | bytes | None],
    ) -> None:
        self.class_guid = class_guid
        self.interface_class_guid = interface_class_guid
        self.path = path
        self.id = id
        self.properties = properties

    def __str__(
        self,
    ) -> str:
        return f"""\
class_guid = {self.class_guid}
interface_class_guid = {self.interface_class_guid}
path = {self.path}
id = {self.id}
{"\n".join([f"[{p.value:02}] {p.name} = {self.properties[p]}" for p in self.properties])}\
"""

class USBHostController(USBDeviceNode):
    pass

class USBHub(USBDeviceNode):
    pass

class USBPort(USBNode):
    pass

class USBDevice(USBDeviceNode):
    pass

def enumerate_usb_host_controllers(
    properties : Iterable[DevProperties] | Literal["all"] = [],
) -> Generator[USBHostController]:
    return enumerate_devices(
        USBDevInterfaceGuids.HOST_CONTROLLER,
        USBHostController,
        properties,
    )

def enumerate_usb_hubs(
    properties : Iterable[DevProperties] | Literal["all"] = [],
) -> Generator[USBHub]:
    return enumerate_devices(
        USBDevInterfaceGuids.HUB,
        USBHub,
        properties,
    )

def enumerate_usb_devices(
    properties : Iterable[DevProperties] | Literal["all"] = [],
) -> Generator[USBDevice]:
    return enumerate_devices(
        USBDevInterfaceGuids.DEVICE,
        USBDevice,
        properties,
    )
