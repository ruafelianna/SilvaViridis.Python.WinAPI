from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from .SetupAPI import DevProperties

@dataclass
class USBNode:
    class_guid : UUID
    interface_class_guid : UUID
    devpath : str
    props : dict[DevProperties, str | int | bytes | None]
    devinfo : USBNodeInfo

class USBNodeInfo:
    pass

class USBDeviceInfo(USBNodeInfo):
    pass

class USBHubInfo(USBNodeInfo):
    pass

class USBHostControllerInfo(USBNodeInfo):
    pass
