# 03 - Personalización y Gitflow

GitHub Copilot permite personalizar cómo se comporta la IA para adaptarse a los estándares de tu equipo. Una de las funciones más útiles es la generación de mensajes de commit.

## 1. Configuración de Reglas de Commit

Para que Copilot use nuestras reglas de **Gitflow**, debemos configurar VS Code:

1.  Abre los ajustes de VS Code (`Ctrl + ,`).
2.  Busca: `github.copilot.chat.commitMessageGeneration.instructions`.
3.  Añade una entrada apuntando a nuestro archivo de instrucciones:

```json
"github.copilot.chat.commitMessageGeneration.instructions": [
    {
        "file": ".github/copilot-commit-message-instructions.md"
    }
]
```

## 2. El archivo de instrucciones

Hemos creado el archivo [.github/copilot-commit-message-instructions.md](../.github/copilot-commit-message-instructions.md) con el siguiente contenido:

- Uso de prefijos: `feat:`, `fix:`, `chore:`, etc.
- Formato imperativo.
- Prohibición de puntos finales en el asunto.

## 3. Ejemplo de Uso

1. Haz un cambio en cualquier archivo (por ejemplo, añade un comentario en `src/test_logic.py`).
2. Ve a la pestaña de **Source Control** (Control de código fuente).
3. Haz clic en el icono de la "chispa" (✨) en el campo del mensaje de commit.
4. ¡Observa cómo Copilot genera un mensaje siguiendo el estándar Gitflow!

---
[Próxima Sesión: Instrucciones de Proyecto](04-instrucciones-proyecto.md)
