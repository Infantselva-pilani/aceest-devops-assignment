# Kubernetes Deployment Strategies — ACEest Fitness & Gym

This folder contains YAML manifests for 5 deployment strategies using Minikube.

## Prerequisites

```bash
# Start Minikube
minikube start

# Verify it's running
minikube status
kubectl get nodes
```

---

## Strategy 1 — Rolling Update (default)

Replaces pods gradually. Zero downtime. Kubernetes does this automatically.

```bash
kubectl apply -f deployment-rolling.yaml
kubectl rollout status deployment/aceest-fitness-rolling

# Access the app
minikube service aceest-fitness-service --url

# Update to new image (triggers rolling update automatically)
kubectl set image deployment/aceest-fitness-rolling aceest-fitness=selva015/aceest-fitness:2

# Rollback if needed
kubectl rollout undo deployment/aceest-fitness-rolling
```

---

## Strategy 2 — Blue-Green

Two full environments. Switch traffic instantly by changing service selector.

```bash
kubectl apply -f deployment-blue-green.yaml

# Traffic goes to BLUE by default
minikube service aceest-fitness-bg-service --url

# Switch to GREEN (after verifying green is healthy)
kubectl patch service aceest-fitness-bg-service \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Rollback to BLUE instantly
kubectl patch service aceest-fitness-bg-service \
  -p '{"spec":{"selector":{"version":"blue"}}}'
```

---

## Strategy 3 — Canary

25% traffic goes to new version. Monitor it. Promote or rollback.

```bash
kubectl apply -f deployment-canary.yaml

# Access app (Kubernetes load-balances ~25% to canary automatically)
minikube service aceest-fitness-canary-service --url

# Monitor canary behaviour
kubectl logs -l version=canary -f

# Promote canary (scale stable down, canary up)
kubectl scale deployment aceest-fitness-canary --replicas=3
kubectl scale deployment aceest-fitness-stable --replicas=0

# Rollback canary
kubectl scale deployment aceest-fitness-canary --replicas=0
```

---

## Strategy 4 — Shadow

Real traffic goes to production. Identical traffic is ALSO sent to shadow silently.
Shadow responses are discarded. Used to test new version with real data.

```bash
kubectl apply -f deployment-shadow.yaml

# Production traffic (real users)
minikube service aceest-fitness-prod-service --url

# Check shadow logs (no user impact)
kubectl logs -l version=shadow -f

# Compare metrics
kubectl top pods
```

---

## Strategy 5 — A/B Testing

Different versions served to different user groups via HTTP header.

```bash
# Enable ingress first
minikube addons enable ingress

kubectl apply -f deployment-ab-testing.yaml

# Get the Minikube IP
minikube ip

# Test version A (default — no special header)
curl http://$(minikube ip)/health

# Test version B (send header to route to version B)
curl -H "X-Version: B" http://$(minikube ip)/health

# Check which version handled requests
kubectl logs -l version=a --tail=10
kubectl logs -l version=b --tail=10
```

---

## Useful Commands

```bash
# View all deployments
kubectl get deployments

# View all pods
kubectl get pods

# View all services
kubectl get services

# Delete everything (cleanup)
kubectl delete -f deployment-rolling.yaml
kubectl delete -f deployment-blue-green.yaml
kubectl delete -f deployment-canary.yaml
kubectl delete -f deployment-shadow.yaml
kubectl delete -f deployment-ab-testing.yaml

# Stop Minikube
minikube stop
```
