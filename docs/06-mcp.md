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


## 4. Concepts and Protocol Simulation

To understand how Copilot communicates with external tools, it is vital to distinguish the two main roles:

| Role | Description | Example |
|:--- |:--- |:--- |
| **MCP Client** | The "brain" or host that orchestrates the calls. | GitHub Copilot in VS Code. |
| **MCP Server** | The "connector" that exposes tools, resources, or prompts. | Our dummy server in Python. |

Communication is based on **JSON-RPC 2.0** over a **Server-Sent Events (SSE)** channel to receive events and **HTTP POST** to send commands.

### Live Protocol Simulation

Follow these steps to simulate how Copilot "talks" to the MCP server using `curl` from a **Windows CMD** terminal.

#### Step 0: Preparation
First, get a token and define the environment variables.
[login](https://login.microsoftonline.com/f3fd384a-4c3e-4c97-97dc-3c473db5c614/oauth2/v2.0/authorize?client_id=834d78ef-0b30-44c8-9069-a686426e8b60&response_type=id_token&redirect_uri=https://jwt.ms&scope=openid%20profile%20email%20GroupMember.Read.All&response_mode=fragment&state=12345&nonce=67890)

```cmd
:: 1. Open the link in your browser to get the id_token (JWT)
:: URL: https://login.microsoftonline.com/... (see above)

:: 2. Configure environment variables (CMD)
set token=YOUR_TOKEN_HERE
set base_url=http://localhost:8000
```

establish a session
```cmd
curl -N -H "Authorization: Bearer %token%" "%base_url%/sse"
```
```cmd
set session=d63eebf17f8444ce88a644535da06f62
```

#### Step 1 — Initialization
The client must identify itself and negotiate the protocol version.

```cmd
curl -s -X POST "%base_url%/messages/?session_id=%session%" -H "Authorization: Bearer %token%" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\",\"capabilities\":{},\"clientInfo\":{\"name\":\"demo-client\",\"version\":\"1.0\"}}}"
```

#### Step 2 — Initialized Notification
We confirm to the server that we are ready to operate.

```cmd
curl -s -X POST "%base_url%/messages/?session_id=%session%" -H "Authorization: Bearer %token%" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\"}"
```

#### Step 3 — List Tools (Discovery)
This is where Copilot "discovers" what your server can do.

```cmd
curl -s -X POST "%base_url%/messages/?session_id=%session%" -H "Authorization: Bearer %token%" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\"}"
```

#### Step 4 — Execute a Tool
We invoke specific logic (e.g., weather in Madrid).

```cmd
curl -s -X POST "%base_url%/messages/?session_id=%session%" -H "Authorization: Bearer %token%" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/call\",\"params\":{\"name\":\"get_weather\",\"arguments\":{\"city\":\"Madrid\"}}}"
```




---
[Next Session: Resources and Continuity](07-resources.md)
