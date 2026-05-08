# 04 - Project Instructions

GitHub Copilot can read a special file in your repository to understand the global context, style rules, and preferred technologies.

## 1. The `/init` Command

In the Chat Panel (`Ctrl + Alt + I`), you can run the `/init` command. This command analyzes your workspace and helps you generate an initial instructions file.

## 2. `.github/copilot-instructions.md`

We have created this file manually for this session. Copilot will automatically read it in every query.

**What have we defined in [.github/copilot-instructions.md](../.github/copilot-instructions.md)?**
- Mandatory use of **type hints**.
- **PEP 8** style.
- Comment language: **English**.
- Test framework: `pytest`.

## 3. Context Demonstration with Agent Mode

**Exercise:**
1. Open Copilot Chat or use the agent command.
2. Ask the chat: "Create a file `src/processor.py` with a function that receives a list of dictionaries with sales and returns the total".
3. Watch how the Agent uses the `.github/copilot-instructions.md` file to:
   - Add mandatory **Type Hints**.
   - Write all **comments in English**.
   - Follow **PEP 8** style.
   - Prefer **functional programming** (using `sum()` for example).

*Note: It is recommended to use the Chat in Agent mode to ensure project instructions are always taken into account globally.*

---
[Next Session: Advanced Capabilities](05-advanced.md)
