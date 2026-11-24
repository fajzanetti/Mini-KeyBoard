"""Acesso HID pela biblioteca hidapi, com o mesmo código no Linux e no Windows."""

import ctypes
import sys

LIBRARY_NAMES = {"linux": "libhidapi-hidraw.so.0", "win32": "libhidapi-0.dll"}


class HidError(Exception):
    pass


class _DeviceInfo(ctypes.Structure):
    pass


# Os campos seguem a ordem de `struct hid_device_info` da hidapi.
_DeviceInfo._fields_ = [
    ("path", ctypes.c_char_p),
    ("vendor_id", ctypes.c_ushort),
    ("product_id", ctypes.c_ushort),
    ("serial_number", ctypes.c_wchar_p),
    ("release_number", ctypes.c_ushort),
    ("manufacturer_string", ctypes.c_wchar_p),
    ("product_string", ctypes.c_wchar_p),
    ("usage_page", ctypes.c_ushort),
    ("usage", ctypes.c_ushort),
    ("interface_number", ctypes.c_int),
    ("next", ctypes.POINTER(_DeviceInfo)),
]


def _load():
    try:
        library = ctypes.CDLL(LIBRARY_NAMES[sys.platform])
    except (KeyError, OSError) as error:
        raise HidError("O app não encontrou a biblioteca hidapi.") from error
    library.hid_enumerate.restype = ctypes.POINTER(_DeviceInfo)
    library.hid_enumerate.argtypes = [ctypes.c_ushort, ctypes.c_ushort]
    library.hid_free_enumeration.argtypes = [ctypes.POINTER(_DeviceInfo)]
    library.hid_open_path.restype = ctypes.c_void_p
    library.hid_open_path.argtypes = [ctypes.c_char_p]
    library.hid_write.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
    library.hid_read_timeout.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_size_t,
        ctypes.c_int,
    ]
    library.hid_close.argtypes = [ctypes.c_void_p]
    library.hid_error.restype = ctypes.c_wchar_p
    library.hid_error.argtypes = [ctypes.c_void_p]
    library.hid_init()
    return library


_library = None


def _hidapi():
    global _library
    if _library is None:
        _library = _load()
    return _library


def find_path(vendor_id, product_ids, usage_page):
    """Retorna o caminho da primeira interface com a usage page pedida, ou None."""
    first = _hidapi().hid_enumerate(vendor_id, 0)
    try:
        node = first
        while node:
            info = node.contents
            if info.product_id in product_ids and info.usage_page == usage_page:
                return info.path
            node = info.next
        return None
    finally:
        _hidapi().hid_free_enumeration(first)


class Device:
    def __init__(self, path):
        self._handle = _hidapi().hid_open_path(path)
        if not self._handle:
            raise HidError(_hidapi().hid_error(None))

    def __enter__(self):
        return self

    def __exit__(self, *_exception):
        _hidapi().hid_close(self._handle)

    def write(self, report):
        if _hidapi().hid_write(self._handle, report, len(report)) < 0:
            raise HidError(_hidapi().hid_error(self._handle))

    def read(self, size, timeout_ms):
        """Retorna bytes vazios quando o tempo acaba sem resposta."""
        buffer = ctypes.create_string_buffer(size)
        length = _hidapi().hid_read_timeout(self._handle, buffer, size, timeout_ms)
        if length < 0:
            raise HidError(_hidapi().hid_error(self._handle))
        return buffer.raw[:length]
