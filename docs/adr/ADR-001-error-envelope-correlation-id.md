# ADR-001: Unified error envelope and correlation_id
Date: 2025-12-14
Status: Accepted

## Context
API errors must not leak internal details and must be traceable.

## Decision
Use a unified JSON error envelope with correlation_id.

## Alternatives
- Raw FastAPI errors
- Full RFC7807

## Consequences
Improved debuggability, stable contract.

## Security impact
Mitigates R4, partially R3.

## Rollout plan
Enable middleware and add tests.

## Links
- NFR-02, NFR-05
- Threat model: R3, R4
- tests/test_errors.py
