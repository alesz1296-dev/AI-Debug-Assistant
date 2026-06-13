# Phase 0 Tasks: Local MVP Baseline

- [x] Create project scaffold.
- [x] Add FastAPI health, query, ingestion, debug-case, and evaluation endpoints.
- [x] Add local deterministic embeddings and retrieval.
- [x] Add seed synthetic/public-style data.
- [x] Add tests for API shape, auth, evaluation, and data safety.
- [x] Add private learning-note template and public docs.

## Deployment-Ready Gates

These items are mandatory before the repo can be called deployment-ready:

- [x] Replace in-memory retrieval with PostgreSQL persistence.
- [x] Replace in-memory retrieval with pgvector or an equivalent vector store.
- [x] Add a worker or queue boundary for ingestion that should not run inline.
- [x] Add container build files and a verified local container run path.
- [x] Add CI that runs lint, tests, and build checks on every pull request.
- [x] Add OpenTelemetry traces or equivalent runtime observability hooks.
- [x] Add structured logs for query and ingestion operations.
- [x] Add readiness for orchestration with health and readiness endpoints documented.
- [ ] Add deployment automation for the target cloud environment.
- [ ] Document the deployment path from clean checkout to running service.

## DevOps-Ready Gates

These original gates now separate local DevOps readiness from cloud deployment readiness. Phase 7 satisfies the local platform gates; the remaining cloud gates move to Phase 8.

- [ ] Add Terraform or equivalent infrastructure-as-code for cloud resources.
- [x] Add a repeatable environment bootstrap flow.
- [ ] Add a reproducible build-and-publish image workflow.
- [ ] Add a deployment workflow that does not rely on manual console setup.
- [x] Add an operational demo path that proves logs, metrics, and health checks in the local containerized platform.

## Post-MVP Product Gates

- [ ] Add React dashboard and screenshots.
- [ ] Add additional evaluation coverage beyond the golden cases.

Post-MVP gates are expanded into later phase directories. This Phase 0 task list remains the historical baseline for the current local MVP.

