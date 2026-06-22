# AWS Validation Checklist

This checklist is the project-facing validation target for the future AWS environment. It is intended for Stage 8C execution after Stage 8B decisions are complete.

## Terraform Validation

- [ ] bootstrap state creates the S3 backend bucket successfully.
- [ ] bootstrap state creates the DynamoDB lock table successfully.
- [ ] `terraform validate` passes for the selected environment.
- [ ] `terraform plan` succeeds without manual console-only prerequisites.
- [ ] remote state backend is reachable and behaves as expected.
- [ ] environment roots use the intended remote backend for `dev`, `staging`, or `prod`.

## Infrastructure Validation

- [ ] VPC, subnets, routing, and security groups are created as planned.
- [ ] multi-AZ subnet layout matches the intended `us-east-1` design.
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
