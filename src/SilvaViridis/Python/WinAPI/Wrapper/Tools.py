from .COMPortDeviceManager import COMPortDevice
from .USBDeviceManager import Device

def get_comports_for_usb(
    device : Device,
    comports : list[COMPortDevice],
) -> list[str]:
    result : list[str] = []

    for port in comports:
        if port.parent.lower() == device.id.lower():
            result.append(port.get_port_name())

    return result
