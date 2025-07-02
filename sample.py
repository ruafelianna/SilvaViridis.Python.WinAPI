from SilvaViridis.Python.WinAPI.Wrapper import USBDeviceManager, Types

nodes = USBDeviceManager.build_usb_tree()

def print_nodes(nodes : list[USBDeviceManager.USBNode]):
    for node in nodes:
        if isinstance(node.device, USBDeviceManager.USBPort):
            s = f"Port {node.device.index + 1:02}"
        else:
            s = f"{node.device.properties[Types.DevProperties.DEVICEDESC]}"
        print(f"{"  " * node.level} {s}")
        print_nodes(node.children)

print_nodes(nodes)
