# Receita do PyInstaller. Ela gera um executável único com o GTK4 e a libadwaita embutidos.
import sys
from pathlib import Path

root = Path(SPECPATH).parent

binaries = []
if sys.platform == "win32":
    # No Linux, o app usa a hidapi do sistema. No Windows, ela vai dentro do executável.
    binaries.append((str(Path(sys.prefix) / "bin" / "libhidapi-0.dll"), "."))

analysis = Analysis(
    [str(root / "packaging" / "launcher.py")],
    pathex=[str(root)],
    binaries=binaries,
    datas=[(str(root / "mini_keyboard" / "style.css"), "mini_keyboard")],
    hooksconfig={
        "gi": {
            "module-versions": {"Gtk": "4.0", "Gdk": "4.0"},
            "icons": ["Adwaita", "hicolor"],
            "languages": ["pt_BR", "pt"],
        },
    },
)

EXE(
    PYZ(analysis.pure),
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    name="MiniKeyboard",
    console=False,
)
