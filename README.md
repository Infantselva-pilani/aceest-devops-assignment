# ACEest Fitness & Gym — Automated CI/CD Pipeline

**Infant Selva | 2024TM93572**
Introduction to DevOps — CSIZG514/SEZG514/SEUSZG514 | BITS Pilani WILP

---

## What I Built and Why

For this assignment, I was given the role of a Junior DevOps Engineer for **ACEest Fitness & Gym**, a scaling startup that needed a proper automated deployment workflow. The existing codebase was a desktop application built with tkinter — it had no API, no tests, and no way to deploy it consistently across environments.

My goal was to modernise this into a **Flask REST API**, wrap it in Docker, and build a complete CI/CD pipeline using **GitHub Actions** and **Jenkins** — so that every time I push code, it automatically gets linted, tested, and containerised without any manual steps.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [How I Set It Up Locally](#how-i-set-it-up-locally)
3. [Running the Tests](#running-the-tests)
4. [Docker](#docker)
5. [GitHub Actions Pipeline](#github-actions-pipeline)
6. [Jenkins Setup](#jenkins-setup)
7. [API Reference](#api-reference)
8. [My Git Branching Approach](#my-git-branching-approach)

---

## Project Structure

```
aceest-devops-assignment/
├── app.py                        # My Flask REST API — the core application
├── requirements.txt              # Python packages I used
├── Dockerfile                    # How I containerised the app
├── Jenkinsfile                   # Jenkins pipeline I configured
├── .github/
│   └── workflows/
│       └── main.yml              # GitHub Actions — auto-runs on every push
├── tests/
│   └── test_app.py               # 30 unit tests I wrote using Pytest
└── README.md                     # This file
```

---

## How I Set It Up Locally

Before setting up any pipeline, I made sure the application runs cleanly on a local machine. Here are the steps I followed:

**Prerequisites:** Python 3.11+, pip, Git, Docker

```bash
# Clone the repository
git clone https://github.com/Infantselva-pilani/aceest-devops-assignment.git
cd aceest-devops-assignment

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# Install all dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
```

Once running, the API is available at `http://localhost:5000`. I can hit the `/health` endpoint to confirm it's live:

```bash
curl http://localhost:5000/health
# {"service": "ACEest Fitness API", "status": "healthy"}
```

---

## Running the Tests

I wrote 30 unit tests using **Pytest** covering every endpoint — happy paths, error cases, duplicate handling, and validation. I structured them into classes so it's easy to see which feature each test belongs to.

```bash
# Run all tests
pytest tests/ -v

# Run with coverage to see which lines are covered
pytest tests/ -v --cov=app --cov-report=term-missing

# Run just one class, for example only client tests
pytest tests/test_app.py::TestClients -v
```

All 30 tests pass locally. The same test suite is also executed inside the Docker container as part of the GitHub Actions pipeline.

---

## Docker

I containerised the application using a **multi-stage Dockerfile**. The first stage installs dependencies and the second stage copies only what's needed, keeping the final image lean. I also added a non-root user for basic security hygiene.

```bash
# Build the image
docker build -t aceest-fitness:latest .

# Run the container
docker run -d -p 5000:5000 --name aceest aceest-fitness:latest

# Verify it's healthy
curl http://localhost:5000/health

# Run tests inside the container (same as the pipeline does)
docker run --rm -v $(pwd)/tests:/app/tests aceest-fitness:latest python -m pytest tests/ -v

# Clean up
docker stop aceest && docker rm aceest
```

I verified that the container starts, passes the health check, and runs all tests successfully before wiring it into the pipeline.

---

## GitHub Actions Pipeline

I set up the pipeline in `.github/workflows/main.yml`. It triggers automatically on every **push** to `main` or `devops-assignment-1`, and on every **pull request** to `main`. This means I never have to manually run tests — they just happen.

The pipeline has three sequential stages:

| Stage | What it does |
|---|---|
| **Build & Lint** | Installs dependencies and runs `flake8` to catch any syntax or import errors in my code |
| **Pytest Suite** | Runs all 30 unit tests and generates a coverage report saved as an artifact |
| **Docker Build** | Builds the Docker image, starts a container, hits `/health`, then runs Pytest inside the container |

Each stage only runs if the previous one passed — so a lint failure stops everything early without wasting time building Docker.

```
Push / PR to main
       │
       ▼
┌──────────────────┐
│  Build & Lint    │  ← pip install + flake8
└────────┬─────────┘
         │ pass
         ▼
┌──────────────────┐
│  Pytest Suite    │  ← 30 tests + coverage report
└────────┬─────────┘
         │ pass
         ▼
┌──────────────────┐
│  Docker Build    │  ← build image + health check + pytest in container
└──────────────────┘
```

---

## Jenkins Setup

Jenkins handles the **BUILD** phase as a secondary quality gate — independent of GitHub Actions. I configured a declarative pipeline using the `Jenkinsfile` at the root of the repo.

### Steps I followed to set it up

1. **Installed Jenkins** on a local machine using the [official guide](https://www.jenkins.io/doc/book/installing/)
2. **Installed plugins**: Git, Pipeline, Docker Pipeline, JUnit
3. **Created a new Pipeline job**:
   - Set source to: *Pipeline script from SCM*
   - SCM: Git → pointed to this GitHub repo URL
   - Script Path: `Jenkinsfile`
4. **Added a GitHub Webhook** so Jenkins triggers on every push:
   - GitHub → Repo Settings → Webhooks → Add webhook
   - Payload URL: `http://<my-jenkins-server>/github-webhook/`
   - Content type: `application/json`
   - Trigger: *Just the push event*

### What the Jenkins pipeline does

```
Checkout → Setup Python venv → Lint → Unit Tests → Docker Build → Docker Health Check → Cleanup
```

The JUnit plugin reads `test-results.xml` after every build and shows a pass/fail trend over time in the Jenkins dashboard — useful for catching regressions.

---

## API Reference

These are all the endpoints I implemented in `app.py`:

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/health` | Confirms the service is running |
| GET | `/clients` | Returns all gym clients |
| POST | `/clients` | Registers a new client |
| GET | `/clients/<name>` | Fetches a specific client's details |
| PUT | `/clients/<name>` | Updates a client's info |
| DELETE | `/clients/<name>` | Removes a client |
| GET | `/workouts/<client_name>` | Gets all workouts logged for a client |
| POST | `/workouts` | Logs a new workout session |
| GET | `/progress/<client_name>` | Gets weekly adherence records |
| POST | `/progress` | Logs a weekly adherence entry |
| GET | `/membership/<client_name>` | Checks membership status |
| POST | `/generate-program` | Suggests a fitness program based on goal |

### Quick examples

```bash
# Add a new client
curl -X POST http://localhost:5000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "Ravi Kumar", "age": 27, "weight": 72.0, "program": "Muscle Gain"}'

# Log a workout
curl -X POST http://localhost:5000/workouts \
  -H "Content-Type: application/json" \
  -d '{"client_name": "Ravi Kumar", "workout_type": "Strength", "duration_min": 60}'

# Generate a program recommendation
curl -X POST http://localhost:5000/generate-program \
  -H "Content-Type: application/json" \
  -d '{"goal": "Fat Loss"}'
```

---

## My Git Branching Approach

I kept `master` as the stable branch with the original code and created `devops-assignment-1` for all my assignment work. This mirrors how feature branches work in real teams — you never commit directly to main.

```
master                  ← original code, untouched
  └── devops-assignment-2  ← all my assignment work (this branch)
           └── test_devops-assignment-2  ← feature branch
```

Within my work I made commits that map to logical steps:
- Initial Flask API structure
- Added unit tests
- Dockerfile and containerisation
- GitHub Actions workflow
- Jenkins pipeline configuration

---

*Infant Selva | 2024TM93572 | BITS Pilani WILP*
