# ADR-003: Secrets outside code
Date: 2025-12-14
Status: Accepted

## Context
Secrets leakage risk.

## Decision
Use env vars and CI secrets.

## Alternatives
- Hardcoded secrets
- Encrypted config

## Consequences
Lower leakage risk.

## Security impact
Mitigates R8.

## Rollout plan
Enforce gitleaks in CI.

## Links
- NFR-07
- Threat model: R8
