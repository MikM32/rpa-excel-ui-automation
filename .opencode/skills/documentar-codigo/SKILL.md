---
name: documentar-codigo
description: Aplica reglas de estilo de documentacion de codigo en espanol. Usar SIEMPRE al escribir o revisar comentarios, docstrings, mensajes de commit y archivos de documentacion (docs/*.md, README): prohibido el uso de acentos ortograficos, caracteres especiales y emojis; solo ASCII plano.
---

# Documentar codigo

Normas obligatorias al escribir o revisar cualquier documentacion de codigo:
comentarios, docstrings, mensajes de commit y archivos de documentacion
(docs/*.md, README, etc.).

## Reglas

1. **Sin acentos ortograficos.** Escribir todo en ASCII plano. Sustituir:
   - `a` por `a`, `e` por `e`, `i` por `i`, `o` por `o`, `u` por `u`.
   - `n` por `n`, `u` por `u`.
   - Ejemplo: "dialogo", "sobreescritura", "exitoso", "resolucion".

2. **Sin caracteres especiales.** No usar tildes en mayusculas, signos como
   `·`, `—`, `•`, ni secuencias de escape innecesarias en prosa.

3. **Sin emojis.** Prohibido usar emojis o iconos en cualquier texto.

4. **Aplica a:** docstrings, comentarios de codigo, mensajes de commit,
   documentos markdown (docs/), nombres de archivo y variables legibles.

## Excepcion funcional

Si una cadena en el CODIGO debe igualar texto real de la interfaz (por
ejemplo un boton cuya etiqueta real lleva tilde), conservar el caracter
original en el valor de la cadena. La regla aplica a comentarios y prosa,
no al valor funcional que debe coincidir con el texto real.

## Ejemplos

### Correcto

```python
# Abre el dialogo nativo de apertura
def open_file(self) -> None:
    """Despliega el dialogo 'Abrir'."""
```

### Incorrecto

```python
# Ábre el diálogo nativo de apertura ✨
def open_file(self) -> None:
    """Despliega el diálogo 'Abrir'."""
```

### Cadena funcional (correcta, conserva el texto real)

```python
REPLACE_BUTTON_NAME_PATTERN = r"^(Sí|Yes)$"
```