"""Mapeamento das teclas no formato YAML do ch57x-keyboard-tool."""

from pathlib import Path

import yaml
from gi.repository import GLib

LAYERS = 3
KNOB_ACTIONS = ("ccw", "press", "cw")
# O mini teclado informa só o número de teclas. A tabela dá as linhas e as colunas.
GRIDS = {6: (2, 3), 9: (3, 3), 12: (3, 4), 15: (3, 5)}

MAPPING_PATH = Path(GLib.get_user_config_dir()) / "mini-keyboard" / "mapping.yaml"


def new_mapping(keys=6, knobs=1):
    # Um número de teclas fora da tabela vira uma linha única, com todas as teclas.
    rows, columns = GRIDS.get(keys, (1, keys))
    # None mantém a ação ou o modo de LED que já está gravado no teclado.
    return {
        "model": "ch57x-1",
        "orientation": "normal",
        "rows": rows,
        "columns": columns,
        "knobs": knobs,
        "layers": [
            {
                "buttons": [[None] * columns for _ in range(rows)],
                "knobs": [dict.fromkeys(KNOB_ACTIONS) for _ in range(knobs)],
                "led": None,
            }
            for _ in range(LAYERS)
        ],
    }


def dump(mapping):
    return yaml.safe_dump(mapping, sort_keys=False, allow_unicode=True)


def load():
    if not MAPPING_PATH.exists():
        return new_mapping()
    return yaml.safe_load(MAPPING_PATH.read_text(encoding="utf-8"))


def save(mapping):
    MAPPING_PATH.parent.mkdir(parents=True, exist_ok=True)
    MAPPING_PATH.write_text(dump(mapping), encoding="utf-8")
