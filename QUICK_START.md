# QUICK START — Assignment 2 Setup

This is your **exact command sequence** to complete Assignment 2 on Windows.

**Author:** Infant Selva | **BITS ID:** 2024TM93572

---

## Prerequisites (already installed on your machine)
- ✅ Docker Desktop
- ✅ Jenkins (running at `http://localhost:8070`)
- ✅ Minikube
- ✅ Git

---

## Total time: ~25 minutes

---

## PHASE 1 — Automated Setup (1 command, ~5 min)

Open **PowerShell** (not CMD) in your repo folder as **Administrator**, then run:

```powershell
cd C:\path\to\your\aceest-devops-assignment
git pull origin test_devops-assignment-2
.\setup-assignment2.ps1
```

This script will:
- Pull latest code from GitHub
- Start SonarQube via Docker (port 9000)
- Download and install SonarQube Scanner
- Add scanner to Windows PATH
- Open `NEXT_STEPS.txt` with your remaining manual actions

**If you get "running scripts is disabled" error, run this first:**
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

---

## PHASE 2 — Three Manual Clicks (5 min)

### 2A. Add Docker Hub credentials to Jenkins

Open: `http://localhost:8070/manage/credentials/store/system/domain/_/`  
Click **+ Add Credentials** (top right) and fill:

| Field | Value |
|---|---|
| Kind | `Username with password` |
| Username | `selva015` |
| Password | `<YOUR_DOCKER_HUB_TOKEN>` |
| **ID** | `dockerhub-credentials` |

### 2B. Generate SonarQube token + add to Jenkins

1. Open: `http://localhost:9000` → login `admin / admin` → change password
2. Top-right profile → **My Account → Security tab**
3. **Generate Tokens:**
   - Name: `jenkins-token`
   - Type: `User Token`
   - Click **Generate** → **COPY THE TOKEN** (starts with `squ_`)
4. Open: `http://localhost:8070/manage/credentials/store/system/domain/_/`
5. Click **+ Add Credentials** and fill:

| Field | Value |
|---|---|
| Kind | `Secret text` |
| Secret | *(paste the sonar token)* |
| **ID** | `sonar-token` |

### 2C. Restart Jenkins

Open CMD as **Administrator**:
```cmd
net stop Jenkins
net start Jenkins
```

---

## PHASE 3 — Run the Pipeline (~10 min)

1. Open Jenkins: `http://localhost:8070/job/aceest-fitness-pipeline/`
2. Click **Build Now**
3. Watch all 9 stages run green:

```
1. Checkout          → Pull code from GitHub
2. Setup Python      → Create venv, install dependencies
3. Lint              → flake8 syntax check
4. Unit Tests        → pytest (30 tests)
5. SonarQube Analysis → Code quality scan
6. Docker Build      → Build image
7. Push to Docker Hub → Upload to selva015/aceest-fitness
8. Deploy            → Run container locally
9. Smoke Test        → Verify /health endpoint
```

---

## PHASE 4 — Deploy to Kubernetes (~5 min)

In the repo folder, run ONE command:

```cmd
deploy-k8s.bat rolling
```

That's it — the script does everything. Copy the URL it prints at the end.

**Want to try all 5 strategies?** Run each separately:
```cmd
deploy-k8s.bat rolling       # Rolling Update
deploy-k8s.bat blue-green    # Blue-Green
deploy-k8s.bat canary        # Canary (25/75)
deploy-k8s.bat shadow        # Shadow traffic
deploy-k8s.bat ab            # A/B Testing via header

deploy-k8s.bat status        # See all pods/services
deploy-k8s.bat clean         # Delete everything
```

---

## PHASE 5 — Take 5 Screenshots

For the assignment report, screenshot these while everything is still running:

| # | What to capture |
|---|---|
| 1 | Jenkins pipeline — all 9 stages green |
| 2 | `hub.docker.com/r/selva015/aceest-fitness` — showing image tags |
| 3 | SonarQube dashboard — Quality Gate PASSED |
| 4 | CMD: `kubectl get pods` — all pods STATUS=Running |
| 5 | CMD: `curl <minikube URL>/health` — `{status: healthy}` |

---

## PHASE 6 — Submit

Submit these on the BITS portal:

| What | Value |
|---|---|
| GitHub Repo | `https://github.com/Infantselva-pilani/aceest-devops-assignment` |
| Docker Hub | `https://hub.docker.com/r/selva015/aceest-fitness` |
| Dev Branch | `test_devops-assignment-2` |
| Report Doc | `DevOps_Assignment2_FINAL_InfantSelva_2024TM93572.docx` (with screenshots added) |

---

## Troubleshooting

### "PowerShell script won't run"
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### "sonar-scanner not found" in Jenkins
- Restart Jenkins: `net stop Jenkins && net start Jenkins`
- Or manually add in Jenkins: Manage Jenkins → System → Global properties → Environment variables → add `PATH` = `C:\sonar-scanner\bin;%PATH%`

### "docker push failed"
- Double-check credential ID in Jenkins is exactly `dockerhub-credentials`
- Token starts with `dckr_pat_` — confirm you copied it correctly

### "Minikube image pull error"
- Point Minikube to Docker Hub: your image is public, so this shouldn't happen
- If it does: `minikube image pull selva015/aceest-fitness:latest`

### Jenkins SonarQube stage fails
- Verify `http://localhost:9000` opens in browser
- Verify `sonar-token` credential exists in Jenkins
- Run `sonar-scanner --version` in CMD to verify installation

---

*Infant Selva | 2024TM93572 | BITS Pilani WILP*
