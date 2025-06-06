from SilvaViridis.Python.WinAPI.Utils import (
    enumerate_devices,
    get_device_property,
    get_devinterface_data,
    get_devinterface_devpath,
)
from SilvaViridis.Python.WinAPI.guiddef import GUID
from SilvaViridis.Python.WinAPI.setupapi import SPDRP_DEVICEDESC, SPDRP_DRIVER
from SilvaViridis.Python.WinAPI.usbiodef import (
    GUID_DEVINTERFACE_USB_DEVICE,
    GUID_DEVINTERFACE_USB_HUB,
)

def print_devices(guid : GUID):
    set_pointer, dev_enumeration = enumerate_devices(guid)
    if set_pointer is not None:
        for index, dev in dev_enumeration.items():
            print(index)
            print(dev.ClassGuid)

            try:
                print(get_device_property(set_pointer, dev, SPDRP_DEVICEDESC))
            except Exception as ex:
                print(ex)

            try:
                print(get_device_property(set_pointer, dev, SPDRP_DRIVER))
            except Exception as ex:
                print(ex)

            try:
                infc_data = get_devinterface_data(set_pointer, GUID_DEVINTERFACE_USB_DEVICE, index)
                print(infc_data.InterfaceClassGuid)
                print(get_devinterface_devpath(set_pointer, infc_data))
            except Exception as ex:
                print(ex)

            print("-" * 80) 

print_devices(GUID_DEVINTERFACE_USB_DEVICE)
print_devices(GUID_DEVINTERFACE_USB_HUB)
