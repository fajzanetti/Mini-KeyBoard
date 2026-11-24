"""Lê e grava o mapeamento do mini teclado pela interface HID de configuração."""

import os

from . import codes, decoder, encoder, hid, mapping

VENDOR_ID = 0x1189
PRODUCT_IDS = (0x8840, 0x8842)
# A interface de configuração declara a usage page do fabricante.
VENDOR_USAGE_PAGE = 0xFF00

REPORT_ID = 0x03
REPORT_SIZE = 65
DEVICE_INFO = 0xFB
READ_LAYER = 0xFA
BIND = 0xFE
# O firmware só guarda uma tecla depois desta sequência.
FINISH = ((0xAA, 0xAA), (0xFD, 0xFE, 0xFF), (0xAA, 0xAA))
LED_ID = 0xB0
LED_KIND = 0x08

RESPONSE_TIMEOUT_MS = 200
# O mini teclado ignora às vezes o primeiro pedido depois de uma gravação.
INFO_ATTEMPTS = 3
FIRST_KNOB_ID = 16
# Os mini teclados de 4 knobs usam os ids 13 a 15 no quarto knob.
FOURTH_KNOB_ID = 13


class DeviceError(Exception):
    """A mensagem do erro vai para a tela."""


def read_mapping():
    """Retorna um mapeamento novo com as ações gravadas no mini teclado."""
    return _with_keyboard(_read)


def write_mapping(mapping_data):
    """Grava as ações e os modos de LED. A gravação mantém as posições vazias."""
    try:
        payloads = list(_payloads(mapping_data))
    except ValueError as error:
        raise DeviceError(str(error)) from error
    _with_keyboard(_send, payloads)


def _with_keyboard(operation, *arguments):
    try:
        with _open() as keyboard:
            return operation(keyboard, *arguments)
    except hid.HidError as error:
        raise DeviceError(f"A comunicação com o mini teclado falhou: {error}") from error


def _open():
    path = hid.find_path(VENDOR_ID, PRODUCT_IDS, VENDOR_USAGE_PAGE)
    if path is None:
        raise DeviceError("Conecte o mini teclado.")
    try:
        return hid.Device(path)
    except hid.HidError as error:
        # No Linux, o caminho é um arquivo e a regra udev libera o acesso a ele.
        if os.path.exists(path) and not os.access(path, os.W_OK):
            raise DeviceError(
                "O sistema negou o acesso. Instale a regra udev do README."
            ) from error
        raise


def _request(keyboard, *payload):
    keyboard.write(bytes([REPORT_ID, *payload]).ljust(REPORT_SIZE, b"\0"))


def _responses(keyboard):
    """O mini teclado não marca o fim da resposta, por isso o silêncio encerra a leitura."""
    while report := keyboard.read(REPORT_SIZE, RESPONSE_TIMEOUT_MS):
        yield report.ljust(REPORT_SIZE, b"\0")


def _read(keyboard):
    for _ in range(INFO_ATTEMPTS):
        _request(keyboard, DEVICE_INFO, 0xFB, 0xFB)
        info = next(_responses(keyboard), None)
        if info is not None:
            break
    else:
        raise DeviceError("O mini teclado não respondeu ao pedido de leitura.")
    keys, knobs = info[2], info[3]

    recorded = mapping.new_mapping(keys, knobs)
    for number, layer in enumerate(recorded["layers"], start=1):
        slots = _slots(layer)
        _request(keyboard, READ_LAYER, keys, knobs, number)
        for report in _responses(keyboard):
            slot = slots.get(report[2])
            if report[1] == READ_LAYER and report[3] == number and slot:
                container, key = slot
                action = decoder.action(report)
                # Uma ação que o app não consegue regravar aparece como posição vazia.
                container[key] = action if encoder.is_valid(action) else None
    return recorded


def _send(keyboard, payloads):
    for payload in payloads:
        _request(keyboard, *payload)


def _payloads(mapping_data):
    for number, layer in enumerate(mapping_data["layers"], start=1):
        for key_id, (container, key) in _slots(layer).items():
            if container[key]:
                yield from _bind_payloads(key_id, number, container[key])
        if layer.get("led"):
            led_code = encoder.led_code(layer["led"])
            yield (BIND, LED_ID, number, LED_KIND, 0, 0, 0, 0, 0, 1, 0, led_code)
            yield FINISH[1]


def _bind_payloads(key_id, layer_number, action):
    kind, data, delay = encoder.encode(action)
    yield (BIND, key_id, layer_number, kind, 0, 0, 0, 0, 0, *data)
    if delay:
        yield (BIND, key_id, layer_number, codes.DELAY, *delay.to_bytes(2, "little"))
    yield from FINISH


def _slots(layer):
    """Associa o id de cada tecla no protocolo ao par (container, chave) que guarda a ação."""
    slots = {}
    for row_index, row in enumerate(layer["buttons"]):
        for column_index in range(len(row)):
            slots[row_index * len(row) + column_index + 1] = (row, column_index)
    for knob_index, knob in enumerate(layer["knobs"]):
        first_id = FIRST_KNOB_ID + knob_index * len(mapping.KNOB_ACTIONS)
        if knob_index == 3:
            first_id = FOURTH_KNOB_ID
        for offset, knob_action in enumerate(mapping.KNOB_ACTIONS):
            slots[first_id + offset] = (knob, knob_action)
    return slots
