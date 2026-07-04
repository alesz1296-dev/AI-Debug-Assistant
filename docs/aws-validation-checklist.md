# AWS Validation Checklist

This checklist is the project-facing validation target for the future AWS environment. It is intended for Stage 8C execution after Stage 8B decisions are complete.

## Terraform Validation

- [x] bootstrap state creates the S3 backend bucket successfully.
- [x] bootstrap state creates the DynamoDB lock table successfully.
- [x] `terraform validate` passes for the selected environment.
- [x] `terraform plan` succeeds without manual console-only prerequisites.
- [x] remote state backend is reachable and behaves as expected.
- [x] environment roots use the intended remote backend for `dev`, `staging`, or `prod`.

## Infrastructure Validation

- [x] VPC, subnets, routing, and security groups are created as planned.
- [x] multi-AZ subnet layout matches the intended `us-east-1` design.
- [ ] ECR repository exists and accepts image push.
- [ ] default `dev` plan excludes EKS, NAT Gateway, RDS, ElastiCache, ALB, and Container Insights.
- [ ] EKS cluster is reachable with `kubectl` during a short-lived EKS lab.
- [ ] managed node group reaches healthy ready state during a short-lived EKS lab.
- [ ] RDS PostgreSQL is reachable from EKS workloads.
- [ ] ElastiCache Redis or Valkey is reachable from EKS workloads.
- [ ] AWS Load Balancer Controller is installed and healthy.
- [ ] External Secrets Operator is installed and healthy.

## Cheap Baseline Validation

- [ ] `enable_eks = false`.
- [ ] `enable_nat_gateway = false`.
- [ ] `enable_rds = false`.
- [ ] `enable_elasticache = false`.
- [ ] `enable_alb = false`.
- [ ] `enable_container_insights = false`.
- [ ] `terraform plan` shows no EKS cluster or node group creation.
- [ ] `terraform plan` shows no NAT Gateway or NAT Elastic IP creation.
- [ ] `terraform plan` shows no RDS creation.
- [ ] `terraform plan` shows no ElastiCache creation.
- [ ] `terraform plan` shows no ALB creation.
- [ ] `terraform plan` shows no Container Insights enablement.
- [ ] `terraform plan` retains only the low-cost baseline resources needed for networking and ECR.
- [ ] if previous EKS or NAT resources exist in state, the plan clearly shows their removal.

## Short-Lived EKS Lab Validation

- [ ] AWS identity is confirmed before the lab.
- [ ] a free-tier-eligible node instance type is confirmed with AWS CLI before apply.
- [ ] `enable_eks = true`.
- [ ] `eks_subnet_tier = "public"` unless a private-subnet lab intentionally enables NAT.
- [ ] `terraform plan` is reviewed for EKS, node group, IAM roles, and subnet placement.
- [ ] `aws eks update-kubeconfig` succeeds.
- [ ] `kubectl get nodes` shows the managed node group nodes as `Ready`.
- [ ] `kubectl get pods -A` shows core system pods healthy.

## Post-Lab Teardown Validation

- [ ] `enable_eks = false` after the lab.
- [ ] EKS cluster is deleted.
- [ ] managed node group is deleted.
- [ ] no EKS worker EC2 instances remain.
- [ ] no lab-created Load Balancers remain.
- [ ] no orphaned Elastic IPs remain.
- [ ] NAT Gateway is absent unless intentionally retained.

## Application Validation

- [ ] Helm release installs successfully into EKS.
- [ ] Alembic migration Job completes successfully against RDS.
- [ ] API Deployment reaches ready state.
- [ ] worker Deployment reaches ready state.
- [ ] ALB exposes the application as designed for `dev`.
- [ ] `GET /api/v1/health` passes on AWS.
- [ ] `GET /api/v1/ready` passes on AWS.
- [ ] `GET /api/v1/metrics` passes on AWS.
- [ ] `POST /api/v1/query` passes on AWS.
- [ ] `POST /api/v1/evaluations/run` passes on AWS.
- [ ] ingestion enqueue and worker processing succeed on AWS.

## Observability and Security Validation

- [ ] application logs are visible in CloudWatch.
- [ ] cluster and workload signals are visible at the planned observability layer.
- [ ] Kubernetes workloads receive AWS access through the intended IRSA pattern.
- [ ] secrets are sourced from AWS-managed secret storage and not committed in git.
- [ ] protected routes still require the expected API key behavior.

## Failure and Recovery Validation

- [ ] at least one AWS-side readiness or dependency failure drill is documented.
- [ ] recovery behavior is documented and validated.
- [ ] teardown steps are exercised and documented.

## Current Evidence Summary

Validated in AWS `dev` so far:

- remote Terraform backend is active and usable from `infra/aws/envs/dev`
- `infra/aws/envs/dev` consumes reusable `network`, `ecr`, and `eks` modules
- `enable_eks = false` is now the default cost-controlled posture
- `enable_nat_gateway = false` is now the default cost-controlled posture
- `enable_rds = false`, `enable_elasticache = false`, `enable_alb = false`, and `enable_container_insights = false` are now explicit future-service defaults
- `eks_subnet_tier = "public"` is the default lower-cost short-lived EKS lab path
- VPC `ai-debug-assistant-ada-dev-vpc` exists in `us-east-1`
- two public subnets and two private subnets exist across `us-east-1a` and `us-east-1b`
- `ai-debug-assistant-ada-dev-igw` is attached to the VPC
- `ai-debug-assistant-ada-dev-nat` was validated previously and is now optional for cost control
- public route table default route points to the Internet Gateway
- private route table default route points to the NAT Gateway only when NAT is enabled
- ECR module is wired into `dev`; image push validation is still pending
- EKS module is wired into `dev` behind `enable_eks`; short-lived lab validation and teardown proof are still pending
