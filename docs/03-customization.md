# 03 - Customization and Gitflow

GitHub Copilot allows you to customize how the AI behaves to adapt to your team's standards. One of the most useful features is the generation of commit messages.

## 1. Commit Rule Configuration

For Copilot to use our **Gitflow** rules, we must configure VS Code:

1.  Open VS Code settings (`Ctrl + ,`).
2.  Search for: `github.copilot.chat.commitMessageGeneration.instructions`.
3.  Add an entry pointing to our instructions file:

```json
"github.copilot.chat.commitMessageGeneration.instructions": [
    {
        "file": ".github/copilot-commit-message-instructions.md"
    }
]
```

## 2. The Instructions File

We have created the file [.github/copilot-commit-message-instructions.md](../.github/copilot-commit-message-instructions.md) with the following content:

- Use of prefixes: `feat:`, `fix:`, `chore:`, etc.
- Imperative format.
- Prohibition of periods at the end of the subject.

## 3. Example of Use

1. Make a change in any file (for example, add a comment in `src/test_logic.py`).
2. Go to the **Source Control** tab.
3. Click on the "sparkle" icon (✨) in the commit message field.
4. Watch how Copilot generates a message following the Gitflow standard!

---
[Next Session: Project Instructions](04-project-instructions.md)
