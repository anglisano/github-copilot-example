# 02 - Funcionalidades Básicas

En esta sección exploraremos cómo interactuar con Copilot en el flujo de trabajo diario.

## 1. Ghost Text (Autocompletado Proactivo)

Copilot sugiere código mientras escribes. Estas sugerencias aparecen en color gris (de ahí "Ghost Text").

**Ejercicio:**
1. Abre un archivo nuevo en `src/test_logic.py`.
2. Empieza a escribir una función para calcular el área de un círculo.
3. Observa cómo Copilot propone el cuerpo de la función.
   - `Tab` para aceptar.
   - `Alt + [` o `Alt + ]` para navegar entre opciones.
   - `Ctrl + Enter` para ver un panel con 10 sugerencias completas.

## 2. Next Edit Suggestions (Siguiente Edición)

Copilot ahora es capaz de predecir dónde harás el siguiente cambio basándose en tus ediciones recientes. Verás una sugerencia de cambio incluso antes de empezar a escribir en esa línea.

## 3. Inline Chat (`Ctrl + I`)

El Inline Chat es ideal para cambios localizados o refactorizaciones rápidas sin perder el foco del archivo.

**Pro tips:**
- Selecciona un bloque de código y pulsa `Ctrl + I`.
- Pide: `/fix` para arreglar errores.
- Pide: `/doc` para generar documentación.
- Pide: "Convierte este bucle for en una list comprehension".

## 4. Chat Panel (`Ctrl + Alt + I`)

Para consultas más abstractas o que requieran más contexto del proyecto, utiliza el panel lateral.
- Usa `#file` para referenciar archivos específicos.
- Usa `@workspace` para preguntar sobre toda la base de código.

---
[Próxima Sesión: Personalización y Gitflow](03-personalizacion.md)
