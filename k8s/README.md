# Kubernetes Deployment Strategies — ACEest Fitness & Gym

**Author:** Infant Selva | 2024TM93572

This folder contains YAML manifests for 5 deployment strategies using Minikube.

---

## Prerequisites

```cmd
minikube start
minikube status
```

---

## Strategy 1 — Rolling Update

Replaces pods gradually. Zero downtime. Kubernetes does this automatically.

```cmd
kubectl apply -f k8s/deployment-rolling.yaml
kubectl rollout status deployment/aceest-fitness-rolling
```

### Accessing the app (3 ways — use whichever works)

**Method A — Port forward (MOST RELIABLE on Windows):**
```cmd
kubectl port-forward service/aceest-fitness-service 8080:80
```
Keep this window open. In a new CMD:
```cmd
curl http://localhost:8080/health
```

**Method B — Minikube service URL:**
```cmd
minikube service aceest-fitness-service
```
Keep this window open. It will tunnel and auto-open browser.

**Method C — Inside the pod (always works):**
```cmd
kubectl get pods
kubectl exec -it <pod-name> -- curl http://localhost:5000/health
```

---

## Strategy 2 — Blue-Green

```cmd
kubectl apply -f k8s/deployment-blue-green.yaml
kubectl port-forward service/aceest-fitness-bg-service 8081:80
# In another CMD:
curl http://localhost:8081/health

# Switch to GREEN version
kubectl patch service aceest-fitness-bg-service -p "{\"spec\":{\"selector\":{\"version\":\"green\"}}}"

# Rollback to BLUE
kubectl patch service aceest-fitness-bg-service -p "{\"spec\":{\"selector\":{\"version\":\"blue\"}}}"
```

---

## Strategy 3 — Canary

```cmd
kubectl apply -f k8s/deployment-canary.yaml
kubectl port-forward service/aceest-fitness-canary-service 8082:80
# Traffic auto-distributed: 75% stable, 25% canary

# Promote canary
kubectl scale deployment aceest-fitness-canary --replicas=3
kubectl scale deployment aceest-fitness-stable --replicas=0
```

---

## Strategy 4 — Shadow

```cmd
kubectl apply -f k8s/deployment-shadow.yaml
kubectl port-forward service/aceest-fitness-prod-service 8083:80
# Check shadow logs:
kubectl logs -l version=shadow -f
```

---

## Strategy 5 — A/B Testing

```cmd
minikube addons enable ingress
kubectl apply -f k8s/deployment-ab-testing.yaml

# Default goes to Version A
curl http://%MINIKUBE_IP%/health

# Header sends to Version B
curl -H "X-Version: B" http://%MINIKUBE_IP%/health
```

---

## Useful commands

```cmd
kubectl get deployments
kubectl get pods
kubectl get services

# Delete everything
kubectl delete -f k8s/deployment-rolling.yaml
kubectl delete -f k8s/deployment-blue-green.yaml
kubectl delete -f k8s/deployment-canary.yaml
kubectl delete -f k8s/deployment-shadow.yaml
kubectl delete -f k8s/deployment-ab-testing.yaml

minikube stop
```
