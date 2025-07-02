from collections.abc import Callable, Generator, Iterable
from typing import Literal
from uuid import UUID

from .Exceptions import (
    InvalidData,
    NoMoreItems,
)

from .SetupAPI import (
    free_device_list,
    get_class_devs,
    get_device_instance_id,
    get_device_interface,
    get_device_interface_devpath,
    get_device_property,
    get_device_registry_property,
    next_device_info,
)

from .Types import (
    DevProperties,
    IncludedInfoFlags,
    DevInterfaceGuids,
    DevPropKeys,
)

class Device:
    def __init__(
        self,
        class_guid : UUID,
        interface_class_guid : UUID,
        path : str,
        id : str,
        parent : str,
        properties : dict[DevProperties, str | int | bytes | None],
    ) -> None:
        self.class_guid = class_guid
        self.interface_class_guid = interface_class_guid
        self.path = path
        self.id = id
        self.parent = parent
        self.properties = properties

    def __str__(
        self,
    ) -> str:
        return f"""\
class_guid = {self.class_guid}
interface_class_guid = {self.interface_class_guid}
path = {self.path}
id = {self.id}
parent = {self.parent}
{"\n".join([f"[{p.value:02}] {p.name} = {self.properties[p]}" for p in self.properties])}\
"""

def enumerate_devices[TOutput : Device](
    guid : DevInterfaceGuids,
    create_device : Callable[[UUID, UUID, str, str, str, dict[DevProperties, str | int | bytes | None]], TOutput],
    properties : Iterable[DevProperties] | Literal["all"] = [],
) -> Generator[TOutput]:
    hdevinfo = get_class_devs(
        guid.value,
        None,
        None,
        IncludedInfoFlags.PRESENT | IncludedInfoFlags.DEVICEINTERFACE,
    )

    try:
        index = 0
        while True:
            try:
                devinfo = next_device_info(hdevinfo, index)
            except NoMoreItems:
                break

            interfaceinfo = get_device_interface(hdevinfo, guid.value, index)

            devpath = get_device_interface_devpath(hdevinfo, interfaceinfo)

            devid = get_device_instance_id(hdevinfo, devinfo)

            parent = get_device_property(hdevinfo, devinfo, DevPropKeys.Device_Parent)

            props : dict[DevProperties, str | int | bytes | None] = {}

            if properties == "all":
                properties = list(DevProperties)

            for prop_name in properties:
                try:
                    prop = get_device_registry_property(hdevinfo, devinfo, prop_name)
                    props[prop_name] = prop
                except InvalidData:
                    props[prop_name] = "N/A"
                except Exception as ex:
                    props[prop_name] = f"Error: {ex}"

            args = (
                devinfo.class_guid,
                interfaceinfo.interface_class_guid,
                devpath,
                devid,
                parent,
                props,
            )

            yield create_device(*args)

            index += 1
    finally:
        free_device_list(hdevinfo)
