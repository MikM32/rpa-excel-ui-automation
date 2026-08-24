"""Genera la estructura .data requerida por el plan de pruebas.

Crea un libro .xlsx minimo con una tabla de datos de ejemplo usando solo
`pathlib` (rutas) y `zipfile` (empaquetado OOXML), sin dependencias externas.

El contenido de `origen.xlsx` es arbitrario para el flujo RPA (el flujo solo
abre y guarda; no transforma datos), pero una tabla simple hace la prueba
mas representativa.
"""

import sys

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

SAMPLE_TABLE = (
    ("ID", "Nombre", "Ciudad", "Monto"),
    ("1", "Ana Garcia", "Madrid", "1500.50"),
    ("2", "Luis Perez", "Bogota", "720.25"),
    ("3", "Maria Lopez", "Lima", "999.99"),
)

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""

WORKBOOK = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="Datos" sheetId="1" r:id="rId1"/></sheets>
</workbook>"""

WORKBOOK_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""

WORKSHEET_OPEN = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>"""

WORKSHEET_CLOSE = """  </sheetData>
</worksheet>"""


def column_letter(index: int) -> str:
    letters = ""
    position = index + 1
    while position > 0:
        position, remainder = divmod(position - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def sheet_xml(table: tuple) -> str:
    rows = []
    for row_index, row in enumerate(table, start=1):
        cells = []
        for col_index, value in enumerate(row):
            reference = f"{column_letter(col_index)}{row_index}"
            cells.append(f'<c r="{reference}" t="inlineStr"><is><t>{value}</t></is></c>')
        rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return WORKSHEET_OPEN + "".join(rows) + WORKSHEET_CLOSE


def build_xlsx(target: Path, table: tuple = SAMPLE_TABLE) -> None:
    with ZipFile(target, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES)
        zf.writestr("_rels/.rels", ROOT_RELS)
        zf.writestr("xl/workbook.xml", WORKBOOK)
        zf.writestr("xl/_rels/workbook.xml.rels", WORKBOOK_RELS)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml(table))


def main() -> None:
    force = "--force" in sys.argv[1:]
    base = Path(".data")
    input_dir = base / "input"
    output_dir = base / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    source = input_dir / "origen.xlsx"
    if not source.exists() or force:
        build_xlsx(source)

    print(f"input : {input_dir.resolve()}")
    print(f"output: {output_dir.resolve()}")
    print(f"origen: {source.resolve()} (exists={source.exists()})")


if __name__ == "__main__":
    main()