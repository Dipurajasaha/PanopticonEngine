# Panopticon Engine

> **Panopticon Engine** is a finance intelligence platform designed for secure, role-aware, and analytics-driven decision support.
>
> Built on a microservice-oriented layout, it combines a **FastAPI backend** for secure data operations, **Redis-backed caching and version tracking** for faster refreshes, and a **Streamlit frontend** for interactive financial insights.

<p align="center">
	<strong>FastAPI</strong> • <strong>SQLAlchemy</strong> • <strong>SQLite</strong> • <strong>Redis</strong> • <strong>PyJWT</strong> • <strong>Streamlit</strong> • <strong>Docker Compose</strong>
</p>

---

## Overview

Panopticon Engine is engineered to turn financial records into actionable intelligence through a secure API layer, strict access governance, Redis-assisted caching, and a dedicated analytics computation layer.

It is designed to support:
- **Operational control** with authenticated and role-limited access.
- **Data lifecycle integrity** using soft deletion patterns.
- **Decision intelligence** through aggregated analytics dashboards.
- **Low-latency refresh behavior** through Redis cache + finance data version tracking.
- **Container-first execution** for predictable local and deployment workflows.

### Why This Platform Stands Out

- **Security-first API layer** with JWT and role-scoped endpoint access.
- **Analytical depth** through a dedicated mathematical aggregation engine.
- **Operational reliability** with strict filtering and soft-delete semantics.
- **Environment parity** from local development to containerized runtime.

---

## Architecture & Tech Stack

### Monorepo Service Layout

```text
docker-compose.yml
backend/    -> FastAPI microservice (API, auth, RBAC, persistence, analytics logic)
frontend/   -> Streamlit microservice (dashboard UI, API consumption)
```

### Service Interaction Flow

```text
User -> Streamlit Frontend (8501) -> FastAPI Backend (8000)
										  |-> SQLite via SQLAlchemy
										  |-> Redis (cache + data version flag)
```

### Backend Stack

- **FastAPI** for high-performance REST endpoints
- **SQLAlchemy** for ORM and database interaction
- **SQLite** for lightweight persistence
- **Redis** for dashboard caching and finance data version signaling
- **passlib (bcrypt)** for password hashing
- **PyJWT** for token-based authentication

### Frontend Stack

- **Streamlit** for an interactive analytics dashboard
- **Pandas** for in-app data shaping and tabular analysis
- **Requests** for backend API communication

### Deployment Stack

- **Docker** for service containerization
- **docker-compose** for multi-service orchestration
- **Redis container** for low-latency cache and version-key coordination

---

## Core Features

### 🔐 JWT Authentication
Secure authentication flow using signed JWT access tokens. Users authenticate once and interact with protected endpoints based on role claims.

### 🧠 Mathematical Analytics Engine
Dedicated analytics service layer computes dashboard-level aggregations and summaries to surface financial intelligence quickly and consistently.

### 🗂️ Soft Deletion
Records are never hard-deleted by default. Instead, logical deletion preserves historical continuity and auditability while keeping active views clean.

### 🎯 Robust Query Filtering
Finance retrieval endpoints support precise filtering to narrow large datasets efficiently:
- **Date-based filtering**
- **Category filtering**
- **Type filtering**

### ⚙️ Container-Native Execution
Two isolated services run in lockstep under Docker Compose, enabling reproducible startup, consistent networking, and clean dependency boundaries.

### 📊 Comprehensive Audit Logging
All critical actions (login, user creation, role updates, record operations) are logged to both the database and server terminal in real-time. Formatted audit logs display user ID, action type, affected resource, and contextual details for complete operational visibility.

### ⚡ Redis Cache + Version Flag Refresh
Panopticon Engine uses a two-layer freshness model for responsive pages and controlled refreshes:

- **Redis dashboard cache** stores precomputed global analytics summary to avoid repeated heavy aggregation.
- **Finance data version flag** is incremented on every finance create/delete transaction.
- **Frontend polling (every 5 seconds)** checks the version key via API.
- **Conditional refresh**: if version is unchanged, UI keeps current data; if changed, UI cache is invalidated and data is refetched.

This approach reduces unnecessary reloads while still keeping dashboard and explorer views fresh after transactions.

---

## Role-Based Access Control (RBAC)

| Role | Dashboard Access | Dashboard Data Scope | Finance Dataset View/Download | Create Record | Soft Delete Record | Manage Users |
|---|---:|---|---:|---|---|---:|
| **Viewer** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Analyst** | ✅ | ✅ | ✅ | ✅ (**own records only**) | ✅ (**own records only**) | ❌ |
| **Admin** | ✅ | ✅ | ✅ | ✅ (**own records only**) | ✅ (**own records only**) | ✅ |

