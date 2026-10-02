# RiskLens AI

> **An Adaptive, Explainable Cyber Risk Intelligence Platform** — *"Know your digital
> risk before it becomes a threat."*

RiskLens AI is a full-stack, production-ready AI cybersecurity platform that detects
threats (phishing URLs, spam emails, weak credentials), **explains why** with SHAP-based
Explainable AI, computes a **Cyber Health Score**, delivers **personalized security
advice**, and lets users download **PDF/CSV reports** — all behind a professional,
Defender/CrowdStrike-style dashboard.

---

## ✨ Features

| Module | What it does |
|---|---|
| **User Authentication** | Register, login (username/email), JWT access + refresh tokens |
| **Dashboard** | Cyber Health Score gauge, risk trend, threat summary, live charts |
| **URL Threat Detection** | Phishing classifier w/ feature engineering |
| **Email Spam Detection** | Spam/ham classifier over email & SMS text |
| **Credential Risk Analyzer** | Entropy, patterns, dictionary & common-password scoring |
| **Explainable AI** | SHAP feature importance + human-readable explanation |
| **Cyber Health Score** | Weighted blend of URL, spam, credential, awareness, history |
| **AI Security Advisor** | Personalized, evidence-based security tips |
| **Threat History** | Paginated scan history + detail |
| **Reports** | Branded PDF report + CSV export |
| **Admin Dashboard** | Platform stats, user list, per-type scan analytics |
| **API Documentation** | Auto-generated Swagger UI at `/docs` |

**Every prediction returns six fields:** `prediction · confidence · risk_score ·
feature_importance · explanation · recommendation`.

---

## 2. Tech Stack

- **Backend:** Python 3.10 · FastAPI · SQLAlchemy 2.0 · Pydantic v2
- **ML / XAI:** Scikit-learn · SHAP · NumPy · Pandas
- **Database:** PostgreSQL (SQLite fallback for zero-setup local dev)
- **Auth:** python-jose (JWT) · bcrypt
- **Frontend:** React 18 · Vite · Tailwind CSS · Chart.js · Axios
- **Deployment:** Docker · Docker Compose · Nginx · Git

---

## 3. Project Structure

```
risklens-ai/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint + lifespan
│   │   ├── api/v1/endpoints/  # controllers (auth, url, email, credential, …)
│   │   ├── core/              # config, logging, security, dependencies, bootstrap
│   │   ├── db/                # engine, session, Base
│   │   ├── models/            # SQLAlchemy ORM models (user, assessment, health, advisor)
│   │   ├── schemas/           # Pydantic request/response models
│   │   ├── services/          # business logic (SOLID, single responsibility)
│   │   ├── repositories/      # database access layer
│   │   ├── ml/                # feature engineering + models + SHAP explainers
│   │   └── utils/             # helpers
│   └── tests/                 # pytest suite
├── frontend/                  # React + Tailwind + Chart.js SPA
├── docker/nginx/nginx.conf     # reverse-proxy config
├── datasets/                   # (git-ignored) raw datasets
├── notebooks/                  # (planned) EDA / training
├── docs/                       # architecture & UML diagrams
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

**Clean architecture:** controllers speak HTTP → services hold domain logic →
repositories own persistence → schemas validate I/O. Each layer is SOLID and
independently testable.

---

## 4. Quickstart (Local Development)

> Python 3.10+ and Node 18+ required.

### Backend

```powershell
# 1. Create + activate a venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Configure environment (creates bootstrap admin + admin/multi DB)
Copy-Item .env.example .env   # (edit if needed; defaults work locally)

# 4. Run the API (from backend/ folder so `app` is importable)
cd backend
..\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for interactive Swagger UI.

> On first start the app auto-creates tables and a bootstrap admin:
> **admin / Admin@123456** (already present in `.env`).

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The Vite dev server proxies `/api` → `:8000`,
so the whole app works with a single browser tab.

### Login

- Create an account, or use the seeded admin: `admin / Admin@123456`

---

## 5. Tests

```powershell
.\venv\Scripts\python.exe -m pytest -v
```

Covers health, auth (register/login/refresh, 401/403 guards), URL/email/credential
scans (verifying the six output fields), dashboard, threat history, and CSV/PDF reports.

---

## 6. API Overview

All endpoints under `/api/v1` (Swagger at `/docs`):

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create account → returns tokens |
| POST | `/auth/login` | Login (username/email) → returns tokens |
| POST | `/auth/refresh` | Exchange refresh for a fresh access token |
| GET | `/auth/me` | Current authenticated user |
| GET | `/dashboard` | Health score + components + activity |
| POST | `/awareness` | Update awareness quiz score |
| POST | `/url` | Analyze a URL |
| POST | `/email` | Analyze email / SMS text |
| POST | `/credential` | Assess a password |
| GET | `/advisor` | List personalized tips |
| POST | `/advisor/{id}/read` · `/advisor/read-all` | Acknowledge tips |
| GET | `/threats` | Paginated threat history |
| GET | `/threats/{id}` | Threat detail |
| GET | `/reports/csv` | CSV export |
| GET | `/reports/pdf` | PDF security report |
| GET | `/admin/stats` · `/admin/users` | Admin oversight (`role=admin`) |
| GET | `/health` | Service health / uptime |

**Example scan response (every detection module):**

