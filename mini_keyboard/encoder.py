"""Converte uma ação da sintaxe para os dados que o mini teclado grava."""

import re

from . import codes

INVALID = (ValueError, LookupError)


def encode(action):
    """Retorna o tipo, os dados e o delay da ação. Levanta ValueError para sintaxe inválida."""
    for parse in (_mouse, _media, _keyboard):
        try:
            return parse(action)
        except INVALID:
            continue
    raise ValueError(f"A ação {action!r} tem sintaxe inválida.")


def is_valid(action):
    """Uma posição vazia (None) é válida: a gravação não toca nela."""
    if action is None:
        return True
    try:
        encode(action)
    except ValueError:
        return False
    return True


def led_code(led):
    if led == "backlight white":
        return codes.LED_WHITE_BACKLIGHT
    mode, _, color = led.partition(" ")
    try:
        if mode == "off" and not color:
            return codes.LED_MODES[mode]
        return (codes.LED_COLORS.index(color) + 1) << 4 | codes.LED_MODES[mode]
    except INVALID as error:
        raise ValueError(f"O modo de LED {led!r} é inválido.") from error


def _groups(pattern, text):
    match = re.fullmatch(pattern, text)
    if match is None:
        raise ValueError(text)
    return match.groups()


def _name(text):
    lowered = text.lower()
    return codes.ALIASES.get(lowered, lowered)


def _bits(names, table):
    mask = 0
    for name in names:
        mask |= 1 << table.index(_name(name))
    return mask


def _delta(text):
    value = int(*_groups(r"(-?\d+)", text))
    if not -128 <= value <= 127:
        raise ValueError(text)
    return value & 0xFF


def _mouse(action):
    modifier, event = _groups(r"(?:([A-Za-z]+)-)?(.+)", action)
    held = _bits([modifier] if modifier else [], codes.MOUSE_MODIFIERS)
    if event in ("wheelup", "wheeldown"):
        event = "wheel(1)" if event == "wheelup" else "wheel(-1)"
    name, arguments = _groups(r"([a-z+]+)(?:\((.*)\))?", event)
    if arguments is None:
        data = [1, held, _bits(name.split("+"), codes.CLICKS)]
    elif name == "click":
        data = [1, held, _bits(arguments.split("+"), codes.MOUSE_BUTTONS)]
    elif name == "wheel":
        data = [3, held, 0, 0, 0, _delta(arguments)]
    elif name == "move":
        dx, dy = arguments.split(",")
        data = [5, held, 0, _delta(dx), _delta(dy)]
    elif name == "drag":
        buttons, dx, dy = arguments.split(",")
        data = [5, held, _bits(buttons.split("+"), codes.MOUSE_BUTTONS), _delta(dx), _delta(dy)]
    else:
        raise ValueError(event)
    return codes.MOUSE, bytes(data), 0


def _media(action):
    names = {name: code for code, name in codes.MEDIA_NAMES.items()}
    return codes.MEDIA, bytes([0, *names[_name(action)].to_bytes(2, "little")]), 0


def _key_code(text):
    if text.startswith("<"):
        return bytes([int(*_groups(r"<(\d+)>", text))])[0]
    return codes.KEY_NAMES.index(_name(text)) + codes.FIRST_KEY_CODE


def _press(text):
    """Um acorde tem modificadores e termina em uma tecla ou em um modificador."""
    *modifiers, last = text.split("-")
    if _name(last) in codes.MODIFIERS:
        return _bits([*modifiers, last], codes.MODIFIERS), 0
    return _bits(modifiers, codes.MODIFIERS), _key_code(last)


def _keyboard(action):
    delay, sequence = _groups(r"(?:\{(?:delay\((\d+)\))?\})?(.+)", action)
    presses = [_press(text) for text in sequence.split(",")]
    delay = int(delay or 0)
    if len(presses) > codes.MAX_PRESSES or delay > codes.MAX_DELAY:
        raise ValueError(action)
    # O firmware espera a contagem 0 quando a ação é um modificador sozinho.
    count = 0 if presses == [(presses[0][0], 0)] else len(presses)
    return codes.KEYBOARD, bytes([count, *(byte for press in presses for byte in press)]), delay