### Dataset Access Rules (Important)

- **Dashboard is centralized/global**: all roles see the same aggregated financial summary.
- **Viewer cannot access raw records dataset**: dashboard only.
- **Analyst and Admin can view + download the full records dataset** in the explorer.
- **Record write model**: records are **creatable + soft-deletable only** (no update endpoint).
- **Ownership rule for writes**: Analyst/Admin can create and soft-delete only **their own records**.
- **Admin-only governance**: create users with roles, update user roles, and delete users.

---

## API Endpoints

### Security

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/auth/login` | Authenticate user and return JWT token | Public |

### User Management

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/users/` | List all users | Admin |
| `POST` | `/users/` | Public signup (always creates Viewer) | Public |
| `POST` | `/users/admin` | Create user with selected role | Admin |
| `PATCH` | `/users/{user_id}/role` | Change user role | Admin |
| `DELETE` | `/users/{user_id}` | Delete a user account | Admin |

### Finance Records

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/records/version` | Get current finance data version flag | Analyst/Admin |
| `POST` | `/records/` | Create new finance record | Analyst/Admin (own records) |
| `GET` | `/records/` | Read records dataset with filters | Analyst/Admin |
| `DELETE` | `/records/{record_id}` | Soft delete a record | Analyst/Admin (own records) |

### Dashboard Analytics

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/analytics/summary` | Global financial summary for dashboard | Viewer/Analyst/Admin |
| `GET` | `/analytics/version` | Get finance data version key for client polling | Viewer/Analyst/Admin |

### System

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/health` | Health check endpoint | Public |

### Query Filters for `/records/`

Supported query parameters:
- `record_type`
- `category`
- `start_date`
- `end_date`
- `skip`
- `limit`

---

## Quick Start (Docker)

### 0) Get the source code from GitHub

Clone the repository first:

```bash
git clone https://github.com/Dipurajasaha/PanopticonEngine.git
cd PanopticonEngine
```

If you already have the repo locally, pull the latest changes instead:

```bash
git pull origin main
```

### 1) Create `.env` at the project root

Create a `.env` file next to `docker-compose.yml` with the following values:

```env
DATABASE_URL=sqlite:///./panopticon.db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change_this_to_a_long_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
API_URL=http://backend:8000
```

### 2) Ensure `docker-compose.yml` matches this setup

```yaml
version: '3.8'

services:
	# -- Redis Cache/Version Store --
	redis:
		image: redis:7-alpine
		container_name: panopticon_redis
		ports:
			- "6379:6379"

	# -- FastAPI Server --
	backend:
		build: ./backend
		container_name: panopticon_backend
		ports:
			- "8000:8000"
		env_file:
			- .env
		volumes:
			# This saves SQLite database to local computer
			# so it doesn't get deleted when Docker turns off!
			- ./backend:/app 
		depends_on:
			- redis

	# -- Streamlit Dashboard --
	frontend:
		build: ./frontend
		container_name: panopticon_frontend
		ports:
			- "8501:8501"
		env_file:
			- .env
		depends_on:
			- backend
```

### 3) Build and run all services

```bash
docker-compose up --build
```

### 4) Open the platform

- **Frontend UI (Streamlit):** http://localhost:8501
- **Backend API Docs (Swagger):** http://localhost:8000/docs

### 5) Demo Accounts Created on First Run

On the first startup, the backend seed routine creates demo users automatically if the admin account does not already exist. This gives you ready-to-test accounts for each role without manual setup.

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@panopticon.com` | `admin123` |
| **Analyst** | `analyst@panopticon.com` | `analyst123` |
| **Viewer** | `viewer@panopticon.com` | `viewer123` |

The seeding logic is triggered during app startup in [backend/main.py](backend/main.py) and implemented in [backend/services/user_service.py](backend/services/user_service.py).

---

## Runtime Snapshot

After startup, the platform runs as two coordinated services:
- **backend**: authentication, user/finance endpoints, analytics computations
- **frontend**: dashboard client consuming backend APIs

This separation keeps business logic centralized while delivering a responsive analytics interface.

---

## Docker Guide Notes

- The backend API is available at [http://localhost:8000](http://localhost:8000).
- The Streamlit frontend is available at [http://localhost:8501](http://localhost:8501).
- The backend container uses the `./backend:/app` volume mount, which keeps the app files and SQLite database available across container restarts.
- The frontend service uses `depends_on` so Docker starts the backend before the frontend, but the backend may still need a few seconds to finish booting before the UI is fully ready.
