# 01 - Initial Setup and Installation

To get started with GitHub Copilot, we need to prepare our VS Code environment and ensure the connection is stable, especially in corporate environments.

## 1. Extension Installation

Search for and install the following extensions from the VS Code Marketplace:

1.  **GitHub Copilot Chat**: The chat interface and inline functionality (`Ctrl+I`).

<img src="../assets/images/01-extencion.png" alt="Extensions State" style="width: 25%;">

## 2. Login and Activation

Once installed:
1.  Click on the **User** icon in the bottom-left corner (or the Copilot icon in the status bar).
2.  Select **Sign in to GitHub**.
3.  Follow the steps in the browser to authorize VS Code.
4.  If everything is correct, you will see the Copilot icon in the bottom status bar without errors.

<img src="../assets/images/01-login.png" alt="Login State" style="width: 25%;">

## 3. Corporate Proxy Configuration (UV/PIP)

In environments with a corporate proxy, you might experience SSL certificate issues (`SSL: CERTIFICATE_VERIFY_FAILED`). To work with Python smoothly in this repo:

### For `uv`:
Use these flags to allow insecure hosts locally:
```sh
uv sync --allow-insecure-host files.pythonhosted.org --allow-insecure-host pypi.org
uv add <pkg> --allow-insecure-host files.pythonhosted.org --allow-insecure-host pypi.org
```

### For `pip`:
```sh
pip install <pkg> --trusted-host files.pythonhosted.org --trusted-host pypi.org
```

> **Note**: These flags are only necessary for local dependency installation.

---
[Next Session: Basic Features](02-basics.md)
