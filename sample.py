from SilvaViridis.Python.WinAPI.Wrapper import USBDeviceManager, COMPortDeviceManager, Tools

comports = list(COMPortDeviceManager.enumerate_comport_devices())

usb_tree = USBDeviceManager.build_usb_tree()

def print_comports(node : USBDeviceManager.USBNode) -> str:
    if not isinstance(node.device, USBDeviceManager.USBPort):
        ports = Tools.get_comports_for_usb(node.device, comports)
        if len(ports) > 0:
            return f" # {", ".join(ports)}"
    return ""

USBDeviceManager.print_usb_tree(
    usb_tree,
    get_additional_info = print_comports,
)
