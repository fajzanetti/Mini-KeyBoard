"""Diálogo que edita a ação de uma tecla ou do knob."""

from gi.repository import Adw, Gtk

from . import keys

SYNTAX_HINT = "Exemplos: ctrl-c · ctrl-shift-t · a,b,c · play · wheelup"


class ActionEditor(Adw.AlertDialog):
    def __init__(self, title, action, is_valid, on_apply):
        super().__init__(heading=title)
        self._is_valid = is_valid
        self._on_apply = on_apply

        self._entry = Gtk.Entry(
            text=action or "",
            placeholder_text="Vazio: mantém a ação gravada no teclado",
            activates_default=True,
        )
        self._entry.connect("changed", self._on_changed)

        self._capture = Gtk.ToggleButton(label="Capturar atalho")
        self._capture.connect("toggled", self._on_capture_toggled)

        labels = ["Ações prontas…", *(label for label, _ in keys.PRESETS)]
        self._presets = Gtk.DropDown.new_from_strings(labels)
        self._presets.connect("notify::selected", self._on_preset_selected)

        buttons = Gtk.Box(spacing=8, homogeneous=True)
        buttons.append(self._capture)
        buttons.append(self._presets)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.append(self._entry)
        content.append(buttons)
        content.append(Gtk.Label(label=SYNTAX_HINT, css_classes=["dim-label", "caption"]))
        self.set_extra_child(content)

        # A fase de captura recebe Esc e Tab antes do diálogo.
        controller = Gtk.EventControllerKey(propagation_phase=Gtk.PropagationPhase.CAPTURE)
        controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(controller)

        self.add_response("cancel", "Cancelar")
        self.add_response("apply", "Aplicar")
        self.set_response_appearance("apply", Adw.ResponseAppearance.SUGGESTED)
        self.set_default_response("apply")
        self.set_close_response("cancel")
        self.connect("response::apply", self._on_apply_response)

    def _action(self):
        return self._entry.get_text().strip() or None

    def _on_changed(self, _entry):
        valid = self._is_valid(self._action())
        self.set_response_enabled("apply", valid)
        if valid:
            self._entry.remove_css_class("error")
        else:
            self._entry.add_css_class("error")

    def _on_capture_toggled(self, button):
        button.set_label("Pressione o atalho…" if button.get_active() else "Capturar atalho")

    def _on_key_pressed(self, _controller, _keyval, keycode, state):
        if not self._capture.get_active():
            return False
        shortcut = keys.shortcut_from_event(keycode, state)
        if shortcut:
            self._entry.set_text(shortcut)
            self._capture.set_active(False)
        return True

    def _on_preset_selected(self, dropdown, _param):
        selected = dropdown.get_selected()
        if selected > 0:
            self._entry.set_text(keys.PRESETS[selected - 1][1])
            dropdown.set_selected(0)

    def _on_apply_response(self, _dialog, _response):
        self._on_apply(self._action())
