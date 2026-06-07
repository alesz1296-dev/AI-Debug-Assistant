# Phase 6 Plan: Container + CI Validation

## Approach

Treat the existing Docker and GitHub Actions files as scaffold until validated. Promote them to accepted platform assets only after build, compose, and CI behavior are proven.

## Validation Commands

- Python tests.
- Ruff lint.
- Mypy type check.
- Docker image build.
- Compose local startup.

## Documentation

README should distinguish local Python setup from containerized setup and should not claim cloud readiness.

## Validated Evidence So Far

- Local Docker Compose startup has been validated for `api`, `postgres`, and `redis`.
- The containerized migration path has been validated through `0003_enable_vector`.
- The Dockerized API has been validated through `/health`, `/ready`, `/metrics`, and `/query`.

## Current CI Status

The current GitHub Actions workflow runs install, Ruff, and pytest only.

Still missing against the Phase 6 target:

- mypy
- Docker image build validation
