# ACEest Fitness & Gym — Automated CI/CD Pipeline

**Author:** Infant Selva | **BITS ID:** 2024TM93572  
**Course:** Introduction to DevOps — CSIZG514 / SEZG514 / SEUSZG514 | BITS Pilani WILP

[![CI/CD Pipeline](https://github.com/Infantselva-pilani/aceest-devops-assignment/actions/workflows/main.yml/badge.svg)](https://github.com/Infantselva-pilani/aceest-devops-assignment/actions/workflows/main.yml)

---

## Overview

This project implements a complete DevOps workflow for **ACEest Fitness & Gym**, a gym management system. I was appointed as a Junior DevOps Engineer to modernise an existing tkinter desktop application into a **Flask REST API** and build a full automated CI/CD pipeline using Git, Docker, GitHub Actions, and Jenkins.

Every code push automatically triggers linting, unit testing, and Docker image assembly — with zero manual steps.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Branch Strategy](#2-branch-strategy)
3. [Local Setup](#3-local-setup)
4. [Running the Tests](#4-running-the-tests)
5. [Docker](#5-docker)
6. [GitHub Actions Pipeline](#6-github-actions-pipeline)
7. [Jenkins Setup](#7-jenkins-setup)
8. [API Reference](#8-api-reference)

---

## 1. Project Structure

```
aceest-devops-assignment/
├── app.py                          # Flask REST API — 12 endpoints, SQLite backend
├── requirements.txt                # Python dependencies (flask, pytest, flake8, pytest-cov)
├── Dockerfile                      # Multi-stage build, non-root user, HEALTHCHECK
├── Jenkinsfile                     # 7-stage declarative pipeline (Windows-compatible)
├── README.md                       # This file
├── .gitignore                      # Excludes venv/, __pycache__/, *.db, test artifacts
├── .github/
│   └── workflows/
│       └── main.yml                # GitHub Actions: Lint → Test → Docker (triggers on push)
└── tests/
    └── test_app.py                 # 30 unit tests across 6 test classes (Pytest)
```

---

## 2. Branch Strategy

| Branch | Purpose |
|---|---|
| `devops-assignment-2` | Development — all assignment work done here |
| `master` | Submission — final merge from development branch |

All development is done in the feature branch. Once tested and verified, changes are merged into `master` for submission — mirroring industry branch management practices.

---

## 3. Local Setup

### Prerequisites

- Python 3.11 or higher
- pip
- Git
- Docker Desktop (for container steps)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Infantselva-pilani/aceest-devops-assignment.git
cd aceest-devops-assignment

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the Flask server
python app.py
# Server starts at http://localhost:5000
```

### Verify it's running

```bash
curl http://localhost:5000/health
# {"service": "ACEest Fitness API", "status": "healthy"}
```

---

## 4. Running the Tests

I wrote **30 unit tests** across 6 test classes using **Pytest**. Tests use a separate isolated database (`test_aceest.db`) and clean up after themselves — production data is never touched.

```bash
# Run all 30 tests with verbose output
pytest tests/ -v

# Run with coverage report (shows which lines are covered)
pytest tests/ -v --cov=app --cov-report=term-missing

# Run a specific test class only
pytest tests/test_app.py::TestClients -v
```

Expected output: **30 passed**

### Test coverage summary

| Class | Tests | What is covered |
|---|---|---|
| `TestHealth` | 2 | Health endpoint, JSON response structure |
| `TestClients` | 12 | Full CRUD, duplicate handling, 404 responses, input validation |
| `TestWorkouts` | 4 | Add workout, missing field validation, retrieve list |
| `TestProgress` | 5 | Adherence 0–100 boundary validation, missing client name |
| `TestMembership` | 2 | Membership status check, 404 for unknown client |
| `TestProgramGenerator` | 5 | All 3 goal types, unknown goal returns 400, empty body default |

---

## 5. Docker

The application is containerised using a **multi-stage Dockerfile**:

- **Stage 1 (builder):** installs all Python dependencies
- **Stage 2 (production):** copies only installed packages and source code — keeps the final image lean
- Non-root user `aceest` is created for security
- `HEALTHCHECK` is configured so Docker monitors the container automatically

```bash
# Build the image
docker build -t aceest-fitness:latest .

# Run the container
docker run -d -p 5000:5000 --name aceest aceest-fitness:latest

# Verify the container is healthy
curl http://localhost:5000/health
# {"service": "ACEest Fitness API", "status": "healthy"}

# Run the test suite inside the container (same as the pipeline does)
docker run --rm -v $(pwd)/tests:/app/tests aceest-fitness:latest python -m pytest tests/ -v

# Stop and remove
docker stop aceest && docker rm aceest
```

---

## 6. GitHub Actions Pipeline

**File:** `.github/workflows/main.yml`

Triggered automatically on every **push** to `master`, `devops-assignment-1`, or `test_devops-assignment-2`, and on every **pull request** to `master`.

### Pipeline stages

```
Push to branch
      │
      ▼
┌─────────────────┐
│  Stage 1        │  pip install + flake8 syntax check on app.py
│  Build & Lint   │  Fails immediately on any E9/F63/F7/F82 error
└────────┬────────┘
         │ pass only
         ▼
┌─────────────────┐
│  Stage 2        │  pytest tests/ -v --cov=app
│  Pytest Suite   │  30 tests must pass. Coverage report saved as artifact.
└────────┬────────┘
         │ pass only
         ▼
┌─────────────────┐
│  Stage 3        │  docker build → start container → curl /health
│  Docker Build   │  Then: pytest inside the running container
└─────────────────┘
```

Each stage only runs if the previous one passed. A lint failure stops the pipeline before wasting time on Docker.

**View live pipeline results:**  
`https://github.com/Infantselva-pilani/aceest-devops-assignment/actions`

---

## 7. Jenkins Setup

Jenkins serves as a **local BUILD server** running at `http://localhost:8070`, independent of GitHub Actions. It performs a secondary quality gate — even if GitHub were unavailable, Jenkins would still validate and deploy the code.

### Installation steps (Windows)

1. Download Jenkins LTS `.msi` from [jenkins.io](https://www.jenkins.io/download/)
2. Run the installer — Jenkins installs as a Windows Service
3. Open `C:\Program Files\Jenkins\jenkins.xml` and update the Java path to JDK 17:
   ```
   <executable>C:\Program Files\Java\jdk-17.0.10\bin\java.exe</executable>
   ```
4. Start the service: `net start Jenkins`
5. Open `http://localhost:8070` in your browser
6. Unlock with the initial admin password from:  
   `C:\ProgramData\Jenkins\.jenkins\secrets\initialAdminPassword`
7. Install suggested plugins, then add: **Git**, **Pipeline**, **Docker Pipeline**, **JUnit**, **Workspace Cleanup**
8. Add Python to Jenkins PATH:  
   `Manage Jenkins → System → Global properties → Environment variables`  
   Add: `PATH` = `C:\Program Files\Python313;C:\Program Files\Python313\Scripts;%PATH%`

### Creating the pipeline job

1. `New Item` → enter name: `aceest-fitness-pipeline` → select **Pipeline** → OK
2. Scroll to Pipeline section → Definition: **Pipeline script from SCM**
3. SCM: **Git** → Repository URL:  
   `https://github.com/Infantselva-pilani/aceest-devops-assignment.git`
4. Branch Specifier: `*/test_devops-assignment-2`
5. Script Path: `Jenkinsfile`
6. **Save** → **Build Now**

### Pipeline stages (7 stages)

| # | Stage | What it does |
|---|---|---|
| 1 | Checkout | Pulls latest code from GitHub |
| 2 | Setup Python | Creates `venv`, installs `requirements.txt` |
| 3 | Lint | `flake8` syntax check — stops on critical errors |
| 4 | Unit Tests | `pytest tests/` — 30 tests, generates `test-results.xml` for JUnit plugin |
| 5 | Docker Build | `docker build` — tags image with build number and `:latest` |
| 6 | Deploy | Stops old container, starts new one on port 5000, health check |
| 7 | Smoke Test | Hits `/health` and `/clients` on the live container |

---

## 8. API Reference

Base URL (local): `http://localhost:5000`

| Method | Endpoint | Description | Success |
|---|---|---|---|
| GET | `/health` | Service health check | 200 |
| GET | `/clients` | List all gym clients | 200 |
| POST | `/clients` | Register a new client | 201 |
| GET | `/clients/<name>` | Get a specific client | 200 |
| PUT | `/clients/<name>` | Update client details | 200 |
| DELETE | `/clients/<name>` | Remove a client | 200 |
| GET | `/workouts/<name>` | List all workouts for a client | 200 |
| POST | `/workouts` | Log a new workout session | 201 |
| GET | `/progress/<name>` | Get weekly adherence records | 200 |
| POST | `/progress` | Log weekly adherence (0–100) | 201 |
| GET | `/membership/<name>` | Check membership status | 200 |
| POST | `/generate-program` | Recommend a program by fitness goal | 200 |

### Example requests

```bash
# Register a new client
curl -X POST http://localhost:5000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "Ravi Kumar", "age": 27, "weight": 72.0, "program": "Muscle Gain"}'

# Log a workout
curl -X POST http://localhost:5000/workouts \
  -H "Content-Type: application/json" \
  -d '{"client_name": "Ravi Kumar", "workout_type": "Strength", "duration_min": 60}'

# Generate a fitness program recommendation
curl -X POST http://localhost:5000/generate-program \
  -H "Content-Type: application/json" \
  -d '{"goal": "Fat Loss"}'
# Available goals: "Fat Loss", "Muscle Gain", "Beginner"

# Check membership status
curl http://localhost:5000/membership/Ravi%20Kumar
```

---

*Infant Selva | 2024TM93572 | Introduction to DevOps | BITS Pilani WILP*
