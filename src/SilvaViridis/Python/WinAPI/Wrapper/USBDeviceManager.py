from collections.abc import Iterable
from uuid import UUID

from .DeviceNode import USBDeviceNode
from .Exceptions import NoMoreItems
from .SetupAPI import (
    IncludedInfoFlags,
    DevProperties,
    get_class_devs,
    next_device_info,
    get_device_property,
    get_device_interface,
    get_device_interface_devpath,
)
from .USBGuids import (
    GUID_DEVINTERFACE_USB_DEVICE,
    GUID_DEVINTERFACE_USB_HOST_CONTROLLER,
    GUID_DEVINTERFACE_USB_HUB,
)

class USBDeviceManager:
    def build_tree(
        self,
    ):
        devs = self.enumerate_devices(GUID_DEVINTERFACE_USB_DEVICE)
        hcs = self.enumerate_devices(GUID_DEVINTERFACE_USB_HOST_CONTROLLER)
        hubs = self.enumerate_devices(GUID_DEVINTERFACE_USB_HUB)

        print(devs)
        print(hcs)
        print(hubs)

    def enumerate_devices(
        self,
        guid : UUID,
        properties : Iterable[DevProperties] | None = None,
    ) -> list[USBDeviceNode]:
        result : list[USBDeviceNode] = []

        hdevinfo = get_class_devs(
            guid,
            None,
            None,
            IncludedInfoFlags.PRESENT | IncludedInfoFlags.DEVICEINTERFACE,
        )

        index = 0
        while True:
            try:
                devinfo = next_device_info(hdevinfo, index)
            except NoMoreItems:
                break

            interfaceinfo = get_device_interface(hdevinfo, guid, index)

            devpath = get_device_interface_devpath(hdevinfo, interfaceinfo)

            props : dict[DevProperties, str | int | bytes | None] = {}

            for prop_name in DevProperties if properties is None else properties:
                try:
                    prop = get_device_property(hdevinfo, devinfo, prop_name)
                    props[prop_name] = prop
                except:
                    pass

            result.append(USBDeviceNode(
                class_guid = devinfo.class_guid,
                interface_class_guid = interfaceinfo.interface_class_guid,
                devpath = devpath,
                props = props,
            ))

            index += 1

        return result
