from SilvaViridis.Python.WinAPI.Wrapper import USBDeviceManager

from SilvaViridis.Python.WinAPI.Wrapper.Types import (
    DevProperties,
    USBDevInterfaceGuids,
)

# dm = USBDeviceManager()

# dm.build_tree()

for device in USBDeviceManager.enumerate_devices(
    USBDevInterfaceGuids.DEVICE,
    [
        DevProperties.DRIVER,
    ]
):
    print(device)
