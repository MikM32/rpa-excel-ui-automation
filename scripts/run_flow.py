"""Ejecuta los Casos de Prueba 01 y 02 definidos en el README."""

import logging
from pathlib import Path

from rpa_excel_ui_automation.flow import run_flow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("run_flow")


def main() -> None:
    base = Path(__file__).resolve().parent.parent
    source = base / ".data" / "input" / "origen.xlsx"
    destination = base / ".data" / "output" / "destino.xlsx"

    if not source.exists():
        raise FileNotFoundError(
            f"No existe el archivo de origen {source}. "
            "Ejecuta primero: pdm run python scripts/create_sample.py"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)

    run_flow(source, destination)
    logger.info("Resultado: archivo destino %s", destination)


if __name__ == "__main__":
    main()