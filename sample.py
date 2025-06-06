from SilvaViridis.Python.WinAPI.Utils import (
    enumerate_devices,
    get_device_property,
    get_devinterface_data,
    get_devinterface_devpath,
)
from SilvaViridis.Python.WinAPI.setupapi import SPDRP_DEVICEDESC, SPDRP_DRIVER
from SilvaViridis.Python.WinAPI.usbiodef import GUID_DEVINTERFACE_USB_DEVICE

set_pointer, dev_enumeration = enumerate_devices(GUID_DEVINTERFACE_USB_DEVICE)

if set_pointer is not None:
    for index, dev in dev_enumeration.items():
        print(index)
        print(dev.ClassGuid)
        print(get_device_property(set_pointer, dev, SPDRP_DEVICEDESC))
        print(get_device_property(set_pointer, dev, SPDRP_DRIVER))
        infc_data = get_devinterface_data(set_pointer, GUID_DEVINTERFACE_USB_DEVICE, index)
        print(infc_data.InterfaceClassGuid)
        print(get_devinterface_devpath(set_pointer, infc_data))
        print("-" * 80)
