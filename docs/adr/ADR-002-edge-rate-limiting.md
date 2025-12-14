# ADR-002: Edge rate limiting
Date: 2025-12-14
Status: Accepted

## Context
Risk of DoS on public endpoints.

## Decision
Add rate limiting middleware.

## Alternatives
- Gateway-based limits
- No limits

## Consequences
Basic DoS protection.

## Security impact
Mitigates R5.

## Rollout plan
Replace with gateway/redis in prod.

## Links
- NFR-04
- Threat model: R5
