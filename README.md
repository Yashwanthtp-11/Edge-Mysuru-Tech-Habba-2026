# KrishiVaani

KrishiVaani is an AI-powered assistance platform for farmers. Phase 1 provides the application foundation only: a React/Vite frontend, a FastAPI backend, environment configuration, and a health check.

## Structure

- `frontend/` - React + Vite dashboard shell
- `backend/app/` - FastAPI application, modular API routes, services, and configuration
- `backend/tests/` - backend tests

Weather, government schemes, AI, and voice features are intentionally not implemented in this phase.

## Setup

Copy `.env.example` to `.env` when local configuration is needed. Keep real credentials out of source control.

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The health endpoint is available at `http://localhost:8000/api/health`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The Vite development server normally runs at `http://localhost:5173`.

## Validation

Run backend tests from `backend/`:

```powershell
python -m pytest
```

Build the frontend from `frontend/`:

```powershell
npm run build
```