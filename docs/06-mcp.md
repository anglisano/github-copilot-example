# 06 - Model Context Protocol (MCP)

The **Model Context Protocol (MCP)** is an open standard that allows connecting Copilot with data sources and external tools it doesn't know natively.

## 1. What is MCP?

MCP allows Copilot Chat to act as an "orchestrator." Through MCP servers, Copilot can:
- Query local databases (SQL, NoSQL).
- Read internal company documentation.
- Interact with third-party APIs (Jira, Confluence, Slack).
- Run browser testing tools (Playwright).

## 2. How to Configure MCP Servers

In VS Code, you can add MCP servers in the `mcp.json` configuration file.

**Configuration Example:**
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db", "my_database.db"]
    }
  }
}
```

## 3. What is it useful for day-to-day?

Imagine you are writing a SQL query. With MCP, Copilot can:
1. See the real schema of your local database.
2. Suggest the exact names of the columns.
3. Execute the query and show you the results directly in the chat.


## 4. Conceptos y Simulación del Protocolo

Para entender cómo Copilot se comunica con herramientas externas, es vital distinguir los dos roles principales:

| Rol | Descripción | Ejemplo |
|:--- |:--- |:--- |
| **MCP Client** | El "cerebro" o host que orquestra las llamadas. | GitHub Copilot en VS Code. |
| **MCP Server** | El "conector" que expone herramientas, recursos o prompts. | Nuestro servidor dummy en Python. |

La comunicación se basa en **JSON-RPC 2.0** sobre un canal de **Server-Sent Events (SSE)** para recibir eventos y **HTTP POST** para enviar comandos.

### Simulación en Vivo (Live Demo)

Sigue estos pasos para simular cómo Copilot "habla" con el servidor MCP usando `curl`.

#### Paso 0: Preparación
Primero, obtén un token y define la sesión en tu terminal.

```bash
# 1. Abre el enlace en el navegador para obtener el id_token (JWT)
# URL: https://login.microsoftonline.com/... (ver arriba)

# 2. Configura las variables de entorno (Bash/Zsh)
export token="TU_TOKEN_AQUÍ"
export session="d63eebf17f8444ce88a644535da06f62"
export base_url="http://localhost:8000"
```

#### Paso 1 — Inicialización
El cliente debe identificarse y negociar la versión del protocolo.

```bash
curl -s -X POST "$base_url/messages/?session_id=$session" \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": { "name": "demo-client", "version": "1.0" }
    }
  }'
```

#### Paso 2 — Notificación de éxito
Confirmamos al servidor que estamos listos para operar.

```bash
curl -s -X POST "$base_url/messages/?session_id=$session" \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
```

#### Paso 3 — Listar Herramientas (Discovery)
Aquí es donde Copilot "descubre" qué puede hacer tu servidor.

```bash
curl -s -X POST "$base_url/messages/?session_id=$session" \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'
```

#### Paso 4 — Ejecutar una Herramienta
Invocamos una lógica específica (ej. el clima en Madrid).

```bash
curl -s -X POST "$base_url/messages/?session_id=$session" \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "get_weather",
      "arguments": { "city": "Madrid" }
    }
  }'
```




---
[Next Session: Resources and Continuity](07-resources.md)
