"""Orquestacion del flujo RPA por UI (Casos 01 y 02 del README)."""

import logging

from pathlib import Path

from rpa_excel_ui_automation.excel_manager import ExcelManager
from rpa_excel_ui_automation.file_explorer import FileExplorer

logger = logging.getLogger(__name__)


def run_flow(source: Path, destination: Path) -> None:
    """Ejecuta los Casos 01 y 02 usando unicamente UI Automation.

    ExcelManager despliega los dialogos nativos ('Abrir'/'Guardar como');
    en Excel 365, donde los atajos abren el Backstage, presiona 'Browse'
    para alcanzar el mismo dialogo nativo. FileExplorer opera el dialogo.
    """
    excel = ExcelManager()
    explorer = FileExplorer()

    excel.open_file()
    explorer.open_file(source)

    excel.save_as()
    explorer.save_file(destination)

    logger.info("run_flow: flujo por UI completado")