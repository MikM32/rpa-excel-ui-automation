"""Responsable de gestionar la instancia de Microsoft Excel."""

import logging
import subprocess
import time

import uiautomation as auto

from rpa_excel_ui_automation.ui import (
    BLANK_WORKBOOK_PATTERN,
    BROWSE_PATTERN,
    find_backstage,
    find_dialog,
)

logger = logging.getLogger(__name__)

EXCEL_WINDOW_CLASS = "XLMAIN"
WINDOW_SEARCH_TIMEOUT = 5.0
LAUNCH_TIMEOUT = 15.0
DIALOG_TIMEOUT = 4.0
HOTKEY_RETRIES = 2
WORKBOOK_WAIT_TIMEOUT = 10.0
OPEN_HOTKEY = "{Ctrl}o"
SAVE_AS_HOTKEY = "{F12}"


class ExcelManager:
    """Gestiona la aplicacion Excel y dispara sus eventos de interfaz."""

    def __init__(self) -> None:
        self._window: auto.WindowControl | None = None

    @property
    def window(self) -> auto.WindowControl:
        if self._window is None or not self._safe_exists(self._window, 0):
            self._window = self._find_or_launch_excel()
        return self._window

    def open_file(self) -> None:
        """Despliega el dialogo nativo 'Abrir'.

        En Excel clasico, Ctrl+O abre el dialogo directamente. En Excel 365
        abre el Backstage, por lo que se presiona 'Browse'/'Examinar' para
        desplegar el dialogo nativo.
        """
        window = self._activate_window()
        for attempt in range(1, HOTKEY_RETRIES + 1):
            window.SendKeys(OPEN_HOTKEY)
            if self._ensure_open_dialog(DIALOG_TIMEOUT):
                logger.info("ExcelManager.open_file: dialogo 'Abrir' detectado")
                return
            logger.warning(
                "ExcelManager.open_file: intento %d/%d sin detectar el dialogo 'Abrir'",
                attempt,
                HOTKEY_RETRIES,
            )
        raise TimeoutError("No se desplego el dialogo 'Abrir' de Excel")

    def save_as(self) -> None:
        self._ensure_workbook_open()
        self._trigger_dialog(SAVE_AS_HOTKEY, "Guardar como")

    def _trigger_dialog(self, hotkey: str, label: str) -> None:
        logger.info("ExcelManager: desplegando el dialogo '%s'", label)
        window = self._activate_window()
        for attempt in range(1, HOTKEY_RETRIES + 1):
            window.SendKeys(hotkey)
            if find_dialog(DIALOG_TIMEOUT) is not None:
                logger.info("ExcelManager: dialogo '%s' detectado", label)
                return
            logger.warning(
                "ExcelManager: intento %d/%d sin detectar el dialogo '%s'",
                attempt,
                HOTKEY_RETRIES,
                label,
            )
        raise TimeoutError(f"No se desplego el dialogo '{label}' de Excel")

    def _ensure_open_dialog(self, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if find_dialog(0.3) is not None:
                return True
            if find_backstage(0.3) is not None:
                browse = auto.ButtonControl(searchDepth=40, RegexName=BROWSE_PATTERN)
                if self._safe_exists(browse, 3):
                    browse.Click()
                    return find_dialog(timeout) is not None
        return False

    def _ensure_workbook_open(self) -> None:
        """Abre un libro en blanco si Excel esta en la pantalla de inicio.

        En Excel 365 el atajo F12 solo despliega el dialogo 'Guardar como'
        cuando hay un libro abierto; en la pantalla de inicio abre el
        Backstage Home.
        """
        window = self.window
        if self._window_name(window) != "Excel":
            return
        logger.info("ExcelManager: abriendo un libro en blanco")
        window.SendKeys(SAVE_AS_HOTKEY)
        blank = auto.ListItemControl(searchDepth=30, RegexName=BLANK_WORKBOOK_PATTERN)
        if not self._safe_exists(blank, 5):
            logger.warning("ExcelManager: no se localizo la plantilla de libro en blanco")
            return
        blank.Click()
        deadline = time.monotonic() + WORKBOOK_WAIT_TIMEOUT
        while time.monotonic() < deadline:
            try:
                window.Refind(0.5)
            except Exception:
                break
            if self._window_name(window) != "Excel":
                return
        logger.warning("ExcelManager: no se confirmo la apertura del libro en blanco")

    @staticmethod
    def _window_name(window: auto.WindowControl) -> str:
        try:
            return window.Name or ""
        except Exception:
            return ""

    def _activate_window(self) -> auto.WindowControl:
        window = self.window
        auto.SetForegroundWindow(window.NativeWindowHandle)
        auto.SwitchToThisWindow(window.NativeWindowHandle)
        window.SetActive()
        return window

    def _find_or_launch_excel(self) -> auto.WindowControl:
        window = auto.WindowControl(searchDepth=1, ClassName=EXCEL_WINDOW_CLASS)
        if not self._safe_exists(window, WINDOW_SEARCH_TIMEOUT):
            logger.info("ExcelManager: iniciando Microsoft Excel")
            subprocess.Popen(["cmd", "/c", "start", "excel"], shell=False)
            if not self._safe_exists(window, LAUNCH_TIMEOUT):
                raise RuntimeError("No fue posible iniciar Microsoft Excel")
        return window

    @staticmethod
    def _safe_exists(control: auto.Control, timeout: float) -> bool:
        """Verifica existencia tolerando elementos que se invalidan al buscar."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                if control.Exists(0.5):
                    return True
            except Exception:
                pass
        return False