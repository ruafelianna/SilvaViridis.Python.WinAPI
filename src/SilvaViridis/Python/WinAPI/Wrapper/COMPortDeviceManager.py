from collections.abc import Generator, Iterable
from typing import Literal

from .DeviceManager import (
    Device,
    enumerate_devices,
)

from .Types import (
    DevInterfaceGuids,
    DevProperties,
)

class COMPortDevice(Device):
    def get_port_name(
        self,
    ) -> str:
        return self.reg_properties["PortName"]

def enumerate_comport_devices(
    properties : Iterable[DevProperties] | Literal["all"] = [],
) -> Generator[COMPortDevice]:
    return enumerate_devices(
        DevInterfaceGuids.COMPORT,
        COMPortDevice,
        properties,
        [
            "PortName",
        ],
    )
