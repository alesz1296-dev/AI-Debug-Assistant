# AWS Teardown and Cost Control Runbook

This runbook defines the project-facing expectations for cost control and teardown before any Stage 8C AWS apply work begins.

## Cost Posture

The default AWS posture for this project is a tight lab budget:

- smallest viable `dev` environment first
- `staging` scaffolded in structure, not necessarily provisioned immediately
- managed services chosen for production alignment, but sized conservatively
- no unnecessary always-on components before the core stack is validated

## Cost Control Rules

- no AWS resource creation before the teardown workflow is documented
- no automatic `terraform apply`
- no automatic `terraform destroy`
- no production-like overprovisioning in the initial `dev` environment
- no secret values committed to git

## Expected Cost-Sensitive Areas

Special attention should be given to:

- NAT-related networking cost
- managed node group sizing
- RDS instance class and storage
- ElastiCache node sizing
- ALB runtime cost
- CloudWatch log volume and retention

## Teardown Expectations

Before Stage 8C is considered complete, the project should define and later validate:

- how to destroy the `dev` environment safely
- how to preserve or intentionally remove remote state
- how to clean up ECR artifacts when appropriate
- how to confirm that RDS, ElastiCache, ALB, and cluster resources are no longer billing
- how to capture final evidence before destructive teardown

## Required Future Teardown Checklist

- [ ] confirm final validation evidence is saved
- [ ] confirm no protected data must be retained
- [ ] destroy application layer dependencies in the intended order
- [ ] destroy infrastructure layer resources in the intended order
- [ ] confirm AWS billing-sensitive resources are gone
- [ ] record teardown result in the tracked phase docs
