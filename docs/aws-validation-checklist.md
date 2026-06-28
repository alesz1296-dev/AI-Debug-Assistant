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
- [ ] EKS cluster is reachable with `kubectl`.
- [ ] managed node group reaches healthy ready state.
- [ ] RDS PostgreSQL is reachable from EKS workloads.
- [ ] ElastiCache Redis or Valkey is reachable from EKS workloads.
- [ ] AWS Load Balancer Controller is installed and healthy.
- [ ] External Secrets Operator is installed and healthy.

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
- VPC `ai-debug-assistant-ada-dev-vpc` exists in `us-east-1`
- two public subnets and two private subnets exist across `us-east-1a` and `us-east-1b`
- `ai-debug-assistant-ada-dev-igw` is attached to the VPC
- `ai-debug-assistant-ada-dev-nat` is available in the first public subnet
- public route table default route points to the Internet Gateway
- private route table default route points to the NAT Gateway
