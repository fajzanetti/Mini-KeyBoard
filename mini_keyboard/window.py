"""Janela principal: mostra o mini teclado, lê e grava o mapeamento."""

from gi.repository import Adw, Gtk

from . import device, encoder, mapping
from .board import layer_board
from .editor import ActionEditor
from .led import LedSelector


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application, title="Mini Keyboard", resizable=False)
        self._mapping = mapping.load()
        self._layer_index = 0

        read = Gtk.Button(icon_name="view-refresh-symbolic", tooltip_text="Ler do teclado")
        read.connect("clicked", self._on_read)

        upload = Gtk.Button(label="Gravar no teclado", css_classes=["suggested-action"])
        upload.connect("clicked", self._on_upload)

        header = Adw.HeaderBar(title_widget=self._layer_switcher())
        header.pack_start(read)
        header.pack_end(upload)

        # O aviso fica na tela enquanto o app mostra o mapeamento salvo em vez do gravado.
        self._read_error = Adw.Banner(button_label="Ler novamente")
        self._read_error.connect("button-clicked", self._on_read)

        self._content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=24,
            margin_top=24,
            margin_bottom=24,
            margin_start=24,
            margin_end=24,
        )
        self._toasts = Adw.ToastOverlay(child=self._content)

        view = Adw.ToolbarView(content=self._toasts)
        view.add_top_bar(header)
        view.add_top_bar(self._read_error)
        self.set_content(view)
        self._on_read()

    def _layer_switcher(self):
        switcher = Gtk.Box(css_classes=["linked"])
        first = None
        for index in range(len(self._mapping["layers"])):
            button = Gtk.ToggleButton(label=f"Camada {index + 1}", group=first, active=not index)
            button.connect("toggled", self._on_layer_toggled, index)
            first = first or button
            switcher.append(button)
        return switcher

    def _on_layer_toggled(self, button, index):
        if button.get_active():
            self._layer_index = index
            self._show_layer()

    def _show_layer(self):
        while child := self._content.get_first_child():
            self._content.remove(child)
        layer = self._mapping["layers"][self._layer_index]
        self._content.append(layer_board(layer, self._on_slot_clicked))
        self._content.append(LedSelector(layer.get("led"), lambda led: self._set_led(layer, led)))

    def _set_led(self, layer, led):
        layer["led"] = led
        mapping.save(self._mapping)

    def _on_slot_clicked(self, slot):
        def apply(action):
            slot.container[slot.key] = action
            slot.refresh()
            mapping.save(self._mapping)

        editor = ActionEditor(
            slot.title,
            slot.container[slot.key],
            is_valid=encoder.is_valid,
            on_apply=apply,
        )
        editor.present(self)

    def _on_read(self, _widget=None):
        error = self._read_keyboard()
        self._read_error.set_title(error or "")
        self._read_error.set_revealed(bool(error))
        self._show_layer()

    def _read_keyboard(self):
        """Mantém o mapeamento salvo e retorna o erro quando a leitura falha."""
        try:
            recorded = device.read_mapping()
        except device.DeviceError as error:
            return str(error)
        # O mini teclado não informa o modo de LED, por isso o modo salvo continua.
        for saved, layer in zip(self._mapping["layers"], recorded["layers"]):
            layer["led"] = saved.get("led")
        self._mapping = recorded
        mapping.save(recorded)
        return None

    def _on_upload(self, _button):
        try:
            device.write_mapping(self._mapping)
        except device.DeviceError as error:
            dialog = Adw.AlertDialog(heading="A gravação falhou", body=str(error))
            dialog.add_response("close", "Fechar")
            dialog.present(self)
        else:
            self._toasts.add_toast(Adw.Toast(title="Mapeamento gravado no teclado."))
