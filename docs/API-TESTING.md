# API Testing Instructions

Este archivo describe cómo ejecutar la suite de solicitudes en `tests.http` para validar el flujo actual del backend (registro/login, documentos y salud).

## 1. Preparar el entorno

1. Instalar dependencias del proyecto (ej: `pip install -r requirements.txt`).
2. Crear variables de entorno mínimas:
   - `JWT_SECRET_KEY`: secreto para firmar tokens (cambiar antes de producción).
   - `AZURE_STORAGE_CONNECTION_STRING` y `AZURE_STORAGE_CONTAINER`: necesarios si activás la carga de documentos.
   - `AUTH_DB_PATH` (opcional): ruta del archivo SQLite que guarda los usuarios (`data/users.db` por defecto).
3. Asegurate de tener Azure Blob configurado o mocks si probás solo local.

## 2. Levantar el backend

```bash
uvicorn src.main:app --reload --port 8001
```

El host base para las pruebas es `http://localhost:8001/api/v1`, tal como usa `tests.http`.

## 3. Ejecutar `tests.http`

1. Abrí `tests.http` con la extensión REST Client (VS Code o similares).
2. Ejecutá las solicitudes en orden. La colección hace lo siguiente:
   - Registra un usuario; intenta un registro duplicado para validar el error.
   - Intenta login con contraseña inválida y luego con la correcta (la segunda petición se marca como `# @name login`).
   - Hace uploads de documento con y sin token, y con un MIME no permitido.
   - Lista los documentos y guarda el `blobName` para descargarlo y eliminarlo.
   - Llama al endpoint de chats (placeholder) y al endpoint `/health`.
3. Cada petición reutiliza el token devuelto por el login marcado; asegurate de ejecutar primero la sección `2.2 Auth: Login (valid)` antes de los demás pasos que necesitan autenticación.

## 4. Repetir pruebas / limpiar datos

- Si necesitás limpiar el almacén (por ejemplo para un nuevo registro), borrá el archivo `AUTH_DB_PATH` o `data/users.db` y reiniciá el backend.
- Las cargas de documentos se almacenan en Azure Blob; podés borrar manualmente en el portal o usar el endpoint `DELETE` incluido.

## 5. Qué validar

- Respuestas HTTP y esquemas (`AuthResponse`, `DocumentUploadResult`).
- Manejo de errores (409 para correo duplicado, 401/403 para falta de token o acceso indebido, 415 para MIME inválido).
- Propagación del `blobName` entre `list`, `download` y `delete`.
- Salud del servicio (`/health`).

## 6. Tips adicionales

- Si necesitás pruebas automatizadas, podés convertir `tests.http` en un script para `httpie` o `pytest` + `httpx`.
- Para probar entornos sin Azure, stubbeá `blob_service` o apuntá `BLOB_STORAGE_CONNECTION_STRING` a un emulador como Azurite.
