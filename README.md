# ACEest Fitness & Gym — CI/CD Pipeline

> **DevOps Assignment 1** | BITS Pilani | Course: Introduction to DevOps (CSIZG514/SEZG514)

A Flask-based REST API for the ACEest Fitness & Gym management system, demonstrating a complete CI/CD pipeline using **Git**, **Docker**, **GitHub Actions**, and **Jenkins**.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Local Setup & Execution](#local-setup--execution)
3. [Running Tests Manually](#running-tests-manually)
4. [Docker Usage](#docker-usage)
5. [GitHub Actions Pipeline](#github-actions-pipeline)
6. [Jenkins Integration](#jenkins-integration)
7. [API Endpoints](#api-endpoints)

---

## Project Structure

```
aceest-fitness/
├── app.py                        # Flask application (REST API)
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Multi-stage Docker build
├── Jenkinsfile                   # Jenkins declarative pipeline
├── .github/
│   └── workflows/
│       └── main.yml              # GitHub Actions CI/CD pipeline
├── tests/
│   └── test_app.py               # Pytest test suite
└── README.md
```

---

## Local Setup & Execution

### Prerequisites
- Python 3.11+
- pip
- Docker (for containerized execution)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/aceest-fitness.git
cd aceest-fitness

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

The API will be available at `http://localhost:5000`.

---

## Running Tests Manually

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing

# Run a specific test class
pytest tests/test_app.py::TestClients -v
```

---

## Docker Usage

```bash
# Build the Docker image
docker build -t aceest-fitness:latest .

# Run the container
docker run -d -p 5000:5000 --name aceest aceest-fitness:latest

# Check health
curl http://localhost:5000/health

# Run tests inside the container
docker run --rm -v $(pwd)/tests:/app/tests aceest-fitness:latest python -m pytest tests/ -v

# Stop and remove the container
docker stop aceest && docker rm aceest
```

---

## GitHub Actions Pipeline

The pipeline is defined in `.github/workflows/main.yml` and is triggered on every **push** to `main`/`develop` and every **pull request** to `main`.

### Pipeline Stages

| Stage | Description |
|---|---|
| **Build & Lint** | Installs dependencies and runs `flake8` to catch syntax errors |
| **Run Pytest Suite** | Executes all unit tests and generates a coverage report |
| **Docker Image Assembly** | Builds the Docker image and validates it with a health-check |

### Workflow Diagram

```
Push / PR
    │
    ▼
┌─────────────────┐
│  Build & Lint   │  ← flake8 syntax check
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Pytest Suite   │  ← unit tests + coverage
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Docker Build   │  ← docker build + health check
└─────────────────┘
```

---

## Jenkins Integration

Jenkins handles the primary **BUILD** phase, serving as a secondary quality gate.

### Setup Steps

1. **Install Jenkins** — follow the [official guide](https://www.jenkins.io/doc/book/installing/)
2. **Install plugins**: Git, Pipeline, Docker Pipeline, JUnit
3. **Create a new Pipeline job**:
   - Source: *Pipeline script from SCM*
   - SCM: *Git* → enter your GitHub repository URL
   - Script Path: `Jenkinsfile`
4. **Configure GitHub Webhook** to trigger builds on push:
   - Go to GitHub → Repo Settings → Webhooks
   - Payload URL: `http://<jenkins-server>/github-webhook/`
   - Content type: `application/json`
   - Events: *Just the push event*

### Jenkins Pipeline Stages

```
Checkout → Setup Python → Lint → Unit Tests → Docker Build → Docker Test → Cleanup
```

The **JUnit** plugin automatically parses `test-results.xml` and displays test pass/fail history over time in the Jenkins UI.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/clients` | List all clients |
| POST | `/clients` | Add a new client |
| GET | `/clients/<name>` | Get a specific client |
| PUT | `/clients/<name>` | Update client details |
| DELETE | `/clients/<name>` | Delete a client |
| GET | `/workouts/<client_name>` | Get workouts for a client |
| POST | `/workouts` | Log a new workout |
| GET | `/progress/<client_name>` | Get progress records |
| POST | `/progress` | Log a progress entry |
| GET | `/membership/<client_name>` | Check membership status |
| POST | `/generate-program` | Generate a fitness program |

### Example: Add a Client

```bash
curl -X POST http://localhost:5000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice Johnson", "age": 28, "weight": 65.0, "goal": "Fat Loss"}'
```

### Example: Generate a Program

```bash
curl -X POST http://localhost:5000/generate-program \
  -H "Content-Type: application/json" \
  -d '{"goal": "Muscle Gain"}'
```

---

## Git Branching Strategy

```
main        ← production-ready code, protected branch
  └── develop ← integration branch
        ├── feature/flask-api
        ├── feature/docker-setup
        └── feature/ci-cd-pipeline
```

---

*Built for BITS Pilani DevOps Assignment 1 | Prof. A R Rahman*
*Student Roll No: 2024TM93572*
