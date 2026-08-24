"""Identificadores de UI Automation y utilidades compartidas."""

import time

import uiautomation as auto

COMMON_DIALOG_CLASS = "CommonDialog"
LEGACY_DIALOG_CLASS = "#32770"
DIALOG_NAME_PATTERN = r"^(Abrir|Open|Guardar como|Save As)$"
OVERWRITE_NAME_PATTERN = r"^Confirm"
FILE_NAME_EDIT_IDS = ("1001", "1148")
FILE_NAME_HOST_IDS = ("FileNameControlHost",)
FILE_NAME_NAME_PATTERN = r"(Nombre de archivo|File name)"
ACTION_BUTTON_IDS = ("1",)
ACTION_BUTTON_NAME_PATTERN = r"(Abrir|Open|Guardar|Save)$"
REPLACE_BUTTON_IDS = ("CommandButton_6", "6")
REPLACE_BUTTON_NAME_PATTERN = r"^(Sí|Yes)$"

BACKSTAGE_VIEW_ID = "BackstageView"
BACKSTAGE_SEARCH_BOX_ID = "HomePageSearchBox"
BLANK_WORKBOOK_PATTERN = r"^(Blank workbook|Libro en blanco)$"
BROWSE_PATTERN = r"^(Browse|Examinar)$"

# En Excel 365 el dialogo nativo aparece como HIJO de la ventana principal
# (root -> XLMAIN -> dialogo), por lo que hay que buscarlo mas profundo.
DIALOG_SEARCH_DEPTH = 3
OVERWRITE_SEARCH_DEPTH = 3

SEARCH_STEP = 0.4


def find_dialog(timeout: float = 5.0) -> auto.WindowControl | None:
    """Busca el dialogo nativo del explorador de archivos activo."""
    modern = auto.WindowControl(
        searchDepth=DIALOG_SEARCH_DEPTH, ClassName=COMMON_DIALOG_CLASS
    )
    legacy = auto.WindowControl(
        searchDepth=DIALOG_SEARCH_DEPTH,
        ClassName=LEGACY_DIALOG_CLASS,
        RegexName=DIALOG_NAME_PATTERN,
    )
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if modern.Exists(SEARCH_STEP):
            return modern
        if legacy.Exists(SEARCH_STEP):
            return legacy
    return None


def find_overwrite_dialog(timeout: float = 5.0) -> auto.WindowControl | None:
    """Busca la ventana emergente de confirmacion de sobreescritura."""
    confirm = auto.WindowControl(
        searchDepth=OVERWRITE_SEARCH_DEPTH,
        ClassName=LEGACY_DIALOG_CLASS,
        RegexName=OVERWRITE_NAME_PATTERN,
    )
    if confirm.Exists(timeout):
        return confirm
    return None


def find_backstage(timeout: float = 5.0) -> auto.PaneControl | None:
    """Busca el Backstage de Excel (vista propia de Office 365)."""
    backstage = auto.PaneControl(searchDepth=30, AutomationId=BACKSTAGE_VIEW_ID)
    if backstage.Exists(timeout):
        return backstage
    return None