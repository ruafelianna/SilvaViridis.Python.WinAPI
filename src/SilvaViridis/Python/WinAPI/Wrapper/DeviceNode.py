from dataclasses import dataclass
from uuid import UUID

from .SetupAPI import DevProperties

@dataclass
class USBDeviceNode:
    class_guid : UUID
    interface_class_guid : UUID
    devpath : str
    props : dict[DevProperties, str | int | bytes | None]
