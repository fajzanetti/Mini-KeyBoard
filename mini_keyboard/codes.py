"""Nomes e códigos das ações, na sintaxe criada pelo ch57x-keyboard-tool."""

FIRST_KEY_CODE = 0x04

# A ordem segue os códigos HID de teclado, a partir de FIRST_KEY_CODE.
KEY_NAMES = (
    *"abcdefghijklmnopqrstuvwxyz1234567890",
    *("enter", "escape", "backspace", "tab", "space", "minus", "equal"),
    *("leftbracket", "rightbracket", "backslash", "nonushash", "semicolon", "quote"),
    *("grave", "comma", "dot", "slash", "capslock"),
    *(f"f{n}" for n in range(1, 13)),
    *("printscreen", "scrolllock", "pause", "insert", "home", "pageup", "delete"),
    *("end", "pagedown", "right", "left", "down", "up", "numlock"),
    *("numpadslash", "numpadasterisk", "numpadminus", "numpadplus", "numpadenter"),
    *(f"numpad{n}" for n in (*range(1, 10), 0)),
    *("numpaddot", "nonusbackslash", "application", "power", "numpadequal"),
    *(f"f{n}" for n in range(13, 25)),
)

# A posição de cada nome nestas tuplas é o bit dele no relatório.
MODIFIERS = ("ctrl", "shift", "alt", "win", "rctrl", "rshift", "ralt", "rwin")
MOUSE_MODIFIERS = ("ctrl", "shift", "alt")
MOUSE_BUTTONS = ("left", "right", "middle")
CLICKS = ("click", "rclick", "mclick")

MEDIA_NAMES = {
    0xB5: "next",
    0xB6: "previous",
    0xB7: "stop",
    0xCD: "play",
    0xE2: "mute",
    0xE9: "volumeup",
    0xEA: "volumedown",
    0x182: "favorites",
    0x192: "calculator",
    0x19E: "screenlock",
}

# Nomes alternativos que a sintaxe aceita.
ALIASES = {
    "opt": "alt",
    "cmd": "win",
    "ropt": "ralt",
    "rcmd": "rwin",
    "prev": "previous",
    "lclick": "click",
    "macbrightnessdown": "scrolllock",
    "macbrightnessup": "pause",
}

LED_MODES = {"off": 0, "backlight": 1, "shock": 2, "shock2": 3, "press": 4}
LED_WHITE_BACKLIGHT = 5
# O código de cada cor é a posição dela mais 1.
LED_COLORS = ("red", "orange", "yellow", "green", "cyan", "blue", "purple")

KEYBOARD, MEDIA, MOUSE, DELAY = 1, 2, 3, 5
MAX_PRESSES = 18
MAX_DELAY = 6000
