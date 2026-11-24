"""Seletor do modo de LED de uma camada."""

from itertools import product

from gi.repository import Adw, Gtk

from . import codes

# Cada modo tem o rótulo, o texto salvo no mapeamento e a indicação de que ele usa uma cor.
MODES = (
    ("Não alterar", None, False),
    ("Desligado", "off", False),
    ("Luz de fundo branca", "backlight white", False),
    ("Luz de fundo colorida", "backlight", True),
    ("Shock ao pressionar", "shock", True),
    ("Shock 2 ao pressionar", "shock2", True),
    ("Tecla pressionada acesa", "press", True),
)

# O nome da cor no protocolo também é a classe CSS da amostra.
COLOR_LABELS = ("Vermelho", "Laranja", "Amarelo", "Verde", "Ciano", "Azul", "Roxo")
COLORS = tuple(zip(COLOR_LABELS, codes.LED_COLORS))


def _led(mode_index, color_index):
    _, mode, has_color = MODES[mode_index]
    return f"{mode} {COLORS[color_index][1]}" if has_color else mode


def _indexes(led):
    for mode_index, color_index in product(range(len(MODES)), range(len(COLORS))):
        if _led(mode_index, color_index) == led:
            return mode_index, color_index
    return 0, 0


class LedSelector(Gtk.ListBox):
    def __init__(self, led, on_change):
        super().__init__(selection_mode=Gtk.SelectionMode.NONE, css_classes=["boxed-list"])
        mode_index, color_index = _indexes(led)

        self._modes = Adw.ComboRow(
            title="LED da camada",
            model=Gtk.StringList.new([label for label, *_ in MODES]),
            selected=mode_index,
        )
        self._modes.connect("notify::selected", self._on_selected, on_change)
        self.append(self._modes)

        swatches = Gtk.Box(spacing=10, valign=Gtk.Align.CENTER)
        self._swatches = []
        for label, color in COLORS:
            swatch = Gtk.ToggleButton(tooltip_text=label, css_classes=["swatch", color])
            swatch.update_property([Gtk.AccessibleProperty.LABEL], [label])
            if self._swatches:
                swatch.set_group(self._swatches[0])
            self._swatches.append(swatch)
            swatches.append(swatch)
        self._swatches[color_index].set_active(True)
        for swatch in self._swatches:
            swatch.connect("toggled", self._on_selected, None, on_change)

        self._color = Adw.ActionRow(title="Cor do LED", sensitive=MODES[mode_index][2])
        self._color.add_suffix(swatches)
        self.append(self._color)

    def _on_selected(self, widget, _param, on_change):
        # O grupo emite `toggled` duas vezes por troca. Só a amostra ativa conta.
        if widget in self._swatches and not widget.get_active():
            return
        mode_index = self._modes.get_selected()
        color_index = next(i for i, swatch in enumerate(self._swatches) if swatch.get_active())
        self._color.set_sensitive(MODES[mode_index][2])
        on_change(_led(mode_index, color_index))
