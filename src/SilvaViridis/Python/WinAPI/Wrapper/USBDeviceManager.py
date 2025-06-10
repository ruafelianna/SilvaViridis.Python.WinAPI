from collections.abc import Iterable
from uuid import UUID

from .USBNode import (
    USBNode,
    USBNodeInfo,
    USBDeviceInfo,
    USBHubInfo,
    USBHostControllerInfo,
)
from .Exceptions import NoMoreItems
from .IO import (
    GenericRights,
    ShareModes,
    CreationModes,
    create_file,
    close_file,
)
from .IOAPISet import (
    ioctl_get_hcd_driver_key_name,
)
from .SetupAPI import (
    IncludedInfoFlags,
    DevProperties,
    get_class_devs,
    next_device_info,
    get_device_property,
    get_device_interface,
    get_device_interface_devpath,
    free_device_list,
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
        print("-" * 20)
        print(hcs)
        print("-" * 20)
        print(hubs)

    def enumerate_devices(
        self,
        guid : UUID,
        properties : Iterable[DevProperties] | None = None,
    ) -> list[USBNode]:
        result : list[USBNode] = []

        hdevinfo = get_class_devs(
            guid,
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

                interfaceinfo = get_device_interface(hdevinfo, guid, index)

                devpath = get_device_interface_devpath(hdevinfo, interfaceinfo)

                props : dict[DevProperties, str | int | bytes | None] = {}

                for prop_name in DevProperties if properties is None else properties:
                    try:
                        prop = get_device_property(hdevinfo, devinfo, prop_name)
                        props[prop_name] = prop
                    except:
                        pass

                info : USBNodeInfo
                if guid == GUID_DEVINTERFACE_USB_DEVICE:
                    info = self.get_device_info()
                elif guid == GUID_DEVINTERFACE_USB_HUB:
                    info = self.get_hub_info()
                elif guid == GUID_DEVINTERFACE_USB_HOST_CONTROLLER:
                    info = self.get_hc_info(devpath)
                else:
                    raise NotImplementedError()

                result.append(USBNode(
                    class_guid = devinfo.class_guid,
                    interface_class_guid = interfaceinfo.interface_class_guid,
                    devpath = devpath,
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
    ) -> USBHubInfo:
        return USBHubInfo()

    def get_hc_info(
        self,
        devpath : str,
    ) -> USBHostControllerInfo:
        hcfd = create_file(
            devpath,
            GenericRights.WRITE,
            ShareModes.WRITE,
            CreationModes.OPEN_EXISTING,
        )

        try:
            driver_key_name = ioctl_get_hcd_driver_key_name(hcfd)
        finally:
            close_file(hcfd)

        return USBHostControllerInfo(
            driver_key_name = driver_key_name,
        )
