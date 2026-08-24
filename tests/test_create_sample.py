"""Tests del generador de datos de ejemplo (scripts/create_sample.py)."""

import importlib.util
import sys
from pathlib import Path
from zipfile import ZipFile

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
SPEC = importlib.util.spec_from_file_location("create_sample", SCRIPTS_DIR / "create_sample.py")
create_sample = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(create_sample)


def test_build_xlsx_es_un_zip_valido_con_las_partes_oooxml(tmp_path):
    target = tmp_path / "origen.xlsx"
    create_sample.build_xlsx(target)

    with ZipFile(target) as zf:
        names = set(zf.namelist())
        expected = {
            "[Content_Types].xml",
            "_rels/.rels",
            "xl/workbook.xml",
            "xl/_rels/workbook.xml.rels",
            "xl/worksheets/sheet1.xml",
        }
        assert expected <= names


def test_sheet_contiene_la_tabla_de_ejemplo(tmp_path):
    target = tmp_path / "origen.xlsx"
    create_sample.build_xlsx(target)

    with ZipFile(target) as zf:
        sheet = zf.read("xl/worksheets/sheet1.xml").decode("utf-8")

    assert "Nombre" in sheet
    assert "Ana Garcia" in sheet
    assert "Luis Perez" in sheet
    assert "Maria Lopez" in sheet
    assert "<row r=\"4\"" in sheet


def test_column_letter():
    assert create_sample.column_letter(0) == "A"
    assert create_sample.column_letter(1) == "B"
    assert create_sample.column_letter(25) == "Z"
    assert create_sample.column_letter(26) == "AA"