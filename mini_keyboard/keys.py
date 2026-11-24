"""Converte teclas pressionadas para a sintaxe do ch57x-keyboard-tool."""

from gi.repository import Gdk


def _sequence(first_code, names):
    return {first_code + offset: name for offset, name in enumerate(names)}


# O mini teclado envia a posição física da tecla, por isso a tabela usa o código evdev.
KEY_NAMES = {
    **_sequence(1, ["escape", *"1234567890", "minus", "equal", "backspace", "tab"]),
    **_sequence(16, [*"qwertyuiop", "leftbracket", "rightbracket", "enter"]),
    **_sequence(30, [*"asdfghjkl", "semicolon", "quote", "grave"]),
    **_sequence(43, ["backslash", *"zxcvbnm", "comma", "dot", "slash"]),
    55: "numpadasterisk",
    57: "space",
    58: "capslock",
    **_sequence(59, [f"f{n}" for n in range(1, 11)]),
    69: "numlock",
    **_sequence(71, ["numpad7", "numpad8", "numpad9", "numpadminus"]),
    **_sequence(75, ["numpad4", "numpad5", "numpad6", "numpadplus"]),
    **_sequence(79, ["numpad1", "numpad2", "numpad3", "numpad0", "numpaddot"]),
    86: "nonusbackslash",
    87: "f11",
    88: "f12",
    96: "numpadenter",
    98: "numpadslash",
    99: "printscreen",
    **_sequence(102, ["home", "up", "pageup", "left", "right", "end", "down"]),
    **_sequence(109, ["pagedown", "insert", "delete"]),
    117: "numpadequal",
    127: "application",
    **_sequence(183, [f"f{n}" for n in range(13, 25)]),
    # Teclas extras do ABNT2: a sintaxe só aceita o código HID delas.
    89: "<135>",
    121: "<133>",
}

MODIFIERS = (
    (Gdk.ModifierType.CONTROL_MASK, "ctrl"),
    (Gdk.ModifierType.SHIFT_MASK, "shift"),
    (Gdk.ModifierType.ALT_MASK, "alt"),
    (Gdk.ModifierType.SUPER_MASK, "win"),
)

PRESETS = (
    ("Tocar / pausar", "play"),
    ("Próxima faixa", "next"),
    ("Faixa anterior", "previous"),
    ("Parar", "stop"),
    ("Mudo", "mute"),
    ("Aumentar volume", "volumeup"),
    ("Diminuir volume", "volumedown"),
    ("Calculadora", "calculator"),
    ("Bloquear tela", "screenlock"),
    ("Clique esquerdo", "click"),
    ("Clique direito", "rclick"),
    ("Clique do meio", "mclick"),
    ("Rolar para cima", "wheelup"),
    ("Rolar para baixo", "wheeldown"),
)


def shortcut_from_event(keycode, state):
    """Retorna None enquanto o usuário segura apenas modificadores."""
    # O GDK soma 8 ao código evdev.
    name = KEY_NAMES.get(keycode - 8)
    if name is None:
        return None
    held = [modifier for mask, modifier in MODIFIERS if state & mask]
    return "-".join([*held, name])
