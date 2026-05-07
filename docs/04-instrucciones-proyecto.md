# 04 - Instrucciones de Proyecto

GitHub Copilot puede leer un archivo especial en tu repositorio para entender el contexto global, las reglas de estilo y las tecnologías que prefieres.

## 1. El comando `/init`

En el Chat Panel (`Ctrl + Alt + I`), puedes ejecutar el comando `/init`. Este comando analiza tu workspace y te ayuda a generar un archivo de instrucciones inicial.

## 2. `.github/copilot-instructions.md`

Hemos creado este archivo manualmente para esta sesión. Copilot lo leerá automáticamente en cada consulta.

**¿Qué hemos definido en [.github/copilot-instructions.md](../.github/copilot-instructions.md)?**
- Uso de **type hints** obligatorio.
- Estilo **PEP 8**.
- Idioma de comentarios: **Español**.
- Framework de tests: `pytest`.

## 3. Demostración de Contexto

**Ejercicio:**
1. Crea un archivo `src/processor.py`.
2. Pide al Inline Chat (`Ctrl + I`): "Crea una función que reciba una lista de diccionarios con ventas y devuelva el total".
3. Observa:
   - ¿Ha añadido Type Hints? `def calcular_total(ventas: list[dict]) -> float:`
   - ¿Los comentarios están en español?
   - ¿Sigue el estilo PEP 8?

Sin este archivo, Copilot podría responder en inglés o sin tipos definidos por defecto.

---
[Próxima Sesión: Capacidades Avanzadas](05-avanzado.md)
