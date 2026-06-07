# Learning Retrospective

Public summary of lessons learned will be curated here. Private weekly notes live in `.learning/` and are ignored by Git.

## Week 1 Summary

- Established data ethics before implementation.
- Built a local-first RAG boundary.
- Added tests around API behavior and data safety.
- Preserved future production architecture without blocking the first runnable slice.

## Architecture Direction

- Reframed the project as a small production-grade AI platform.
- Added an SSD phase map that separates local MVP, persistence, workers, evaluation, observability, container validation, DevOps readiness, cloud deployment, and optional dashboard work.
- Defined Phase 7 as the handoff point where manual development becomes the primary mode and Codex shifts into guidance, review, and debugging support.

## Phase 6 Container Validation Lessons

- Docker validation needs to prove behavior, not just container existence. A stack is not really validated until `/health`, `/ready`, `/metrics`, and `/query` all work in the containerized path.
- Alembic revision naming matters operationally. Overlong revision IDs can fail against the `alembic_version` table even when the migration body is otherwise correct.
- Rebuilding the API image matters after migration edits. A correct host-side migration file does not help if the container still runs an older copied version.
- Pgvector setup is part of runtime readiness. Query failures in the database-backed path exposed that the `vector` extension must be enabled explicitly through migration.
- Shared database sessions need recovery behavior. Once a SQL error aborts a transaction, rollback handling is required or later requests can fail with `InFailedSqlTransaction`.
- Docker troubleshooting also taught a useful operational lesson: host port conflicts, stale network bindings, and partial compose recreation can look like app bugs until the infrastructure state is cleaned up.

