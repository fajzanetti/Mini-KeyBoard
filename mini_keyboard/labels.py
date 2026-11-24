"""Converte uma ação da sintaxe do ch57x-keyboard-tool para o texto da tela."""

import re

from . import keys

EMPTY = "—"
PRESET_LABELS = {action: label for label, action in keys.PRESETS}
TOKEN_LABELS = {
    "ctrl": "Ctrl",
    "shift": "Shift",
    "alt": "Alt",
    "win": "Super",
    "rctrl": "Ctrl dir.",
    "rshift": "Shift dir.",
    "ralt": "Alt dir.",
    "rwin": "Super dir.",
    "escape": "Esc",
    "space": "Espaço",
    "pageup": "Page Up",
    "pagedown": "Page Down",
    "printscreen": "Print Screen",
}
# As ações de mouse e as opções usam parênteses e chaves. A tela mostra a sintaxe delas.
CHORDS = re.compile(r"[a-z0-9]+(?:[-,][a-z0-9]+)*")


def describe(action):
    if action is None:
        return EMPTY
    if not CHORDS.fullmatch(action):
        return action
    chords = (chord.split("-") for chord in action.split(","))
    return ", ".join(" + ".join(_token_label(token) for token in chord) for chord in chords)


def _token_label(token):
    label = TOKEN_LABELS.get(token) or PRESET_LABELS.get(token)
    if label:
        return label
    if token.startswith("numpad"):
        return f"Num {token.removeprefix('numpad').capitalize()}"
    return token.capitalize()
