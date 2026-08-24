"""Tests unitarios de ExcelManager (con mocks, no requieren Excel)."""

from unittest import mock

import pytest

from rpa_excel_ui_automation import ExcelManager
from rpa_excel_ui_automation.excel_manager import (
    HOTKEY_RETRIES,
    LAUNCH_TIMEOUT,
    WINDOW_SEARCH_TIMEOUT,
)


class FakeWindow:
    def __init__(self, exists=True):
        self._exists = exists
        self.NativeWindowHandle = 999
        self.Name = "Book1 - Excel"
        self.sent = []
        self.activations = 0

    def Exists(self, timeout, *args, **kwargs):
        return self._exists

    def SetActive(self):
        self.activations += 1
        return True

    def SendKeys(self, text, **kwargs):
        self.sent.append(text)


class TestExcelManager:
    def test_open_file_envia_ctrl_o_y_activa_la_ventana(self):
        window = FakeWindow()
        dialog = mock.Mock()
        with mock.patch(
            "rpa_excel_ui_automation.excel_manager.auto.WindowControl",
            return_value=window,
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.find_dialog", return_value=dialog
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.auto.SetForegroundWindow"
        ) as set_fg, mock.patch(
            "rpa_excel_ui_automation.excel_manager.auto.SwitchToThisWindow"
        ) as switch:
            manager = ExcelManager()
            manager.open_file()

        assert window.sent == ["{Ctrl}o"]
        assert window.activations == 1
        set_fg.assert_called_once_with(999)
        switch.assert_called_once_with(999)

    def test_open_file_presiona_browse_cuando_aparece_el_backstage(self):
        window = FakeWindow()
        dialog = mock.Mock()
        backstage = mock.Mock()
        browse = mock.Mock()
        browse.Exists.return_value = True

        with mock.patch(
            "rpa_excel_ui_automation.excel_manager.auto.WindowControl",
            return_value=window,
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.find_dialog",
            side_effect=[None, dialog],
        ) as find_dialog, mock.patch(
            "rpa_excel_ui_automation.excel_manager.find_backstage",
            return_value=backstage,
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.auto.ButtonControl",
            return_value=browse,
        ):
            ExcelManager().open_file()

        assert window.sent == ["{Ctrl}o"]
        browse.Click.assert_called_once()
        find_dialog.assert_called()

    def test_save_as_envia_f12(self):
        window = FakeWindow()
        with mock.patch(
            "rpa_excel_ui_automation.excel_manager.auto.WindowControl",
            return_value=window,
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.find_dialog",
            return_value=mock.Mock(),
        ):
            ExcelManager().save_as()

        assert window.sent == ["{F12}"]

    def test_reintenta_y_lanza_timeout_cuando_no_aparece_el_dialogo(self):
        window = FakeWindow()
        with mock.patch(
            "rpa_excel_ui_automation.excel_manager.auto.WindowControl",
            return_value=window,
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.find_dialog", return_value=None
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.find_backstage", return_value=None
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.DIALOG_TIMEOUT", 0.2
        ):
            manager = ExcelManager()
            with pytest.raises(TimeoutError, match="Abrir"):
                manager.open_file()

        assert window.sent == ["{Ctrl}o"] * HOTKEY_RETRIES

    def test_inicia_excel_cuando_no_esta_en_ejecucion(self):
        class LaunchWindow(FakeWindow):
            def __init__(self):
                super().__init__(exists=False)
                self.started = False

            def Exists(self, timeout, *args, **kwargs):
                return self.started

        window = LaunchWindow()

        def popen_side_effect(*args, **kwargs):
            window.started = True
            return mock.Mock()

        with mock.patch(
            "rpa_excel_ui_automation.excel_manager.auto.WindowControl",
            return_value=window,
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.subprocess.Popen",
            side_effect=popen_side_effect,
        ) as popen, mock.patch(
            "rpa_excel_ui_automation.excel_manager.WINDOW_SEARCH_TIMEOUT", 0.2
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.LAUNCH_TIMEOUT", 0.5
        ):
            manager = ExcelManager()
            assert manager.window is window

        popen.assert_called_once()

    def test_lanza_runtimeerror_si_excel_no_puede_iniciarse(self):
        window = FakeWindow(exists=False)
        with mock.patch(
            "rpa_excel_ui_automation.excel_manager.auto.WindowControl",
            return_value=window,
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.subprocess.Popen"
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.WINDOW_SEARCH_TIMEOUT", 0.2
        ), mock.patch(
            "rpa_excel_ui_automation.excel_manager.LAUNCH_TIMEOUT", 0.5
        ):
            manager = ExcelManager()
            with pytest.raises(RuntimeError, match="iniciar Microsoft Excel"):
                _ = manager.window

        assert window.Exists(WINDOW_SEARCH_TIMEOUT) is False
        assert window.Exists(LAUNCH_TIMEOUT) is False