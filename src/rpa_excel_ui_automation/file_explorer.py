"""Responsable de interactuar con los dialogos nativos del explorador."""

import logging

import uiautomation as auto

from pathlib import Path

from rpa_excel_ui_automation.ui import (
    ACTION_BUTTON_IDS,
    ACTION_BUTTON_NAME_PATTERN,
    FILE_NAME_EDIT_IDS,
    FILE_NAME_HOST_IDS,
    FILE_NAME_NAME_PATTERN,
    REPLACE_BUTTON_IDS,
    REPLACE_BUTTON_NAME_PATTERN,
    find_dialog,
    find_overwrite_dialog,
)

logger = logging.getLogger(__name__)

DIALOG_TIMEOUT = 6.0
CONTROL_TIMEOUT = 3.0
OVERWRITE_TIMEOUT = 5.0
TYPING_RETRIES = 2


class FileExplorer:
    """Maneja los dialogos nativos del sistema operativo (Explorador de archivos)."""

    def open_file(self, source_path: Path, timeout: float = DIALOG_TIMEOUT) -> None:
        logger.info("FileExplorer.open_file: abriendo %s", source_path)
        dialog = self._wait_for_dialog(timeout)
        file_name_edit = self._get_file_name_edit(dialog)
        self._inject_path(file_name_edit, source_path)
        self._click_action_button(dialog)
        self._wait_dialog_close(dialog, timeout)
        logger.info("FileExplorer.open_file: accion 'Abrir' completada")

    def save_file(
        self,
        destination_path: Path,
        timeout: float = DIALOG_TIMEOUT,
        overwrite_timeout: float = OVERWRITE_TIMEOUT,
    ) -> None:
        logger.info("FileExplorer.save_file: guardando en %s", destination_path)
        dialog = self._wait_for_dialog(timeout)
        file_name_edit = self._get_file_name_edit(dialog)
        self._inject_path(file_name_edit, destination_path)
        self._click_action_button(dialog)
        self._confirm_overwrite(overwrite_timeout)
        self._wait_dialog_close(dialog, timeout)
        if not destination_path.exists():
            raise RuntimeError(f"No se creo el archivo destino: {destination_path}")
        logger.info("FileExplorer.save_file: archivo guardado en %s", destination_path)

    def _wait_for_dialog(self, timeout: float) -> auto.WindowControl:
        dialog = find_dialog(timeout)
        if dialog is None:
            raise TimeoutError("No se detecto el dialogo nativo del explorador")
        dialog.SetActive()
        return dialog

    def _get_file_name_edit(self, dialog: auto.WindowControl) -> auto.EditControl:
        for edit_id in FILE_NAME_EDIT_IDS:
            edit = dialog.EditControl(AutomationId=edit_id)
            if edit.Exists(CONTROL_TIMEOUT):
                return edit
        for host_id in FILE_NAME_HOST_IDS:
            host = dialog.ComboBoxControl(AutomationId=host_id)
            if host.Exists(CONTROL_TIMEOUT):
                edit = host.EditControl()
                if edit.Exists(CONTROL_TIMEOUT):
                    return edit
        edit = dialog.EditControl(RegexName=FILE_NAME_NAME_PATTERN)
        if edit.Exists(CONTROL_TIMEOUT):
            return edit
        raise LookupError("No se localizo el control de nombre de archivo en el dialogo")

    def _inject_path(self, file_name_edit: auto.EditControl, target_path: Path) -> None:
        path = str(target_path.resolve())
        file_name_edit.SetFocus()
        for attempt in range(1, TYPING_RETRIES + 1):
            file_name_edit.SendKeys("{Ctrl}a{Delete}")
            file_name_edit.SendKeys(path)
            if self._edit_value_matches(file_name_edit, path):
                logger.info("FileExplorer: ruta inyectada en el control Edit")
                return
            logger.warning(
                "FileExplorer: la ruta no coincidio (intento %d/%d)", attempt, TYPING_RETRIES
            )
        raise RuntimeError("No se pudo inyectar la ruta en el campo de nombre de archivo")

    def _edit_value_matches(self, edit: auto.EditControl, expected: str) -> bool:
        try:
            current = edit.GetValuePattern().Value
        except Exception:
            return True
        return current.rstrip() == expected

    def _click_action_button(self, dialog: auto.WindowControl) -> None:
        controls = (dialog.ButtonControl, dialog.SplitButtonControl)
        for button_id in ACTION_BUTTON_IDS:
            for factory in controls:
                button = factory(AutomationId=button_id)
                if button.Exists(CONTROL_TIMEOUT):
                    button.Click()
                    logger.info("FileExplorer: boton de accion presionado")
                    return
        for factory in controls:
            button = factory(RegexName=ACTION_BUTTON_NAME_PATTERN)
            if button.Exists(CONTROL_TIMEOUT):
                button.Click()
                logger.info("FileExplorer: boton de accion presionado")
                return
        raise LookupError("No se localizo el boton de accion del dialogo")

    def _confirm_overwrite(self, timeout: float) -> None:
        confirm = find_overwrite_dialog(timeout)
        if confirm is None:
            logger.info("FileExplorer: no se detecto advertencia de sobreescritura")
            return
        logger.info("FileExplorer: detectada advertencia de sobreescritura")
        confirm.SetActive()
        button = confirm.ButtonControl(RegexName=REPLACE_BUTTON_NAME_PATTERN)
        if button.Exists(CONTROL_TIMEOUT):
            button.Click()
        else:
            for button_id in REPLACE_BUTTON_IDS:
                button = confirm.ButtonControl(AutomationId=button_id)
                if button.Exists(CONTROL_TIMEOUT):
                    button.Click()
                    break
            else:
                raise LookupError("No se localizo el boton de confirmacion de sobreescritura")
        auto.WaitForDisappear(confirm, timeout)
        logger.info("FileExplorer: sobreescritura confirmada")

    def _wait_dialog_close(self, dialog: auto.WindowControl, timeout: float) -> None:
        if not auto.WaitForDisappear(dialog, timeout):
            logger.warning("FileExplorer: el dialogo no se cerro dentro del tiempo esperado")