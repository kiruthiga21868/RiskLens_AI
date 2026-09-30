# RiskLens AI — Architecture & Design

> All diagrams are [Mermaid](https://mermaid.js.org) — they render natively on GitHub.

---

## 1. System Architecture

```mermaid
flowchart TB
    subgraph Client
        Browser["User Browser"]
    end

    subgraph Frontend["React SPA (Vite)"]
        UI["Dashboard / Scanners / Advisor / Reports"]
    end

    subgraph Nginx
        proxy["Nginx reverse-proxy (/api → backend)"]
    end

    subgraph Backend["FastAPI Application (Clean Architecture)"]
        Controllers["Controllers (routes)"]
        Services["Services (business logic)"]
        Repos["Repositories (persistence)"]
        ML["ML layer (models + SHAP)"]
        Auth["JWT / bcrypt"]
    end

    subgraph Data
        DB[("PostgreSQL / SQLite")]
    end

    Browser --> UI
    UI --> proxy
    proxy --> Controllers
    Controllers --> Services
    Services --> Repos
    Services --> ML
    Auth --> Services
    Repos --> DB
```

---

## 2. Database ER Diagram

```mermaid
erDiagram
    USERS ||--o{ ASSESSMENTS : "scans"
    USERS ||--o{ HEALTH_SNAPSHOTS : "has"
    USERS ||--o{ ADVISOR_MESSAGES : "receives"

    USERS {
        int id PK
        string username UK
        string email UK
        string hashed_password
        string full_name
        string role
        bool is_active
        int awareness_score
        datetime created_at
        datetime last_login
    }

    ASSESSMENTS {
        int id PK
        int user_id FK
        string type
        text content
        string prediction
        float confidence
        float risk_score
        json feature_importance
        text explanation
        text recommendation
        float raw_score
        json details
        datetime created_at
    }

    HEALTH_SNAPSHOTS {
        int id PK
        int user_id FK
        float health_score
        float url_safety
        float spam_exposure
        float credential_strength
        float awareness_score
        float threat_history
        json factors
        datetime created_at
    }

    ADVISOR_MESSAGES {
        int id PK
        int user_id FK
        string title
        text message
        string category
        string priority
        bool is_read
        datetime created_at
    }
```

---

## 3. Detection Sequence (scan → health → advice)

```mermaid
sequenceDiagram
    participant U as User
    participant FE as React UI
    participant API as FastAPI Controller
    participant SVC as DetectionService
    participant ML as ML + SHAP
    participant DB as Database
    participant HS as HealthScoreService

    U->>FE: submits URL / email / password
    FE->>API: POST /api/v1/{url,email,credential} (JWT)
    API->>SVC: run_and_persist(user, kind, input)
    SVC->>ML: analyze(input)
    ML-->>SVC: {prediction, confidence, risk_score, importance, explanation, recommendation}
    SVC->>DB: INSERT assessment
    SVC-->>API: unified result + id
    API->>HS: recompute health snapshot
    HS->>DB: INSERT health_snapshot
    API->>AdvisorService: regenerate tips
    API-->>FE: 200 unified response
    FE-->>U: prediction card + SHAP bars + recommendation
```

---

## 4. Use Case Diagram

```mermaid
flowchart LR
    User((User))
    Admin((Admin))

    User -->|register / login| A1[Authentication]
    User -->|view| A2[Dashboard & Health Score]
    User -->|scan| A3[URL Threat Detection]
    User -->|scan| A4[Email Spam Detection]
    User -->|scan| A5[Credential Risk Analyzer]
    User -->|read| A6[AI Advisor tips]
    User -->|browse| A7[Threat History]
    User -->|download| A8[PDF / CSV Reports]
    Admin -->|oversee| A9[Platform Stats & Users]
```

---

## 5. Deployment Diagram

```mermaid
flowchart LR
    Internet((Internet))
    subgraph Docker Host
        N[Nginx :80]
        FE[Frontend Container (React build)]
        BE[Backend Container (uvicorn :8000)]
        DB[(PostgreSQL :5432)]
        N --> FE
        N -->|/api| BE
        BE --> DB
    end
    Internet --> N
```

---

## 6. Cyber Health Score Formula

```
HealthScore = 0.30·URL_Safety + 0.20·Spam_Exposure
            + 0.20·Credential_Strength + 0.15·Awareness
            + 0.15·Threat_History
```

Each component is derived per-user from stored assessments:

- **URL Safety** = 100 − avg(url risk_score)
- **Spam Exposure** = 100 − avg(email risk_score)
- **Credential Strength** = 100 − avg(credential risk_score)
- **Awareness** = user's quiz score (0–100)
- **Threat History** = 85 − (high-risk share × 65), floor 20

**Status bands:** ≥80 Excellent · ≥60 Good · ≥40 Fair · <40 At Risk

---

## 7. Detection Pipeline (every module)

```mermaid
flowchart LR
    Raw["Raw input"] --> Feat["Feature engineering"]
    Feat --> Model["Logistic regression (domain weights)"]
    Model --> Prob["Sigmoid probability"]
    Prob --> Risk["risk_score 0-100 + threshold"]
    Prob --> Conf["confidence"]
    Prob --> SHAP["shap.LinearExplainer"]
    SHAP --> Imp["feature_importance"]
    Imp --> Exp["explanation (top signals)"]
    Risk --> Rec["recommendation (rules)"]
    Exp --> Out["Unified 6-field response"]
    Rec --> Out
```