import re

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
    ioctl_get_usb_controller_info,
)
from .SetupAPI import (
    IncludedInfoFlags,
    DevProperties,
    get_class_devs,
    next_device_info,
    get_device_property,
    get_device_interface,
    get_device_interface_devpath,
    get_device_instance_id,
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

        for dev in devs:
            self.print_device(dev)
        print("-" * 20)
        for dev in hcs:
            self.print_device(dev)
        print("-" * 20)
        for dev in hubs:
            self.print_device(dev)

    def print_device(self, device : USBNode) -> None:
        print(f"Class GUID: {device.class_guid}")
        print(f"Interface Class GUID: {device.interface_class_guid}")
        print(f"Device Path: {device.devpath}")
        print(f"Device ID: {device.devid}")

        if isinstance(device.devinfo, USBDeviceInfo):
            pass
        elif isinstance(device.devinfo, USBHubInfo):
            pass
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
        else:
            raise NotImplementedError()

        for prop, value in device.props.items():
            print(f"{prop.name} [{prop.value}] = {value}")

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

                devid = get_device_instance_id(hdevinfo, devinfo)

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
    ) -> USBHubInfo:
        return USBHubInfo()

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
        )
