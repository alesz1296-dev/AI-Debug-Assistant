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

The current GitHub Actions workflow now runs install, Ruff, mypy, pytest, and a sequential Docker Compose API image build.

Still intentionally outside the Phase 6 CI scope:

- compose runtime startup validation
- migration execution inside CI
