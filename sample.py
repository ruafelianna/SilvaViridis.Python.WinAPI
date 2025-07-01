from SilvaViridis.Python.WinAPI.Wrapper import USBDeviceManager

from SilvaViridis.Python.WinAPI.Wrapper.Types import (
    DevProperties,
)

# dm = USBDeviceManager()

# dm.build_tree()

for device in USBDeviceManager.enumerate_usb_devices(
    [
        DevProperties.DRIVER,
    ]
):
    print(device)
