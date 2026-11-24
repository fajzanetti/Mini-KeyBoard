import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gdk, Gtk  # noqa: E402

from .window import MainWindow  # noqa: E402

STYLE_PATH = Path(__file__).with_name("style.css")


def load_style():
    provider = Gtk.CssProvider()
    provider.load_from_path(str(STYLE_PATH))
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )


def main():
    app = Adw.Application(application_id="local.MiniKeyboard")
    app.connect("startup", lambda _application: load_style())
    app.connect("activate", lambda application: MainWindow(application).present())
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
