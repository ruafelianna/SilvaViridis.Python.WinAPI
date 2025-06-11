ERROR_INVALID_DATA = 13
ERROR_INSUFFICIENT_BUFFER = 122
ERROR_NO_MORE_ITEMS = 259

APP_ERROR_MASK = 0x20000000

ERROR_SEVERITY_SUCCESS = 0x00000000
ERROR_SEVERITY_INFORMATIONAL = 0x40000000
ERROR_SEVERITY_WARNING = 0x80000000
ERROR_SEVERITY_ERROR = 0xc0000000

def devinstaller_error(code : int):
    return (APP_ERROR_MASK | ERROR_SEVERITY_ERROR | code) - 0x100000000

ERROR_INVALID_REG_PROPERTY = devinstaller_error(0x209)
ERROR_NO_SUCH_DEVINST = devinstaller_error(0x20b)
ERROR_INVALID_CLASS_INSTALLER = devinstaller_error(0x20d)

class MemAllocError(Exception): pass

class WinAPIException(Exception):
    code : int

    def __str__(self) -> str:
        return f"WinAPIException {self.code} [{self.__class__.__name__}]"

class UnknownException(WinAPIException): pass

class InvalidData(WinAPIException): pass
class InsufficientBuffer(WinAPIException): pass
class NoMoreItems(WinAPIException): pass
class InvalidRegProperty(WinAPIException): pass
class NoSuchDevInst(WinAPIException): pass
class InvalidClassInstaller(WinAPIException): pass

codes : dict[int, type[WinAPIException]] = {
    ERROR_INVALID_DATA: InvalidData,
    ERROR_INSUFFICIENT_BUFFER: InsufficientBuffer,
    ERROR_NO_MORE_ITEMS: NoMoreItems,
    ERROR_INVALID_REG_PROPERTY: InvalidRegProperty,
    ERROR_NO_SUCH_DEVINST: NoSuchDevInst,
    ERROR_INVALID_CLASS_INSTALLER: InvalidClassInstaller,
}

def raise_ex(code : int):
    if code == 0:
        return
    ex_type = codes.get(code)
    ex = UnknownException() if ex_type is None else ex_type()
    ex.code = code
    raise ex
