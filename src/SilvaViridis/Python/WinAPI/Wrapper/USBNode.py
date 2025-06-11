from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .IOAPISet import USBControllerFlavor, HCFeatureFlags
from .SetupAPI import DevProperties

@dataclass
class USBNode:
    class_guid : UUID
    interface_class_guid : UUID
    devpath : str
    devid : str
    props : dict[DevProperties, str | int | bytes | None]
    devinfo : USBNodeInfo

class USBNodeInfo:
    pass

class USBDeviceInfo(USBNodeInfo):
    pass

class USBHubInfo(USBNodeInfo):
    pass

@dataclass
class USBHostControllerInfo(USBNodeInfo):
    driver_key_name : str
    vendor_id : str
    device_id : str
    sub_sys_id : str
    revision : str
    pci_vendor_id : int
    pci_device_id : int
    pci_revision : int
    number_of_root_ports : int
    controller_flavor : USBControllerFlavor
    hc_feature_flags : HCFeatureFlags