```json
{
  "prediction": "phishing",
  "confidence": 0.94,
  "risk_score": 94.5,
  "feature_importance": {"has_at_symbol": 1.9, "use_https": -1.8, "keyword_volume": 1.4},
  "explanation": "The 'has_at_symbol' signal was the strongest factor…",
  "recommendation": "Do NOT click this link. It shows multiple phishing indicators…",
  "raw_score": 0.945,
  "details": {"top_features": {}}
}
```

---

## 7. Machine Learning Workflow

This project ships a complete, honest ML pipeline that works out of the box
(built on engineering weights) and is structured so it can be retrained on real data.

1. **Feature engineering** (`ml/url_features.py`, `ml/detectors.py`) — encode
   security heuristics (HTTPS, IP-host, suspicious TLDs, subdomains, urgency words…).
2. **Interpretable model** (`ml/engine_base.py`) — a scikit-learn `LogisticRegression`
   whose coefficients *are* the domain weights (deterministic, fast).
3. **Explainable AI** — `shap.LinearExplainer` computes exact per-feature
   contributions (why a prediction is risky).
4. **Risk engine** — sigmoid probabilities → `risk_score` + threshold bands.
5. **Cyber Health Score** — 5 weighted components → aggregate posture (0–100).
6. **Advisor** — turns low components into targeted, prioritized recommendations.

> Replace `weights` with coefficients from `RandomForest`/`XGBoost` trained on real
> datasets under `datasets/` (see `notebooks/`) — the API & SHAP layers never change.

---

## 7. Docker Deployment

Docker is optional and no extra services are needed for local dev (SQLite fallback).
To run the full production stack (PostgreSQL + API + Nginx-served UI):

```powershell
# install Docker Desktop, then:
docker compose up --build
```

- Backend: `http://localhost:8000`
- Frontend (Nginx): **http://localhost:8080**
- PostgreSQL on `:5432`

`docker-compose.yml` wires a Postgres container with a healthcheck, the backend that
reads `DATABASE_URL` (switched to postgres automatically), and a multi-stage frontend
that builds the React app and serves it via Nginx while reverse-proxying `/api`.

## 8. Render Deployment

The repository includes a [`render.yaml`](./render.yaml) Blueprint that deploys
the complete application as three Render resources:

- `risklens-backend`: FastAPI web service
- `risklens-frontend`: React/Vite static site
- `risklens-db`: PostgreSQL database

### Deploy with the Blueprint

1. Push the repository to GitHub.
2. In Render, choose **New → Blueprint** and select this repository.
3. Keep the repository root as the Blueprint root and apply `render.yaml`.
4. Provide values for `ADMIN_USERNAME`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD`
   when Render prompts for the backend service secrets.
5. Wait for the database, backend, and frontend deployments to finish.
6. Verify the backend at:

   ```text
   https://risklens-backend.onrender.com/api/v1/health
   ```

The Blueprint sets `VITE_API_URL` on the frontend, configures the FastAPI
service to listen on Render's `$PORT`, and adds the React Router rewrite.
If Render assigns different service URLs, update `VITE_API_URL` on the
frontend and `CORS_ORIGINS` on the backend to match those URLs, then redeploy.

Render's free web services can sleep after inactivity, so the first request
after a period of inactivity may take several seconds.

The backend is pinned to Python 3.10.13 because the pinned scientific
dependencies provide compatible prebuilt wheels for that runtime. Do not
change the Render service to Python 3.14 without upgrading and retesting the
entire ML dependency set.

## 9. Vercel Deployment

Vercel is configured to build and serve the React/Vite frontend from the
repository root. The FastAPI service contains large ML dependencies and should
run as a separate persistent service (for example, Render, Railway, or a VM);
Vercel's serverless Python runtime is not a suitable replacement for this
backend.

### Deploy the frontend

1. Push the repository to GitHub and import it into Vercel.
2. Keep the project root as the repository root. The checked-in `vercel.json`
   runs the frontend build and serves `frontend/dist`.
3. Add this Vercel project environment variable:

   ```text
   VITE_API_URL=https://<your-backend-domain>/api/v1
   ```

   The value must include `/api/v1` and must not have a trailing slash.
4. Deploy. The rewrite in `vercel.json` keeps React Router routes working on
   direct navigation and refresh.

### Configure the backend

Set the backend's `CORS_ORIGINS` environment variable to the deployed Vercel
origin (and any local origins you still need), for example:

```text
CORS_ORIGINS=["https://<your-project>.vercel.app","http://localhost:5173"]
```

Also set a strong, unique `JWT_SECRET_KEY`, a production `DATABASE_URL`, and
production admin credentials. After the backend is reachable, verify
`https://<your-backend-domain>/api/v1/health`, then open the Vercel URL.

---

## 10. Roadmap

| Sprint | Component | Status |
|---|---|---|
| 1 | Project setup & environment | ✅ |
| 2 | Authentication (JWT) + DB | ✅ |
| 3 | Dashboard API | ✅ |
| 4 | URL threat detection | ✅ |
| 5 | Email spam detection | ✅ |
| 6 | Credential risk analyzer | ✅ |
| 7 | Explainable AI (SHAP) | ✅ |
| 8 | Cyber Health Score | ✅ |
| 9 | AI Security Advisor | ✅ |
| 10 | Threat history | ✅ |
| 11 | Reports (PDF/CSV) | ✅ |
| 12 | Admin dashboard | ✅ |
| 13 | Frontend (React + Tailwind) | ✅ |
| 14 | Docker / Nginx | ✅ (files ready) |

---

## 11. License & Attribution

© 2026 RiskLens AI. Built as an educational cybersecurity / ML engineering project.