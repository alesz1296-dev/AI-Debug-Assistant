# Local Kubernetes Kind Runbook

This runbook introduces the local Kubernetes path for the Enterprise AI Debug Assistant. The goal is to move from the validated Docker Compose platform to Kubernetes in small, observable steps before AWS EKS work begins.

## Prerequisites

Before using Kubernetes, the container platform must already be working.

Required local tools:

- Docker Desktop
- `kind`
- `kubectl`
- project Docker image build

On this Windows workstation, `kind` can be installed as a workspace-local executable:

```powershell
C:\Users\alesz\Projects_Apps\tools\kind.exe version
```

To use `kind` as a command in the current PowerShell session, prepend the tools folder to `PATH`:

```powershell
$env:PATH = "C:\Users\alesz\Projects_Apps\tools;$env:PATH"
kind version
```

Required project capabilities:

- API container starts successfully.
- PostgreSQL and Redis dependencies are understood from Docker Compose.
- Alembic migrations run successfully.
- API, worker, metrics, logs, and evaluation paths are already validated in Compose.

## Core Kubernetes Concepts

### Pod

A Pod is the smallest runnable unit in Kubernetes. It wraps one or more containers that share networking and lifecycle.

In this project, an API Pod runs the FastAPI container.

### Deployment

A Deployment manages long-running Pods. It keeps the desired number of replicas running, replaces failed Pods, and supports rolling updates.

This project will use separate Deployments for:

- API
- ingestion worker

### Service

A Service gives Pods a stable network name. Pods are temporary, but Services provide stable discovery.

Examples:

- `ai-debug-api` routes traffic to API Pods.
- `postgres` gives the API and worker a stable database hostname.
- `redis` gives the API and worker a stable queue hostname.

### Job

A Job runs a task to completion.

Alembic migrations should run as a Job, because migrations are not a long-running service.

### ConfigMap

A ConfigMap stores non-sensitive configuration.

Examples:

- `APP_ENV`
- `LOG_LEVEL`
- provider mode flags

### Secret

A Secret stores sensitive configuration.

Examples:

- `API_KEY`
- `DATABASE_URL`
- `REDIS_URL`

For local Kubernetes, safe dummy values are acceptable. For AWS, secrets must come from AWS-managed secret storage.

## Target Local Architecture

```text
Developer
  -> kubectl port-forward
  -> Service: ai-debug-api
  -> API Deployment
  -> Postgres Service
  -> Postgres Pod

API Deployment
  -> Redis Service
  -> Redis Pod

Worker Deployment
  -> Redis Service
  -> Redis Pod
  -> Postgres Service
  -> Postgres Pod

Migration Job
  -> Postgres Service
  -> Postgres Pod
```

The API, worker, and migration Job should use the same image but different commands.

## Why Kind First

`kind` means Kubernetes in Docker. It creates a local Kubernetes cluster using Docker containers as Kubernetes nodes.

This is a good first runtime because:

- it exposes standard Kubernetes behavior
- it works well for local labs and CI validation
- it keeps the cluster minimal
- it maps cleanly to later EKS concepts

## Implementation Stages

### Stage 1: Create a Kind Cluster

Create a local cluster:

```powershell
kind create cluster --name ai-debug-local
```

Verify the cluster:

```powershell
kubectl cluster-info
kubectl get nodes
```

Expected result:

- one control-plane node
- node status is `Ready`

### Stage 2: Build and Load the API Image

Build the image:

```powershell
docker build -f infra/Dockerfile.api -t ai-debug-assistant-api:local .
```

Load it into kind:

```powershell
kind load docker-image ai-debug-assistant-api:local --name ai-debug-local
```

Why this is needed:

- kind nodes run inside Docker
- a locally built image is not automatically available inside the kind node
- `kind load docker-image` copies the image into the cluster node

### Stage 3: Add Kubernetes Manifests

Start with raw manifests before Helm so each Kubernetes object is visible.

Initial objects:

- Namespace
- ConfigMap
- Secret
- PostgreSQL Deployment and Service
- Redis Deployment and Service
- API Deployment and Service
- Alembic migration Job
- worker Deployment

At this point in the project, the following raw manifest layer exists under `infra/k8s`:

