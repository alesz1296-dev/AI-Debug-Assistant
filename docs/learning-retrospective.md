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

