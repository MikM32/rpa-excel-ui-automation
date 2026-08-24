# Automatización por UI de Excel (clásico y Excel 365)

> Documento técnico del flujo implementado. El bot opera **exclusivamente con
> UI Automation** (`uiautomation`), cumpliendo el plan de pruebas del
> `README.md`.

## 1. Arquitectura

Dos clases con responsabilidad única, tal como exige el enunciado:

- **`ExcelManager`** (`excel_manager.py`): gestiona la instancia de Excel y
  dispara los eventos de la ventana.
  - `open_file()`: despliega el diálogo nativo **"Abrir"**.
  - `save_as()`: despliega el diálogo nativo **"Guardar como"**.
  - Lanza Excel si no está en ejecución y asegura que haya un libro abierto
    antes de `F12`.
- **`FileExplorer`** (`file_explorer.py`): interactúa con los diálogos nativos
  del sistema (Explorador de archivos).
  - `open_file(ruta)`: inyecta la ruta origen en el campo de nombre de archivo
    y presiona "Abrir".
  - `save_file(ruta)`: inyecta la ruta destino, presiona "Guardar" y confirma
    la sobreescritura si el sistema la advierte.

`flow.py` orquesta ambos casos de prueba; `ui.py` centraliza los selectores y
utilidades compartidas.

## 2. Consideraciones de la versión actual de Excel (Excel 365)

El comportamiento de los atajos **difiere según la versión de Excel**:

| Acción | Excel clásico | Excel 365 |
|---|---|---|
| `Ctrl+O` | Diálogo nativo "Abrir" directo | Backstage de abrir |
| `F12` (con libro abierto) | Diálogo nativo "Guardar como" | Diálogo nativo "Guardar como" |
| `F12` (pantalla de inicio) | Diálogo nativo | Backstage *Home* |

### Hallazgos verificados en Excel 365

1. **El diálogo nativo es HIJO de la ventana principal.** En Excel 365, los
   diálogos "Abrir"/"Guardar como" (`#32770`) aparecen **anidados bajo
   `XLMAIN`** en el árbol de UI Automation, no como ventanas top-level. Por eso
   `find_dialog()` y `find_overwrite_dialog()` buscan con `searchDepth` mayor
   (no `1`).

2. **`Ctrl+O` no abre el diálogo en 365**: abre el Backstage. El Backstage de
   abrir tiene un botón **"Browse"/"Examinar"** (`NetUISimpleButton`) que
   despliega el **mismo diálogo nativo** de Excel clásico. `open_file()` lo
   presiona para llegar al diálogo.

3. **`F12` solo funciona con un libro abierto** en 365. En la pantalla de
   inicio abre el Backstage *Home*. Por eso `save_as()` asegura un libro abierto
   (crea un libro en blanco con la plantilla "Blank workbook"/"Libro en blanco"
   del Backstage) antes de enviar `F12`.

4. **Selectores distintos entre diálogos**:
   - "Abrir": campo de nombre `Edit` (AutomationId **`1148`**); botón "Abrir"
     es un **`SplitButtonControl`** (AutomationId **`1`**).
   - "Guardar como": campo de nombre `Edit` (AutomationId **`1001`**); botón
     "Guardar" es un `ButtonControl` (AutomationId **`1`**).
   - Confirmación de sobrescritura: `#32770` con nombre **"Confirm..."**
     ("Confirm Save As"/"Confirmar guardar como"); botón "Yes"/"Sí"
     (AutomationId `CommandButton_6`).

5. **Idioma**: los selectores se resuelven por `AutomationId` (estable) y, como
   respaldo, por `RegexName` que cubre inglés y español (p. ej.
   `^(Sí|Yes)$`, `^(Browse|Examinar)$`, `^(Blank workbook|Libro en blanco)$`).

### Advertencias

- **Excel 365 (Backstage)**: los selectores `NetUI*` del Backstage pueden
  variar entre versiones de Office; el código los usa solo como puente para
  llegar al diálogo nativo (que sí tiene selectores estables).
- **Excel clásico**: los atajos abren el diálogo directo, por lo que el flujo
  es el mismo; el puente por Backstage simplemente no se activa.
- **El diálogo puede tardar** en aparecer; el bot espera con `Exists(timeout)`
  y reintenta los atajos, sin pausas estáticas.

## 3. Cómo maneja la automatización la UI

- **Sincronización por eventos**: todas las esperas usan `.Exists(timeout)` y
  `WaitForDisappear` (sin `time.sleep()`).
- **Direccionamiento explícito**: cada control se localiza por
  `AutomationId`/`ClassName`/`RegexName`; prohibido navegar con `Tab` y hacer
  clics por coordenadas X/Y.
- **Inyección de rutas con verificación**: la ruta se escribe en el campo de
  nombre y se valida con el patrón `Value`; se reintenta si no coincide.
- **Confirmación dinámica de sobrescritura**: la ventana de advertencia se
  evalúa con `.Exists(timeout)` y se confirma con el botón "Yes"/"Sí".
- **Rutas con `pathlib`**: entrada `.data/input/origen.xlsx`, salida
  `.data/output/destino.xlsx`.
- **Trazabilidad**: logs en todos los métodos (inicio, resultados, detecciones
  de sobreescritura).

## 4. Cómo ejecutar

```bash
pdm install
pdm run python scripts/create_sample.py --force   # datos de ejemplo
pdm run python scripts/run_flow.py                # Casos 01 y 02
pdm run pytest                                    # tests unitarios
```