- `namespace.yaml`
- `configmap.yaml`
- `secret.yaml`
- `postgres-pvc.yaml`
- `postgres-deployment.yaml`
- `postgres-service.yaml`
- `redis-deployment.yaml`
- `redis-service.yaml`
- `api-deployment.yaml`
- `api-service.yaml`
- `worker-deployment.yaml`
- `alembic-migration-job.yaml`

Apply the full local platform in dependency order:

```powershell
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/configmap.yaml
kubectl apply -f infra/k8s/secret.yaml
kubectl apply -f infra/k8s/postgres-pvc.yaml
kubectl apply -f infra/k8s/postgres-deployment.yaml
kubectl apply -f infra/k8s/postgres-service.yaml
kubectl apply -f infra/k8s/redis-deployment.yaml
kubectl apply -f infra/k8s/redis-service.yaml
kubectl apply -f infra/k8s/alembic-migration-job.yaml
kubectl apply -f infra/k8s/api-deployment.yaml
kubectl apply -f infra/k8s/api-service.yaml
kubectl apply -f infra/k8s/worker-deployment.yaml
```

Why this order matters:

- namespace first, because every namespaced object depends on it
- config and secret before app workloads, because the Pods reference them at startup
- Postgres and Redis before migrations and app workloads, because they are runtime dependencies
- migration Job before API validation, because the app should start against the expected schema
- API before worker validation, because you will use the API to enqueue ingestion work

### Stage 4: Validate the API

Port-forward the API Service:

```powershell
kubectl port-forward service/ai-debug-api 8000:8000 -n ai-debug
```

