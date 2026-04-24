@echo off
REM ============================================================================
REM ACEest Fitness - Kubernetes Deploy Helper (Windows)
REM
REM Usage:
REM   deploy-k8s.bat rolling     # Rolling Update strategy
REM   deploy-k8s.bat blue-green  # Blue-Green strategy
REM   deploy-k8s.bat canary      # Canary strategy
REM   deploy-k8s.bat shadow      # Shadow strategy
REM   deploy-k8s.bat ab          # A/B Testing strategy
REM   deploy-k8s.bat clean       # Delete all deployments
REM   deploy-k8s.bat status      # Show all pods and services
REM
REM Author: Infant Selva | 2024TM93572
REM ============================================================================

SETLOCAL

IF "%1"=="" (
    ECHO.
    ECHO Usage: deploy-k8s.bat [strategy]
    ECHO.
    ECHO Strategies:  rolling ^| blue-green ^| canary ^| shadow ^| ab
    ECHO Other:       clean ^| status
    ECHO.
    EXIT /B 1
)

REM Ensure Minikube is running
minikube status >nul 2>&1
IF ERRORLEVEL 1 (
    ECHO Starting Minikube...
    minikube start
)

IF /I "%1"=="rolling" (
    ECHO.
    ECHO ========================================
    ECHO Deploying: ROLLING UPDATE
    ECHO ========================================
    kubectl apply -f k8s/deployment-rolling.yaml
    kubectl rollout status deployment/aceest-fitness-rolling
    ECHO.
    ECHO Access the app at:
    minikube service aceest-fitness-service --url
    GOTO :END
)

IF /I "%1"=="blue-green" (
    ECHO.
    ECHO ========================================
    ECHO Deploying: BLUE-GREEN
    ECHO ========================================
    kubectl apply -f k8s/deployment-blue-green.yaml
    kubectl rollout status deployment/aceest-fitness-blue
    kubectl rollout status deployment/aceest-fitness-green
    ECHO.
    ECHO Currently routing to BLUE. Access at:
    minikube service aceest-fitness-bg-service --url
    GOTO :END
)

IF /I "%1"=="canary" (
    ECHO.
    ECHO ========================================
    ECHO Deploying: CANARY (75% stable, 25% canary)
    ECHO ========================================
    kubectl apply -f k8s/deployment-canary.yaml
    kubectl rollout status deployment/aceest-fitness-stable
    kubectl rollout status deployment/aceest-fitness-canary
    ECHO.
    ECHO Access (25%% of traffic to canary) at:
    minikube service aceest-fitness-canary-service --url
    GOTO :END
)

IF /I "%1"=="shadow" (
    ECHO.
    ECHO ========================================
    ECHO Deploying: SHADOW
    ECHO ========================================
    kubectl apply -f k8s/deployment-shadow.yaml
    kubectl rollout status deployment/aceest-fitness-production
    kubectl rollout status deployment/aceest-fitness-shadow
    ECHO.
    ECHO Production traffic at:
    minikube service aceest-fitness-prod-service --url
    ECHO Shadow receives mirror traffic silently.
    GOTO :END
)

IF /I "%1"=="ab" (
    ECHO.
    ECHO ========================================
    ECHO Deploying: A/B TESTING
    ECHO ========================================
    ECHO Enabling ingress addon...
    minikube addons enable ingress
    kubectl apply -f k8s/deployment-ab-testing.yaml
    kubectl rollout status deployment/aceest-fitness-version-a
    kubectl rollout status deployment/aceest-fitness-version-b
    ECHO.
    FOR /F "tokens=*" %%i IN ('minikube ip') DO SET MINIKUBE_IP=%%i
    ECHO Access Version A:  curl http://%MINIKUBE_IP%/health
    ECHO Access Version B:  curl -H "X-Version: B" http://%MINIKUBE_IP%/health
    GOTO :END
)

IF /I "%1"=="clean" (
    ECHO.
    ECHO Cleaning up all deployments...
    kubectl delete -f k8s/deployment-rolling.yaml --ignore-not-found
    kubectl delete -f k8s/deployment-blue-green.yaml --ignore-not-found
    kubectl delete -f k8s/deployment-canary.yaml --ignore-not-found
    kubectl delete -f k8s/deployment-shadow.yaml --ignore-not-found
    kubectl delete -f k8s/deployment-ab-testing.yaml --ignore-not-found
    ECHO DONE
    GOTO :END
)

IF /I "%1"=="status" (
    ECHO.
    ECHO === Deployments ===
    kubectl get deployments
    ECHO.
    ECHO === Pods ===
    kubectl get pods
    ECHO.
    ECHO === Services ===
    kubectl get services
    GOTO :END
)

ECHO Unknown strategy: %1
ECHO Use: rolling ^| blue-green ^| canary ^| shadow ^| ab ^| clean ^| status

:END
ENDLOCAL
