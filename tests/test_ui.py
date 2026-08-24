"""Tests unitarios de los helpers de deteccion de dialogos (ui.py)."""

from unittest import mock

from rpa_excel_ui_automation import ui


class FakeWindow:
    def __init__(self, exists):
        self._exists = exists

    def Exists(self, timeout, *args, **kwargs):
        return self._exists


def test_find_dialog_devuelve_el_moderno():
    modern = FakeWindow(True)
    legacy = FakeWindow(False)

    def factory(**kwargs):
        if kwargs.get("ClassName") == ui.COMMON_DIALOG_CLASS:
            return modern
        return legacy

    with mock.patch("rpa_excel_ui_automation.ui.auto.WindowControl", side_effect=factory), mock.patch(
        "rpa_excel_ui_automation.ui.SEARCH_STEP", 0.01
    ):
        assert ui.find_dialog(0.5) is modern


def test_find_dialog_devuelve_el_clasico():
    modern = FakeWindow(False)
    legacy = FakeWindow(True)

    def factory(**kwargs):
        if kwargs.get("ClassName") == ui.COMMON_DIALOG_CLASS:
            return modern
        return legacy

    with mock.patch("rpa_excel_ui_automation.ui.auto.WindowControl", side_effect=factory), mock.patch(
        "rpa_excel_ui_automation.ui.SEARCH_STEP", 0.01
    ):
        assert ui.find_dialog(0.5) is legacy


def test_find_dialog_devuelve_none():
    modern = FakeWindow(False)
    legacy = FakeWindow(False)

    def factory(**kwargs):
        if kwargs.get("ClassName") == ui.COMMON_DIALOG_CLASS:
            return modern
        return legacy

    with mock.patch("rpa_excel_ui_automation.ui.auto.WindowControl", side_effect=factory), mock.patch(
        "rpa_excel_ui_automation.ui.SEARCH_STEP", 0.01
    ):
        assert ui.find_dialog(0.05) is None


def test_find_overwrite_dialog_encontrado():
    window = FakeWindow(True)
    with mock.patch("rpa_excel_ui_automation.ui.auto.WindowControl", return_value=window):
        assert ui.find_overwrite_dialog(0.5) is window


def test_find_overwrite_dialog_ausente():
    window = FakeWindow(False)
    with mock.patch("rpa_excel_ui_automation.ui.auto.WindowControl", return_value=window):
        assert ui.find_overwrite_dialog(0.05) is None


def test_find_backstage_encontrado():
    window = FakeWindow(True)
    with mock.patch("rpa_excel_ui_automation.ui.auto.PaneControl", return_value=window):
        assert ui.find_backstage(0.5) is window


def test_find_backstage_ausente():
    window = FakeWindow(False)
    with mock.patch("rpa_excel_ui_automation.ui.auto.PaneControl", return_value=window):
        assert ui.find_backstage(0.05) is None