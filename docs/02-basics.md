# 02 - Basic Features

In this section, we will explore how to interact with Copilot in your daily workflow.

## 1. Ghost Text (Proactive Autocomplete)

Copilot suggests code as you type. These suggestions appear in gray (hence "Ghost Text").

**Exercise:**
1. Open a new file in `src/test_logic.py`.
2. Start typing a function to calculate the area of a circle.
3. Observe how Copilot proposes the body of the function.
   - `Tab` to accept.
   - `Alt + [` or `Alt + ]` to navigate between options.
   - `Ctrl + Enter` to see a panel with 10 complete suggestions.

## 2. Next Edit Suggestions

Copilot is now able to predict where you will make your next change based on your recent edits. You will see a change suggestion even before you start typing on that line.

## 3. Inline Chat (`Ctrl + I`)

Inline Chat is ideal for localized changes or quick refactorings without losing the focus of the file.

**Pro tips:**
- Select a block of code and press `Ctrl + I`.
- Ask: `/fix` to fix errors.
- Ask: `/doc` to generate documentation.
- Ask: "Convert this for loop into a list comprehension".

## 4. Chat Panel (`Ctrl + Alt + I`)

For more abstract queries or those that require more project context, use the side panel.
- Use `#file` to reference specific files.
- Use `@workspace` to ask about the entire codebase.

---
[Next Session: Customization and Gitflow](03-customization.md)
