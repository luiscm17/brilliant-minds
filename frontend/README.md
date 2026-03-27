# Frontend DocSimplify

Aplicación frontend en Next.js para la experiencia de lectura adaptada.

## Scripts

```bash
npm run dev
npm run lint
npm run build
npm run start
```

Desarrollo local: `http://localhost:3000`

## Modos de ejecución

### Demo con mocks

Es el modo por defecto. No requiere backend ni Azure.

```bash
npm run dev
```

### Integrado con backend real

Crea `frontend/.env.local`:

```bash
NEXT_PUBLIC_USE_MOCK_API=false
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

Después levanta el backend FastAPI en `http://localhost:8001`.

## Qué cubre el frontend

- Landing interactiva
- Login y registro
- Onboarding de perfil cognitivo
- Dashboard adaptado
- Subida y listado de documentos
- Chat con respuesta simplificada

## Notas

- Si `NEXT_PUBLIC_USE_MOCK_API` no es `false`, la app usa datos mock en `localStorage`.
- El frontend está validado con `eslint` y `next build`.