Validate:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/ready
Invoke-RestMethod http://127.0.0.1:8000/api/v1/metrics
```

Expected:

- health is `ok`
- backend is `postgresql`
- readiness reports database and Redis as `ok`

Important probe design:

- the liveness probe should ask, "is the process alive enough to keep running?"
- the readiness probe should ask, "is this Pod ready to receive traffic right now?"

For this project:

- liveness uses `/api/v1/health`
- readiness uses `/api/v1/ready`

That split is intentional. If Redis or Postgres is unavailable, readiness should fail so Kubernetes stops sending traffic, but liveness should not necessarily kill and restart the container immediately.

### Stage 5: Validate Worker Processing

Enqueue a document through the API.

Then inspect:

```powershell
kubectl logs deployment/ai-debug-worker -n ai-debug
```

Expected events:

- `worker.started`
- `ingestion.job.started`
- `ingestion.job.succeeded`

The worker does not need a Service because nothing sends network traffic into it. It is a consumer, not a server. This is an important Kubernetes design habit: only expose a Service for workloads that must be reached over the network.

### Stage 6: Debugging Commands

List everything in the namespace:

```powershell
kubectl get all -n ai-debug
```

Inspect Pods:

```powershell
kubectl get pods -n ai-debug
kubectl describe pod <pod-name> -n ai-debug
```

Read logs:

```powershell
kubectl logs <pod-name> -n ai-debug
kubectl logs deployment/ai-debug-api -n ai-debug
kubectl logs deployment/ai-debug-worker -n ai-debug
```

Open a shell in a Pod:

```powershell
kubectl exec -it <pod-name> -n ai-debug -- /bin/sh
```

Check Services:

```powershell
kubectl get svc -n ai-debug
kubectl describe svc ai-debug-api -n ai-debug
```

Check Jobs:

```powershell
kubectl get jobs -n ai-debug
kubectl logs job/ai-debug-migrations -n ai-debug
```

## Common Failure Drills

### ImagePullBackOff

Cause:

- image name is wrong
- image was not loaded into kind
- image pull policy tries to pull from a registry

Debug:

```powershell
kubectl describe pod <pod-name> -n ai-debug
```

### CrashLoopBackOff

Cause:

- app starts and exits repeatedly
- bad command
- missing env var
- failed dependency connection

Debug:

```powershell
kubectl logs <pod-name> -n ai-debug --previous
kubectl describe pod <pod-name> -n ai-debug
```

### Readiness Fails

Cause:

- API is running but dependency checks fail
- database unavailable
- Redis unavailable

Debug:

```powershell
kubectl logs deployment/ai-debug-api -n ai-debug
kubectl describe pod <api-pod-name> -n ai-debug
```

### Migration Job Fails

Cause:

- database unavailable
- schema error
- missing pgvector extension
- bad `DATABASE_URL`

Debug:

```powershell
kubectl logs job/ai-debug-migrations -n ai-debug
kubectl describe job ai-debug-migrations -n ai-debug
```

If you need to rerun the Job after changing its manifest, delete it first:

```powershell
kubectl delete job ai-debug-migrations -n ai-debug
kubectl apply -f infra/k8s/alembic-migration-job.yaml
```

## Completion Criteria

Local Kubernetes is validated when:

- API Deployment is running.
- Worker Deployment is running.
- Migration Job completes.
- Health endpoint passes.
- Readiness endpoint passes.
- Metrics endpoint responds.
- Query endpoint returns citations.
- Evaluation endpoint passes.
- Document ingestion reaches `finished`.
- API logs include request IDs and runtime events.
- Worker logs include `ingestion.job.succeeded`.

## Validated Local Evidence

Validated on 2026-06-20:

- the `ai-debug-local` kind cluster was created and the node reached `Ready`
- the project image `ai-debug-assistant-api:local` was loaded into the cluster
- PostgreSQL and Redis were deployed in the `ai-debug` namespace and reached healthy running state
- the Alembic migration Job ran successfully against PostgreSQL
- the API Service was port-forwarded locally and `/api/v1/health`, `/api/v1/ready`, and `/api/v1/metrics` passed
- `/api/v1/query` returned citations, warnings, and a `retrieval_trace_id`
- `/api/v1/evaluations/run` passed with expected threshold fields
- protected-route auth succeeded with the local API key and failed without it
- ingestion jobs were queued through the Kubernetes-hosted API and processed successfully by the worker
- API logs showed structured `http.request.completed` and `readiness.checked` events with request IDs
- worker logs showed `worker.started`, `ingestion.job.started`, and `ingestion.job.succeeded`

## Helm Packaging

Why Helm exists here:

- raw manifests are good for learning each object directly
- Helm packages those same objects into a reusable deployment unit
- values files let you keep one chart and change environment-specific settings without copying YAML files

Chart location:

```text
infra/helm/ai-debug-assistant
```

Important chart files:

- `Chart.yaml`: chart metadata
- `values.yaml`: default values
- `values-kind.yaml`: the validated local Kubernetes values for `kind`
- `templates/`: parameterized Kubernetes manifests

Useful Helm commands:

Render the chart locally without applying it:

```powershell
helm template ai-debug-assistant infra/helm/ai-debug-assistant --namespace ai-debug -f infra/helm/ai-debug-assistant/values-kind.yaml
```

Install or upgrade the chart locally:

```powershell
helm upgrade --install ai-debug-assistant infra/helm/ai-debug-assistant --namespace ai-debug --create-namespace -f infra/helm/ai-debug-assistant/values-kind.yaml --wait --wait-for-jobs --timeout 240s
```

Uninstall the chart:

```powershell
helm uninstall ai-debug-assistant -n ai-debug
```

How this maps to what you already learned:

- Helm `templates/` still produce normal Kubernetes objects
- the chart is not replacing Deployments, Services, Jobs, ConfigMaps, or Secrets
- it is generating them from values instead of keeping one fully hardcoded YAML per environment

## Recorded Failure Drill

Redis readiness drill validated on 2026-06-20:

1. scale Redis down:

   ```powershell
   kubectl scale deployment redis --replicas=0 -n ai-debug
   ```

2. confirm readiness degrades:

   ```powershell
   Invoke-RestMethod http://127.0.0.1:8000/api/v1/ready
   ```

   Expected result:

   - `status: degraded`
   - `redis_queue: unavailable`

3. restore Redis:

   ```powershell
   kubectl scale deployment redis --replicas=1 -n ai-debug
   Invoke-RestMethod http://127.0.0.1:8000/api/v1/ready
   ```

   Expected recovery:

   - readiness returns `ok`
   - `redis_queue` returns to `ok`

This drill demonstrates the intended probe split:

- liveness keeps the API process running
- readiness removes the Pod from traffic when a critical dependency is unavailable

## Next Step

After raw manifests work, convert them into a Helm chart so the same deployment shape can be reused for local Kubernetes and later AWS EKS.
