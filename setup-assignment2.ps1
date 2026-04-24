# =============================================================================
# ACEest Fitness — Assignment 2 ONE-SHOT SETUP SCRIPT
# =============================================================================
# This script sets up everything on your Windows machine:
# 1. Pulls latest code from GitHub
# 2. Starts SonarQube via Docker
# 3. Installs SonarQube Scanner
# 4. Creates a credentials reminder file
#
# USAGE: Right-click this file → "Run with PowerShell"
# OR run in PowerShell: .\setup-assignment2.ps1
#
# Author: Infant Selva | 2024TM93572
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " ACEest Fitness Assignment 2 - Automated Setup" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# -----------------------------------------------------------------------------
# STEP 1: Pull latest code from GitHub
# -----------------------------------------------------------------------------
Write-Host "[1/4] Pulling latest code from GitHub..." -ForegroundColor Yellow
try {
    git pull origin test_devops-assignment-2
    Write-Host "   DONE: Code updated" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: Could not pull from GitHub. Make sure you are in the repo folder." -ForegroundColor Red
    exit 1
}

# -----------------------------------------------------------------------------
# STEP 2: Start SonarQube via Docker
# -----------------------------------------------------------------------------
Write-Host ""
Write-Host "[2/4] Starting SonarQube via Docker..." -ForegroundColor Yellow
$existing = docker ps -a --filter "name=sonarqube" --format "{{.Names}}" 2>$null
if ($existing -eq "sonarqube") {
    Write-Host "   SonarQube container already exists. Starting it..." -ForegroundColor Yellow
    docker start sonarqube | Out-Null
} else {
    docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community | Out-Null
}

Write-Host "   Waiting 90 seconds for SonarQube to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 90
Write-Host "   DONE: SonarQube running at http://localhost:9000" -ForegroundColor Green

# -----------------------------------------------------------------------------
# STEP 3: Install SonarQube Scanner
# -----------------------------------------------------------------------------
Write-Host ""
Write-Host "[3/4] Installing SonarQube Scanner..." -ForegroundColor Yellow
$scannerPath = "C:\sonar-scanner"
$scannerZip  = "$env:TEMP\sonar-scanner-cli.zip"
$scannerUrl  = "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-6.2.1.4610-windows-x64.zip"

if (Test-Path $scannerPath) {
    Write-Host "   SonarQube Scanner already installed at $scannerPath" -ForegroundColor Green
} else {
    Write-Host "   Downloading SonarQube Scanner (~50 MB)..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $scannerUrl -OutFile $scannerZip
    Write-Host "   Extracting..." -ForegroundColor Yellow
    Expand-Archive -Path $scannerZip -DestinationPath "C:\" -Force
    $extractedFolder = Get-ChildItem -Path "C:\" -Directory -Filter "sonar-scanner-*" | Select-Object -First 1
    if ($extractedFolder) {
        Rename-Item -Path $extractedFolder.FullName -NewName "sonar-scanner" -Force
    }
    Remove-Item $scannerZip -Force

    # Add to system PATH
    $currentPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$scannerPath\bin*") {
        [System.Environment]::SetEnvironmentVariable("Path", "$currentPath;$scannerPath\bin", "Machine")
        Write-Host "   DONE: Added C:\sonar-scanner\bin to system PATH" -ForegroundColor Green
        Write-Host "   NOTE: You must restart Jenkins service for PATH change to take effect" -ForegroundColor Yellow
    }
}

# -----------------------------------------------------------------------------
# STEP 4: Create credentials reminder
# -----------------------------------------------------------------------------
Write-Host ""
Write-Host "[4/4] Creating credentials reminder file..." -ForegroundColor Yellow

$reminderFile = "$PWD\NEXT_STEPS.txt"
@"
====================================================================
 ACEest Fitness Assignment 2 - Your NEXT 3 manual steps
====================================================================

STEP A: ADD DOCKER HUB CREDENTIALS TO JENKINS
   Open: http://localhost:8070/manage/credentials/store/system/domain/_/
   Click: + Add Credentials (top right)
   Fill:
     Kind:        Username with password
     Username:    selva015
     Password:    <YOUR_DOCKER_HUB_TOKEN>
     ID:          dockerhub-credentials
   Click: Create

STEP B: SETUP SONARQUBE + ADD TOKEN TO JENKINS
   Open: http://localhost:9000
   Login: admin / admin (you'll be forced to change password on first login)
   New password: set anything you'll remember

   After login:
     Top right (your profile icon) -> My Account -> Security tab
     Generate Tokens section:
       Name: jenkins-token
       Type: User Token (default)
     Click: Generate
     COPY THE TOKEN (starts with squ_...) - you'll see it only once

   Open Jenkins:
     http://localhost:8070/manage/credentials/store/system/domain/_/
     Click: + Add Credentials
     Fill:
       Kind:        Secret text
       Secret:      (paste the sonar token)
       ID:          sonar-token
     Click: Create

STEP C: RESTART JENKINS (so PATH change is picked up)
   Open CMD as Administrator and run:
     net stop Jenkins
     net start Jenkins

STEP D: RUN THE PIPELINE
   Open: http://localhost:8070/job/aceest-fitness-pipeline/
   Click: Build Now
   Watch all 9 stages go green.

STEP E: DEPLOY TO KUBERNETES
   In this folder, run:
     minikube start
     kubectl apply -f k8s/deployment-rolling.yaml
     minikube service aceest-fitness-service --url

====================================================================
When done, take these 5 screenshots:
  1. Jenkins pipeline - all 9 stages green
  2. Docker Hub - hub.docker.com/r/selva015/aceest-fitness - image tags
  3. SonarQube dashboard - Quality Gate PASSED
  4. kubectl get pods - all pods Running
  5. curl on minikube URL - health response
====================================================================
"@ | Set-Content $reminderFile

Write-Host "   DONE: Reminder saved to NEXT_STEPS.txt" -ForegroundColor Green

# -----------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " AUTOMATED SETUP COMPLETE" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "What was automated:"
Write-Host "  [OK] Pulled latest code"
Write-Host "  [OK] SonarQube running at http://localhost:9000"
Write-Host "  [OK] SonarQube Scanner installed at C:\sonar-scanner"
Write-Host "  [OK] Added scanner to Windows PATH"
Write-Host ""
Write-Host "What you still need to do manually (5 min):"
Write-Host "  Open NEXT_STEPS.txt - follow Steps A, B, C, D, E"
Write-Host ""
Write-Host "File saved to: $reminderFile"
Write-Host ""
Invoke-Item $reminderFile
