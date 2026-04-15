# Server Migration Runbook

This document explains how to move the `lp-agent` project from this machine to another server.

## 1. Decide What You Are Moving

You need to move:
- application source code
- environment configuration
- Python dependencies
- database file or database connection settings

You should **not** move:
- `lpenv/`

Reason:
- virtual environments are machine-specific
- this project now expects Python `3.13.5`
- the target server should create its own fresh virtual environment

## 2. Prerequisites On The Target Server

Install these first:
- Python `3.13.5`
- Git

Optional:
- PostgreSQL, if you do not want to keep using SQLite

## 3. Copy The Code To The Target Server

Option 1: clone from GitHub

```powershell
git clone https://github.com/kunalkaushik1982/lpagent.git
cd lpagent
```

Option 2: copy the project folder manually

If copying manually, exclude:
- `lpenv/`
- `__pycache__/`

## 4. Create A Fresh Virtual Environment

From the project root:

```powershell
python -m venv lpenv
.\lpenv\Scripts\python.exe --version
```

Expected:
- `Python 3.13.5`

## 5. Install Python Dependencies

For deployment, use the top-level pinned file:

```powershell
.\lpenv\Scripts\python.exe -m pip install -r requirements-top-level-pinned.txt
```

If you want a fully locked install with all transitive dependencies, use:

```powershell
.\lpenv\Scripts\python.exe -m pip install -r requirements-pinned.txt
```

Recommended default:
- `requirements-top-level-pinned.txt`

## 6. Configure Environment Variables

Create `.env` from `.env.example`.

Minimal SQLite setup:

```env
OPENAI_API_KEY=
DATABASE_URL=sqlite:///./lp_agent.db
```

If using PostgreSQL, first install the optional driver:

```powershell
.\lpenv\Scripts\python.exe -m pip install psycopg2-binary==2.9.11
```

Then set `DATABASE_URL` to something like:

```env
DATABASE_URL=postgresql://username:password@host:5432/dbname
```

## 7. Move The Database

### Option A: Keep SQLite

Copy this file from the current machine to the target server:

- `lp_agent.db`

Place it in the project root beside:
- `backend/`
- `frontend/`
- `.env`

### Option B: Switch To PostgreSQL

If switching to PostgreSQL:
- create the target database first
- update `DATABASE_URL`
- seed or migrate your data separately

This project currently has no Alembic migration flow, so SQLite-to-Postgres migration is manual.

## 8. Seed Data If Needed

If the database is empty, seed it:

```powershell
.\lpenv\Scripts\python.exe seed_data.py
```

## 9. Start The Backend

From the project root:

```powershell
.\lpenv\Scripts\uvicorn.exe backend.main:app --host 0.0.0.0 --port 8000
```

Check:
- `http://<server>:8000/`
- `http://<server>:8000/docs`

## 10. Serve The Frontend

The frontend is static HTML/CSS/JS.

Simple option:

```powershell
cd frontend
..\lpenv\Scripts\python.exe -m http.server 8080
```

Then open:

- `http://<server>:8080/`

If you use a proper web server later, point it at:
- `frontend/`

## 11. Important Frontend Deployment Note

The certificate feature currently loads `html2pdf.js` from a CDN in:

- [frontend/course-detail.html](/c:/Users/work/Documents/lp-agent/frontend/course-detail.html:439)

That means:
- the browser viewing the app needs internet access to download that script

If the target environment is isolated or internet-restricted, certificate download will fail unless you vendor that library locally.

## 12. Smoke Test After Migration

Run this checklist:

1. Open the frontend.
2. Register or log in.
3. Generate a learning plan.
4. Open a course detail page.
5. Mark a course complete after at least 20% progress.
6. Download the certificate PDF.
7. Confirm backend APIs respond at `/` and `/docs`.

## 13. Recommended Production Improvements

Before a real production deployment, consider these changes:

1. Put the frontend behind a real web server instead of `python -m http.server`.
2. Run FastAPI behind a process manager or service.
3. Vendor `html2pdf.js` locally instead of relying on CDN.
4. Pin and document the exact Python version as `3.13.5`.
5. Use PostgreSQL instead of SQLite if multiple users or concurrent writes matter.
6. Replace SHA-256 password hashing with `bcrypt` or `argon2`.
7. Restrict CORS in [backend/main.py](/c:/Users/work/Documents/lp-agent/backend/main.py:19).

## 14. Quick Command Summary

```powershell
git clone https://github.com/kunalkaushik1982/lpagent.git
cd lpagent
python -m venv lpenv
.\lpenv\Scripts\python.exe -m pip install -r requirements-top-level-pinned.txt
Copy-Item .env.example .env
.\lpenv\Scripts\uvicorn.exe backend.main:app --host 0.0.0.0 --port 8000
cd frontend
..\lpenv\Scripts\python.exe -m http.server 8080
```

## 15. Files You Will Commonly Copy Or Edit

- `.env`
- `lp_agent.db` if staying on SQLite
- `requirements-top-level-pinned.txt`
- `requirements-pinned.txt` if you want a full lock-style install
- `frontend/course-detail.html` if you later vendor the certificate library locally
