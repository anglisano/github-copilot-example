# 06 - Model Context Protocol (MCP)

El **Model Context Protocol (MCP)** es un estándar abierto que permite conectar Copilot con fuentes de datos y herramientas externas que no conoce de forma nativa.

## 1. ¿Qué es MCP?

MCP permite que CopilotChat actúe como un "orquestador". A través de servidores MCP, Copilot puede:
- Consultar bases de datos locales (SQL, NoSQL).
- Leer documentación interna de tu empresa.
- Interactuar con APIs de terceros (Jira, Confluence, Slack).
- Ejecutar herramientas de testing en el navegador (Playwright).

## 2. Cómo configurar servidores MCP

En VS Code, puedes añadir servidores MCP en el archivo de configuración `mcp.json`.

**Ejemplo de configuración:**
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db", "mi_base_de_datos.db"]
    }
  }
}
```

## 3. ¿Para qué sirve en el día a día?

Imagina que estás escribiendo una query SQL. Con MCP, Copilot puede:
1. Ver el esquema real de tu base de datos local.
2. Sugerirte el nombre exacto de las columnas.
3. Ejecutar la query y mostrarte los resultados directamente en el chat.

---
[Próxima Sesión: Recursos y Continuidad](07-recursos.md)
