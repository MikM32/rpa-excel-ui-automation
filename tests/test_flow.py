"""Tests unitarios del orquestador run_flow (con mocks)."""

from pathlib import Path
from unittest import mock

from rpa_excel_ui_automation.flow import run_flow


class TestRunFlow:
    def test_ejecuta_los_cuatro_pasos_por_ui(self):
        with mock.patch("rpa_excel_ui_automation.flow.ExcelManager") as excel_cls, mock.patch(
            "rpa_excel_ui_automation.flow.FileExplorer"
        ) as explorer_cls:
            run_flow(Path("a.xlsx"), Path("b.xlsx"))

        excel_cls.return_value.open_file.assert_called_once()
        excel_cls.return_value.save_as.assert_called_once()
        explorer_cls.return_value.open_file.assert_called_once_with(Path("a.xlsx"))
        explorer_cls.return_value.save_file.assert_called_once_with(Path("b.xlsx"))