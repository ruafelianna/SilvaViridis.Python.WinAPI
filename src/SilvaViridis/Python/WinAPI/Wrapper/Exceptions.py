from .Errors import (
    ERROR_INVALID_DATA,
    ERROR_INSUFFICIENT_BUFFER,
    ERROR_NO_MORE_ITEMS,
)

class MemAllocError(Exception): pass

class WinAPIException(Exception):
    code : int

    def __str__(self) -> str:
        return f"WinAPIException {self.code} [{self.__class__.__name__}]"

class UnknownException(WinAPIException): pass

class InvalidData(WinAPIException): pass
class InsufficientBuffer(WinAPIException): pass
class NoMoreItems(WinAPIException): pass

codes : dict[int, type[WinAPIException]] = {
    ERROR_INVALID_DATA: InvalidData,
    ERROR_INSUFFICIENT_BUFFER: InsufficientBuffer,
    ERROR_NO_MORE_ITEMS: NoMoreItems,
}

def raise_ex(code : int):
    if code == 0:
        return
    ex_type = codes.get(code)
    ex = UnknownException() if ex_type is None else ex_type()
    ex.code = code
    raise ex
