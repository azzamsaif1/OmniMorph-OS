# UCSK Deployment Guide

## Overview

This guide covers deploying UCSK in three environments:
1. **Local Development** — Docker Compose
2. **Staging** — Kubernetes (single cluster)
3. **Production** — Kubernetes (multi-replica, autoscaling)

---

## Prerequisites

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| Docker | 24+ | Container runtime |
| Docker Compose | 2.20+ | Local orchestration |
| kubectl | 1.28+ | Kubernetes management |
| Node.js | 22+ | Frontend build |
| Python | 3.12+ | Backend runtime |

---

## 1. Local Development (Docker Compose)

### Quick Start

```bash
cd infrastructure/
cp ../.env.example ../.env
# Edit .env with your API keys

docker compose up --build
```

### Services

| Service | Port | Purpose |
|---------|------|---------|
| backend | 8000 | FastAPI REST + WebSocket |
| frontend | 5173 | Vite dev server |
| qdrant | 6333 | Vector DB (behavioral fingerprints) |
| neo4j | 7474/7687 | Graph DB (skill relationships) |
| postgres | 5432 | Event store (temporal data) |
| redis | 6379 | Agent coordination + caching |

### Verify

```bash
curl http://localhost:8000/health
# {"status":"ok","service":"UCSK"}

curl http://localhost:5173
# HTML response (frontend)
```

---

## 2. Kubernetes Deployment

### Secrets Setup

Create the secrets before deploying:

```bash
kubectl create secret generic ucsk-secrets \
  --from-literal=postgres-dsn='postgresql+asyncpg://ucsk:PASSWORD@postgres:5432/ucsk' \
  --from-literal=gemini-api-key='YOUR_GEMINI_API_KEY'
```

### Persistent Volumes

Create PVCs for stateful services:

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qdrant-pvc
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: neo4j-pvc
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 10Gi
EOF
```

### Deploy

```bash
kubectl apply -f infrastructure/k8s/deployment.yaml
kubectl apply -f infrastructure/k8s/service.yaml
```

### Verify

```bash
kubectl get pods -l app=ucsk
kubectl get svc -l app=ucsk

# Check backend health
kubectl port-forward svc/ucsk-backend-service 8000:8000
curl http://localhost:8000/health
```

---

## 3. Production Considerations

### Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ucsk-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ucsk-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `UCSK_GEMINI_API_KEY` | Yes (for AI features) | — | Google Gemini API key |
| `UCSK_QDRANT_HOST` | No | localhost | Qdrant server hostname |
| `UCSK_QDRANT_PORT` | No | 6333 | Qdrant server port |
| `UCSK_NEO4J_URI` | No | bolt://localhost:7687 | Neo4j connection URI |
| `UCSK_NEO4J_USER` | No | neo4j | Neo4j username |
| `UCSK_NEO4J_PASSWORD` | No | ucsk_secret | Neo4j password |
| `UCSK_POSTGRES_DSN` | No | postgresql+asyncpg://ucsk:ucsk@localhost:5432/ucsk | PostgreSQL DSN |
| `UCSK_REDIS_URL` | No | redis://localhost:6379/0 | Redis connection URL |
| `UCSK_CORS_ORIGINS` | No | ["http://localhost:3000","http://localhost:5173"] | Allowed CORS origins |
| `UCSK_DEBUG` | No | false | Enable debug mode |

### Security Checklist

- [ ] All secrets stored in Kubernetes Secrets (not ConfigMaps)
- [ ] Network policies restrict inter-pod communication
- [ ] TLS termination at Ingress layer
- [ ] WebSocket connections use `wss://` in production
- [ ] Database credentials rotated quarterly
- [ ] Audit log exported to immutable storage
- [ ] CORS origins restricted to production domains
- [ ] Rate limiting applied at Ingress

### Monitoring

Recommended stack:
- **Metrics**: Prometheus + Grafana (scrape `/health` + custom `/metrics` endpoint)
- **Logs**: Fluentd → Elasticsearch → Kibana
- **Traces**: OpenTelemetry → Jaeger
- **Alerts**: PagerDuty integration for backend health failures

---

## Architecture Diagram

```
Internet
    │
    ▼
┌─────────┐
│ Ingress │  (TLS termination, routing)
└─────────┘
    │
    ├── /api, /ws → ucsk-backend-service (port 8000)
    │                    │
    │                    ├── Qdrant (port 6333)
    │                    ├── Neo4j (port 7687)
    │                    ├── PostgreSQL (port 5432)
    │                    └── Redis (port 6379)
    │
    └── / → ucsk-frontend-service (port 80)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check `UCSK_POSTGRES_DSN` is reachable |
| WebSocket disconnects | Verify Ingress WebSocket annotation |
| Qdrant OOM | Increase memory limits in deployment |
| Frontend blank page | Ensure `VITE_API_URL` points to backend |
| Slow mental state inference | Check MediaPipe GPU acceleration |
