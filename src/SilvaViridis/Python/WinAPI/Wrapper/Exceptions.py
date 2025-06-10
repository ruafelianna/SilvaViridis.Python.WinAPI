from .Errors import (
    ERROR_INSUFFICIENT_BUFFER,
    ERROR_NO_MORE_ITEMS,
)

class MemAllocError(Exception): pass

class WinAPIException(Exception):
    code : int

class UnknownException(WinAPIException): pass

class InsufficientBuffer(WinAPIException): pass
class NoMoreItems(WinAPIException): pass

codes : dict[int, type[WinAPIException]] = {
    ERROR_INSUFFICIENT_BUFFER: InsufficientBuffer,
    ERROR_NO_MORE_ITEMS: NoMoreItems,
}

def raise_ex(code : int):
    ex_type = codes.get(code)
    ex = UnknownException() if ex_type is None else ex_type()
    ex.code = code
    raise ex
