# Phase 8 Spec: Local Kubernetes to AWS EKS Platform (ADA)

## Goal

Promote the DevOps-ready Compose platform into a Kubernetes-first platform path. Phase 8 starts with local Kubernetes so the deployment model, Helm chart, probes, migration jobs, worker runtime, and debugging workflow are proven before any AWS resources are created.

After the local Kubernetes gate passes, the same workload can move to AWS EKS through Terraform-managed infrastructure.

Stage 8B (ADA) is also the transition point from agent-led implementation into owner-led implementation. From this stage forward, the project owner should perform as much of the hands-on Terraform and AWS work as possible, with Codex acting as teacher, architectural guide, reviewer, and debugging partner.

## Requirements

- Build a local Kubernetes deployment path before AWS work starts.
- Use a four-environment ladder: `local`, `dev`, `staging`, and `prod`.
- Keep `local` as the Kind/Compose learning and validation lab.
- Use `dev` as the first AWS environment, `staging` as the production rehearsal space, and `prod` as the final live environment.
- Package the API and worker with Helm or Kubernetes manifests.
- Represent Alembic migrations as an explicit Kubernetes Job.
- Configure API readiness and liveness probes against `/api/v1/ready` and `/api/v1/health`.
- Run the API and worker as separate Kubernetes workloads.
- Keep Postgres and Redis dependencies explicit for local Kubernetes validation.
- Define AWS infrastructure as a later Phase 8 stage using Terraform, with EKS treated as an opt-in lab target.
- Keep AWS `dev` cost-controlled by default, with EKS and other billable services enabled only for focused labs.
- Use three operating profiles: `local-full`, `aws-free-friendly`, and `aws-eks-lab`.
- Design Terraform around reusable modules rather than a single flat stack.
- Use ECR for image publishing before EKS deployment, with a repeatable local publishing helper before CI automation.
- Use RDS PostgreSQL with pgvector for the AWS database target.
- Use ElastiCache Redis or Valkey for the AWS queue/cache target.
- Add Kubernetes/AWS secrets handling without committing secrets.
- Add logs and metrics validation for local Kubernetes and AWS EKS.
- Document manual smoke tests, debugging commands, failure modes, and teardown.
- Keep tracked documentation limited to project-facing architecture, tasks, validation, and operational runbooks.
- Keep all personal learning notes, coaching notes, study prompts, and reflections in ignored private directories only.
- Define Stage 8B decisions before Stage 8C implementation starts.

## Acceptance Criteria

- Local Kubernetes can deploy the API, worker, and migration job from the same container image.
- Local Kubernetes smoke tests prove health, readiness, query, evaluation, ingestion enqueue, worker processing, metrics, and logs.
- Kubernetes manifests or Helm templates are reproducible and reviewed before AWS deployment.
- The environment strategy clearly distinguishes `local`, `dev`, `staging`, and `prod`.
- Terraform module boundaries are documented so AWS infrastructure can be built and reused cleanly across environments.
- Stage 8B documents the AWS target architecture, Terraform structure, secrets approach, validation workflow, and teardown workflow clearly enough that Stage 8C can be executed without further architecture decisions.
- Terraform plans the AWS EKS foundation without manual console setup.
- AWS image publishing workflow is documented, manually validated, and repeatable from a local script.
- AWS deployment workflow is documented and repeatable before any long-running AWS app stack is claimed.
- Secrets are not stored in git.
- Operational demo proves health, readiness, logs, metrics, migrations, and worker processing after deployment.
- Teardown and cost-control steps are documented before any AWS apply.
- Default `dev` Terraform plans do not create EKS, NAT Gateway, RDS, ElastiCache, ALB, or Container Insights unless explicitly enabled for a lab.
- EKS lab validation includes immediate teardown proof before the project moves to later AWS application deployment work.

## Out Of Scope

- High-availability production SLOs.
- Multi-region deployment.
- Automatic Terraform apply.
- Automatic production deployment.
- Dashboard unless Phase 9 is started.
- LangChain or LangGraph adoption unless a future spec justifies it.
- Committing personal study notes or coaching notes into tracked project documentation.
