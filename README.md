# X
The full codebase of Ability.

## Prerequisites:
- Python >= 3.10
- Node.js >= 20
- Claude Code >= 2.0.0: `npm install -g @anthropic-ai/claude-code`


## TL;DR

```bash
# backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
fastapi dev app/main.py

# frontend
cd frontend
npm ci
npm run dev
```

## Getting Started

### 1. Clone & Configure
```bash
cp backend/.env.example backend/.env
# Edit secrets
```

### 2. Start Services
```bash
cd backend
docker compose up --build
```

API at http://localhost:8000
Docs at http://localhost:8000/docs

### 3. Run Migrations
```bash
docker compose exec api alembic upgrade head
```

### 4. Register & Test
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"me@example.com","password":"pass123"}'
```

### 5. Frontend (Vue 3)
```bash
cd frontend
npm ci
npm run dev
```

Frontend at http://localhost:5173

## Development
- `make dev` hot reload backend
- `make test` run tests
- Frontend includes Pinia for state management
- Vue Router with route guards for authentication

## Production Notes
- Use gunicorn with uvicorn workers
- Terminate TLS at a reverse proxy (nginx / traefik)
- Rotate JWT secret keys carefully
- Enable structured tracing (OpenTelemetry)
- Add request ID middleware and propagate
- Build frontend with `npm run build` and serve static files

## Vue Frontend Features
- **Vue 3 Composition API** with TypeScript
- **Pinia** for state management
- **Vue Router** with navigation guards
- **daisyUI** for UI components
- **Ky** for API requests
- **TanStack Vue Query** for server state management
- Responsive design with scoped CSS
- Authentication flow with token management
- Protected routes and automatic redirects
