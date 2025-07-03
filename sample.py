from SilvaViridis.Python.WinAPI.Wrapper import USBDeviceManager, Types, COMPortDeviceManager

comports = list(COMPortDeviceManager.enumerate_comport_devices())

nodes = USBDeviceManager.build_usb_tree()

def print_nodes(nodes : list[USBDeviceManager.USBNode]):
    for node in nodes:
        if isinstance(node.device, USBDeviceManager.USBPort):
            s = f"Port {node.device.index + 1:02}"
        else:
            s = f"{node.device.properties[Types.DevProperties.DEVICEDESC]} [{node.device.id}]"

            comport = next(
                (p for p in comports if p.parent.lower() == node.device.id.lower()),
                None,
            )

            if comport is not None:
                s = f"[{comport.get_port_name()}] {s}"
        print(f"{"  " * node.level} {s}")
        print_nodes(node.children)

print_nodes(nodes)
