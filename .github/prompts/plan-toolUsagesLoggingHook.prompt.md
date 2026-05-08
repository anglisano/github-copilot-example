# Plan: tool_usages table + logging hook + VS Code agent

## Goal
Create a `tool_usages` SQLite table, a Python logging hook (decorator + proxy middleware)
that auto-inserts a record on every tool call, and a VS Code `.agent.md` for querying analytics.

---

## Phase 1 — SQLite table

**Step 1**: Create `tool_usages` via `mcp_mcp-local1_create_table` (can be done immediately).

Schema:
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `timestamp` TEXT NOT NULL  (ISO 8601 UTC)
- `tool_name` TEXT NOT NULL
- `arguments_json` TEXT       (JSON-encoded kwargs)
- `duration_ms` REAL
- `is_error` INTEGER          (0 or 1)
- `result_preview` TEXT       (first 300 chars of result/error)

---

## Phase 2 — Python hook: `tool_logger.py`

**Step 2**: Create `src/mcp_server/tool_logger.py`
- Imports: `functools`, `inspect`, `json`, `sqlite3`, `time`, `datetime`, `timezone`
- Uses the same `DB_PATH` as `proxy_loader.py` (re-derive with `os.path`)
- `_insert_log(tool_name, arguments_json, result_preview, duration_ms, is_error)` — opens a
  short-lived `sqlite3.connect(DB_PATH)` per call (thread-safe, no connection state to manage)
- `log_tool_usage(func)` — single decorator that handles both sync and async functions via
  `inspect.iscoroutinefunction`. Uses `functools.wraps(func)` to preserve `__wrapped__` so
  FastMCP's `inspect.signature()` sees the original parameters.

---

## Phase 3 — Apply hook to native tools

**Step 3**: Modify `src/mcp_server/dummy_tools.py`
- Import `log_tool_usage` from `..tool_logger`
- Stack decorator INSIDE `@mcp.tool()` for all 6 tools:
  ```
  @mcp.tool()
  @log_tool_usage
  def get_weather(...): ...
  ```
  FastMCP reads signature via `inspect.signature()` which follows `__wrapped__`, so it sees the
  original params even after wrapping.

**Step 4**: Modify `src/mcp_server/services/fetch_tools.py`
- Same pattern — add `@log_tool_usage` inside `@mcp.tool()` on `fetch_url_as_markdown`.

---

## Phase 4 — Apply hook to proxied tools

**Step 5**: Modify `src/mcp_server/services/proxy_loader.py`
- Import `log_tool_usage` from `..tool_logger`
- In `_register_proxy_tool`, wrap `proxy_fn` with `log_tool_usage` BEFORE calling `mcp.add_tool`:
  ```python
  proxy_fn = log_tool_usage(proxy_fn)
  mcp.add_tool(proxy_fn, name=tool_name, description=description)
  ```
- The `_ProxyArgModel` patching that follows still applies to the same tool slot.

---

## Phase 5 — VS Code Agent

**Step 6**: Create `.github/agents/tool-usage-analyst.agent.md`
- Name: `tool-usage-analyst`
- Knows the full schema of `tool_usages`
- Uses the sqlite MCP tool (read_query) to answer questions:
  - Most called tools, error rates, slowest tools, usage over time
- Knows the MCP server URL is `http://localhost:8000/sse`

---

## Files to create/modify

| Action | File |
|--------|------|
| CREATE | `src/mcp_server/tool_logger.py` |
| MODIFY | `src/mcp_server/dummy_tools.py` |
| MODIFY | `src/mcp_server/services/fetch_tools.py` |
| MODIFY | `src/mcp_server/services/proxy_loader.py` |
| CREATE | `.github/agents/tool-usage-analyst.agent.md` |

## Verification
1. Restart MCP server (`uvicorn src.mcp_server.server:app --reload`)
2. Call any tool (e.g., `get_weather London`)
3. Query: `SELECT * FROM tool_usages ORDER BY id DESC LIMIT 5;`
4. Confirm row appears with correct tool_name, duration_ms, etc.
5. Invoke `tool-usage-analyst` agent in VS Code and ask "What are the most used tools?"

## Decisions
- Direct `sqlite3` per-call (not the proxied mcp-server-sqlite) — avoids circular dependency
  and works before/during proxy server startup.
- Decorator applied INSIDE `@mcp.tool()` so FastMCP sees original signature via `__wrapped__`.
- Proxied tools: wrap `proxy_fn` before `mcp.add_tool()` — single injection point.
- `result_preview` capped at 300 chars to avoid bloating the DB.
