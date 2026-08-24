"""Tests unitarios de FileExplorer (con mocks, no requieren Excel)."""

from contextlib import ExitStack, contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from rpa_excel_ui_automation import FileExplorer


class FakeEdit:
    def __init__(self, exists=True, value=None):
        self._exists = exists
        self.value = value if value is not None else ""
        self.focus = False
        self.typed = []

    def Exists(self, timeout, *args, **kwargs):
        return self._exists

    def SetFocus(self):
        self.focus = True

    def SendKeys(self, text, **kwargs):
        self.typed.append(text)
        if text == "{Ctrl}a{Delete}":
            self.value = ""
        else:
            self.value += text

    def GetValuePattern(self):
        return SimpleNamespace(Value=self.value)


class FakeButton:
    def __init__(self, exists=True):
        self._exists = exists
        self.clicked = False

    def Exists(self, timeout, *args, **kwargs):
        return self._exists

    def Click(self):
        self.clicked = True


class FakeDialog:
    def __init__(self, edit=None, button=None, combo=None):
        self.edit = edit if edit is not None else FakeEdit()
        self.button = button if button is not None else FakeButton()
        self.combo = combo
        self.active = False
        self.button_requests = []

    def SetActive(self):
        self.active = True

    def EditControl(self, **kwargs):
        return self.edit

    def ComboBoxControl(self, **kwargs):
        return self.combo

    def ButtonControl(self, **kwargs):
        self.button_requests.append(kwargs)
        return self.button

    def SplitButtonControl(self, **kwargs):
        self.button_requests.append(kwargs)
        return FakeButton(exists=False)


class FakeConfirm:
    def __init__(self, button=None):
        self.button = button if button is not None else FakeButton()
        self.active = False
        self.button_requests = []

    def SetActive(self):
        self.active = True

    def ButtonControl(self, **kwargs):
        self.button_requests.append(kwargs)
        return self.button


class SeqExistsButton(FakeButton):
    def __init__(self, results):
        super().__init__()
        self.results = list(results)

    def Exists(self, timeout, *args, **kwargs):
        return self.results.pop(0) if self.results else False


@contextmanager
def _patches(dialog=None, confirm=None, wait_result=True):
    with ExitStack() as stack:
        stack.enter_context(
            mock.patch("rpa_excel_ui_automation.file_explorer.find_dialog", return_value=dialog)
        )
        stack.enter_context(
            mock.patch(
                "rpa_excel_ui_automation.file_explorer.find_overwrite_dialog",
                return_value=confirm,
            )
        )
        stack.enter_context(
            mock.patch(
                "rpa_excel_ui_automation.file_explorer.auto.WaitForDisappear",
                return_value=wait_result,
            )
        )
        yield


class TestFileExplorer:
    def test_open_file_inyecta_ruta_y_clickea_abrir(self, tmp_path):
        source = tmp_path / "origen.xlsx"
        source.write_bytes(b"x")
        dialog = FakeDialog()
        with _patches(dialog=dialog):
            FileExplorer().open_file(source)

        assert dialog.edit.focus is True
        assert dialog.edit.value == str(source.resolve())
        assert dialog.edit.typed[0] == "{Ctrl}a{Delete}"
        assert dialog.button.clicked is True
        assert dialog.active is True

    def test_open_file_lanza_timeout_sin_dialogo(self, tmp_path):
        source = tmp_path / "origen.xlsx"
        with _patches(dialog=None):
            with pytest.raises(TimeoutError, match="dialogo nativo"):
                FileExplorer().open_file(source)

    def test_save_file_guarda_y_confirma_sobreescritura(self, tmp_path):
        destination = tmp_path / "destino.xlsx"
        destination.write_bytes(b"x")
        dialog = FakeDialog()
        confirm = FakeConfirm()
        with _patches(dialog=dialog, confirm=confirm):
            FileExplorer().save_file(destination)

        assert dialog.button.clicked is True
        assert confirm.button.clicked is True
        assert confirm.active is True

    def test_save_file_sin_advertencia_de_sobreescritura(self, tmp_path):
        destination = tmp_path / "destino.xlsx"
        destination.write_bytes(b"x")
        with _patches(dialog=FakeDialog(), confirm=None):
            FileExplorer().save_file(destination)

    def test_save_file_lanza_runtimeerror_si_no_se_crea_el_destino(self, tmp_path):
        destination = tmp_path / "destino.xlsx"
        with _patches(dialog=FakeDialog(), confirm=None):
            with pytest.raises(RuntimeError, match="destino"):
                FileExplorer().save_file(destination)

    def test_sobreescritura_usa_fallback_por_automation_id(self, tmp_path):
        destination = tmp_path / "destino.xlsx"
        destination.write_bytes(b"x")
        button = SeqExistsButton([False, True])
        confirm = FakeConfirm(button=button)
        with _patches(dialog=FakeDialog(), confirm=confirm):
            FileExplorer().save_file(destination)

        assert confirm.button.clicked is True

    def test_get_file_name_edit_fallback_al_combo(self):
        combo_edit = FakeEdit()
        combo = mock.Mock()
        combo.Exists.return_value = True
        combo.EditControl.return_value = combo_edit
        dialog = FakeDialog(edit=FakeEdit(exists=False), combo=combo)

        edit = FileExplorer()._get_file_name_edit(dialog)

        assert edit is combo_edit

    def test_edit_value_matches(self):
        explorer = FileExplorer()
        edit = FakeEdit(value="C:/a/b.xlsx")
        assert explorer._edit_value_matches(edit, "C:/a/b.xlsx") is True
        assert explorer._edit_value_matches(edit, "otra/ruta.xlsx") is False

    def test_edit_value_matches_asume_ok_si_no_soporta_value_pattern(self):
        explorer = FileExplorer()
        edit = SimpleNamespace(
            GetValuePattern=lambda: (_ for _ in ()).throw(RuntimeError("sin ValuePattern"))
        )
        assert explorer._edit_value_matches(edit, "x") is True