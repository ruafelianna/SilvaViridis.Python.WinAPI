ERROR_INVALID_DATA = 13
ERROR_INSUFFICIENT_BUFFER = 122
ERROR_NO_MORE_ITEMS = 259
ERROR_NO_SUCH_DEVINST = -536870389 # 0xe000020b

class MemAllocError(Exception): pass

class WinAPIException(Exception):
    code : int

    def __str__(self) -> str:
        return f"WinAPIException {self.code} [{self.__class__.__name__}]"

class UnknownException(WinAPIException): pass

class InvalidData(WinAPIException): pass
class InsufficientBuffer(WinAPIException): pass
class NoMoreItems(WinAPIException): pass
class NoSuchDevInst(WinAPIException): pass

codes : dict[int, type[WinAPIException]] = {
    ERROR_INVALID_DATA: InvalidData,
    ERROR_INSUFFICIENT_BUFFER: InsufficientBuffer,
    ERROR_NO_MORE_ITEMS: NoMoreItems,
    ERROR_NO_SUCH_DEVINST: NoSuchDevInst,
}

def raise_ex(code : int):
    if code == 0:
        return
    ex_type = codes.get(code)
    ex = UnknownException() if ex_type is None else ex_type()
    ex.code = code
    raise ex
