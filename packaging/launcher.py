"""Ponto de entrada do executável: o PyInstaller precisa de um script fora do pacote."""

import sys

from mini_keyboard.__main__ import main

sys.exit(main())
