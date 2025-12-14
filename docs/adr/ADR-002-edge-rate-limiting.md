# ADR-002: Rate limiting на Edge для публичных endpoints
Дата: 2025-12-14
Статус: Accepted

## Context
В Threat Model (P04) присутствует риск **R5 (DoS)** на потоке F1 (Client → API).

## Decision
- Best-effort rate limiting middleware на уровне API (Edge).
- Лимит по умолчанию: 60 req/min/IP (конфигурируется).
- При превышении возвращать HTTP 429 в error-envelope с `correlation_id`.

## Alternatives
- Rate limiting на gateway/ingress
- Redis-backed limiter
- Без rate limiting

## Consequences
In-memory ограничитель не подходит для кластера; для курса — достаточно.

## Security impact
Снижаем риск **R5 (DoS)**.

## Rollout plan
В проде перенести в gateway/ingress или Redis.

## Links
- NFR-04 (Rate limiting), NFR-08 (Доступность)
- Threat Model: F1, риск R5
- Реализация: `app/main.py`
- Тесты: `tests/test_errors.py::test_rate_limit_blocks_after_threshold`
