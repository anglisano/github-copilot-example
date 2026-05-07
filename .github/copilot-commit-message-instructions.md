# Commit Message Instructions (Gitflow)

Siempre que generes un mensaje de commit, sigue estas reglas de **Gitflow**:

1.  **Formato del Asunto**: `tipo(scope): descripción corta en minúsculas`
2.  **Tipos permitidos**:
    - `feat`: Una nueva característica.
    - `fix`: Una corrección de errores.
    - `docs`: Cambios en la documentación.
    - `style`: Cambios que no afectan el significado del código (espacios, formato, etc.).
    - `refactor`: Un cambio de código que no corrige un error ni añade una característica.
    - `perf`: Un cambio de código que mejora el rendimiento.
    - `test`: Añadir pruebas existentes o corregir pruebas existentes.
    - `chore`: Cambios en el proceso de construcción o herramientas auxiliares.
3.  **Descripción**:
    - Usa el imperativo ("añade" en lugar de "añadido").
    - No pongas punto final al asunto.
4.  **Cuerpo**: (Opcional) Explica el "por qué" del cambio, no el "cómo". Especialmente si es un `refactor` o `fix` complejo.
