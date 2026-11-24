"""Converte um relatório de leitura do mini teclado para a sintaxe das ações."""

import struct

from . import codes

WHEELS = {1: "wheelup", -1: "wheeldown"}


def action(report):
    """Retorna None quando a posição está vazia ou a sintaxe não cobre a ação."""
    decoders = {codes.KEYBOARD: _keyboard, codes.MEDIA: _media, codes.MOUSE: _mouse}
    decode = decoders.get(report[4])
    return decode(report) if decode else None


def _set_bits(value, names):
    return [name for bit, name in enumerate(names) if value >> bit & 1]


def _key_name(code):
    index = code - codes.FIRST_KEY_CODE
    if 0 <= index < len(codes.KEY_NAMES):
        return codes.KEY_NAMES[index]
    return f"<{code}>"


def _keyboard(report):
    # A gravação usa a contagem 0 quando a ação é um modificador sozinho.
    count = min(max(report[10], 1), codes.MAX_PRESSES)
    presses = []
    for index in range(count):
        modifiers, code = report[11 + 2 * index : 13 + 2 * index]
        parts = _set_bits(modifiers, codes.MODIFIERS)
        if code:
            parts.append(_key_name(code))
        if parts:
            presses.append("-".join(parts))
    if not presses:
        return None
    delay = int.from_bytes(report[5:7], "big")
    options = f"{{delay({delay})}}" if delay else ""
    return options + ",".join(presses)


def _media(report):
    return codes.MEDIA_NAMES.get(int.from_bytes(report[11:13], "little"))


def _mouse(report):
    modifier, buttons, dx, dy, wheel = struct.unpack_from("BBbbb", report, 11)
    held = _set_bits(modifier, codes.MOUSE_MODIFIERS)
    if wheel:
        event = WHEELS.get(wheel, f"wheel({wheel})")
    elif dx or dy:
        pressed = "+".join(_set_bits(buttons, codes.MOUSE_BUTTONS))
        event = f"drag({pressed},{dx},{dy})" if pressed else f"move({dx},{dy})"
    else:
        event = "+".join(_set_bits(buttons, codes.CLICKS))
    # A sintaxe aceita um único modificador em ações de mouse.
    if len(held) > 1 or not event:
        return None
    return "-".join([*held, event])
