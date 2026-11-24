"""Desenha as teclas e os knobs de uma camada, na posição que eles têm no mini teclado."""

from gi.repository import Gtk, Pango

from . import labels

KNOB_LABELS = {"ccw": "Girar ↺", "press": "Pressionar", "cw": "Girar ↻"}


class Slot(Gtk.Button):
    """`container[key]` guarda a ação, tanto para tecla (lista) quanto para knob (dict)."""

    def __init__(self, title, caption, container, key, shape):
        super().__init__(css_classes=["slot", shape])
        self.title = title
        self.container = container
        self.key = key

        self._action = Gtk.Label(
            css_classes=["heading"],
            vexpand=True,
            wrap=True,
            lines=2,
            max_width_chars=13,
            justify=Gtk.Justification.CENTER,
            ellipsize=Pango.EllipsizeMode.END,
        )
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.append(Gtk.Label(label=caption, css_classes=["caption", "dim-label"], xalign=0))
        content.append(self._action)
        self.set_child(content)
        self.refresh()

    def refresh(self):
        action = self.container[self.key]
        self._action.set_label(labels.describe(action))
        # A dica mostra a sintaxe que o app grava.
        self.set_tooltip_text(action)
        if action:
            self.remove_css_class("empty")
        else:
            self.add_css_class("empty")


def layer_board(layer, on_slot_clicked):
    grid = Gtk.Grid(row_spacing=14, column_spacing=12)
    for row_index, row in enumerate(layer["buttons"]):
        for column_index in range(len(row)):
            number = row_index * len(row) + column_index + 1
            slot = Slot(f"Tecla {number}", str(number), row, column_index, "keycap")
            slot.connect("clicked", on_slot_clicked)
            grid.attach(slot, column_index, row_index, 1, 1)

    board = Gtk.Box(spacing=20, halign=Gtk.Align.CENTER, css_classes=["board"])
    board.append(grid)
    for number, knob in enumerate(layer["knobs"], start=1):
        column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14, homogeneous=True)
        for key, label in KNOB_LABELS.items():
            slot = Slot(f"Knob {number}: {label}", label, knob, key, "knob")
            slot.connect("clicked", on_slot_clicked)
            column.append(slot)
        board.append(column)
    return board
