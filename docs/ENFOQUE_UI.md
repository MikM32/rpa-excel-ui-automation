# Automatizacion por UI de Excel (clasico y Excel 365)

> Documento tecnico del flujo implementado. El bot opera **exclusivamente con
> UI Automation** (`uiautomation`), cumpliendo el plan de pruebas del
> `README.md`.

## 1. Arquitectura

Dos clases con responsabilidad unica, tal como exige el enunciado:

- **`ExcelManager`** (`excel_manager.py`): gestiona la instancia de Excel y
  dispara los eventos de la ventana.
  - `open_file()`: despliega el dialogo nativo **"Abrir"**.
  - `save_as()`: despliega el dialogo nativo **"Guardar como"**.
  - Lanza Excel si no esta en ejecucion y asegura que haya un libro abierto
    antes de `F12`.
- **`FileExplorer`** (`file_explorer.py`): interactua con los dialogos nativos
  del sistema (Explorador de archivos).
  - `open_file(ruta)`: inyecta la ruta origen en el campo de nombre de archivo
    y presiona "Abrir".
  - `save_file(ruta)`: inyecta la ruta destino, presiona "Guardar" y confirma
    la sobreescritura si el sistema la advierte.

`flow.py` orquesta ambos casos de prueba; `ui.py` centraliza los selectores y
utilidades compartidas.

## 2. Consideraciones de la version actual de Excel (Excel 365)

El comportamiento de los atajos **difiere segun la version de Excel**:

| Accion | Excel clasico | Excel 365 |
|---|---|---|
| `Ctrl+O` | Dialogo nativo "Abrir" directo | Backstage de abrir |
| `F12` (con libro abierto) | Dialogo nativo "Guardar como" | Dialogo nativo "Guardar como" |
| `F12` (pantalla de inicio) | Dialogo nativo | Backstage *Home* |

### Hallazgos verificados en Excel 365

1. **El dialogo nativo es HIJO de la ventana principal.** En Excel 365, los
   dialogos "Abrir"/"Guardar como" (`#32770`) aparecen **anidados bajo
   `XLMAIN`** en el arbol de UI Automation, no como ventanas top-level. Por eso
   `find_dialog()` y `find_overwrite_dialog()` buscan con `searchDepth` mayor
   (no `1`).

2. **`Ctrl+O` no abre el dialogo en 365**: abre el Backstage. El Backstage de
   abrir tiene un boton **"Browse"/"Examinar"** (`NetUISimpleButton`) que
   despliega el **mismo dialogo nativo** de Excel clasico. `open_file()` lo
   presiona para llegar al dialogo.

3. **`F12` solo funciona con un libro abierto** en 365. En la pantalla de
   inicio abre el Backstage *Home*. Por eso `save_as()` asegura un libro
   abierto (crea un libro en blanco con la plantilla "Blank workbook"/"Libro
   en blanco" del Backstage) antes de enviar `F12`.

4. **Selectores distintos entre dialogos**:
   - "Abrir": campo de nombre `Edit` (AutomationId **`1148`**); boton "Abrir"
     es un **`SplitButtonControl`** (AutomationId **`1`**).
   - "Guardar como": campo de nombre `Edit` (AutomationId **`1001`**); boton
     "Guardar" es un `ButtonControl` (AutomationId **`1`**).
   - Confirmacion de sobreescritura: `#32770` con nombre **"Confirm..."**
     ("Confirm Save As"/"Confirmar guardar como"); boton "Yes"/"Si".

5. **Idioma**: los selectores se resuelven por `AutomationId` (estable) y, como
   respaldo, por `RegexName` que cubre ingles y espanol (p. ej.
   `^(Si|Yes)$`, `^(Browse|Examinar)$`, `^(Blank workbook|Libro en blanco)$`).
   Nota: en el codigo, el patron del boton de reemplazo conserva la tilde del
   texto real del boton en la UI en espanol.

### Advertencias

- **Excel 365 (Backstage)**: los selectores `NetUI*` del Backstage pueden
  variar entre versiones de Office; el codigo los usa solo como puente para
  llegar al dialogo nativo (que si tiene selectores estables).
- **Excel clasico**: los atajos abren el dialogo directo, por lo que el flujo
  es el mismo; el puente por Backstage simplemente no se activa.
- **El dialogo puede tardar** en aparecer; el bot espera con `Exists(timeout)`
  y reintenta los atajos, sin pausas estaticas.

## 3. Como maneja la automatizacion la UI

- **Sincronizacion por eventos**: todas las esperas usan `.Exists(timeout)` y
  `WaitForDisappear` (sin `time.sleep()`).
- **Direccionamiento explicito**: cada control se localiza por
  `AutomationId`/`ClassName`/`RegexName`; prohibido navegar con `Tab` y hacer
  clics por coordenadas X/Y.
- **Inyeccion de rutas con verificacion**: la ruta se escribe en el campo de
  nombre y se valida con el patron `Value`; se reintenta si no coincide.
- **Confirmacion dinamica de sobreescritura**: la ventana de advertencia se
  evalua con `.Exists(timeout)` y se confirma con el boton "Yes"/"Si".
- **Rutas con `pathlib`**: entrada `.data/input/origen.xlsx`, salida
  `.data/output/destino.xlsx`.
- **Trazabilidad**: logs en todos los metodos (inicio, resultados, detecciones
  de sobreescritura).

## 4. Como ejecutar

```bash
pdm install
pdm run python scripts/create_sample.py --force   # datos de ejemplo
pdm run python scripts/run_flow.py                # Casos 01 y 02
pdm run pytest                                    # tests unitarios
```