# 05 - Capacidades Avanzadas

GitHub Copilot está evolucionando de ser un autocompletado a ser un **Agente de IA** capaz de realizar tareas complejas.

## 1. Agentes y Skills

Los Agentes pueden planificar y ejecutar cambios en múltiples archivos simultáneamente.
- **Agent Desktop**: Puede abrir archivos, ejecutar comandos en la terminal y leer errores para corregirse a sí mismo.
- **Skills**: Son capacidades extra que permiten a Copilot usar herramientas específicas (ej: buscar en Azure, analizar costos, generar infraestructura).

## 2. GitHub CLI con Copilot (`gh copilot`)

Puedes usar Copilot directamente en tu terminal.

**Instalación:**
1. Instala GitHub CLI (`gh`).
2. Instala la extensión: `gh extension install github/gh-copilot`.

**Funcionalidades:**
- `gh copilot explain "sudo rm -rf /"`: Te explica qué hace un comando (¡Cuidado con este!).
- `gh copilot suggest "listar archivos de mas de 100mb"`: Te sugiere el comando exacto para tu shell.

## 3. Prompts y Hooks

- **Custom Prompts**: Puedes guardar plantillas de prompts para tareas repetitivas en archivos `.prompt.md`.
- **Chat Hooks**: Permiten ejecutar comandos automáticamente después de una interacción con Copilot (ej: ejecutar `black` o `pylint` automáticamente tras generar código).

---
[Próxima Sesión: Model Context Protocol (MCP)](06-mcp.md)
