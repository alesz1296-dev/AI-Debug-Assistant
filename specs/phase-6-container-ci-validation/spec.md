# Phase 6 Spec: Container + CI Validation

## Goal

Validate the application as a repeatable containerized service with CI checks that prove a clean checkout can build and test it.

## Requirements

- Existing Dockerfile and compose scaffold must be validated and documented.
- CI must run lint, tests, type checks, and container build validation.
- Local clean-checkout instructions must be accurate.
- Configuration must be environment-driven.

## Acceptance Criteria

- Docker image builds successfully.
- Compose stack runs API, Postgres, and Redis locally.
- CI runs lint, tests, type checks, and image build validation.
- README documents clean local setup and container setup.

## Out Of Scope

- Terraform.
- AWS deployment.
- Kubernetes manifests.
