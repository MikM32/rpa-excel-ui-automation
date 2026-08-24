"""Prueba de integracion end-to-end (Casos 01 y 02 del README).

Requiere una maquina con Excel clasico (dialogos nativos). Se omite salvo
que se defina la variable de entorno RUN_EXCEL_INTEGRATION=1.
"""

import os
from pathlib import Path

import pytest

from rpa_excel_ui_automation import ExcelManager, FileExplorer

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_EXCEL_INTEGRATION") != "1",
    reason="Requiere Excel clasico y RUN_EXCEL_INTEGRATION=1",
)


def test_casos_01_y_02_end_to_end():
    base = Path(__file__).resolve().parent.parent
    source = base / ".data" / "input" / "origen.xlsx"
    destination = base / ".data" / "output" / "destino.xlsx"

    assert source.exists(), "Ejecuta antes: pdm run python scripts/create_sample.py"

    excel = ExcelManager()
    explorer = FileExplorer()

    excel.open_file()
    explorer.open_file(source)

    excel.save_as()
    explorer.save_file(destination)

    assert destination.exists(), "El archivo destino no se creo"