# NFR Traceability — NFR ↔ Stories/Tasks

Трассировка показывает, что NFR встроены в backlog/roadmap. Истории ниже — **планируемые** задачи для Study Planner.
Рекомендуется завести их как GitHub Issues с label `nfr` / `security` и (опционально) привязать к Milestone.

| Story/Task ID | Название / Краткое описание | Связанные NFR | Приоритет | Release / Milestone |
|---------------|-----------------------------|---------------|-----------|---------------------|
| SP-01 | Единый формат ошибок для всех endpoints | NFR-02, NFR-03 | High | MVP |
| SP-02 | Негативные тесты на валидацию входных данных | NFR-03 | High | MVP |
| SP-03 | Correlation ID + политика логов без секретов | NFR-05 | Medium | Hardening |
| SP-04 | SCA (Dependabot/OSV) + правило «Critical/High <= 7 дней» | NFR-06 | High | Hardening |
| SP-05 | gitleaks/semgrep в CI: запрет секретов в git | NFR-07 | High | MVP |
| SP-06 | Настроить HTTPS/TLS и HSTS на ingress/reverse-proxy | NFR-01 | High | Release-1 |
| SP-07 | Добавить rate limiting на публичные endpoints | NFR-04 | Medium | Release-1 |
| SP-08 | Мониторинг `/health` и алёрты по SLO | NFR-08 | Medium | Release-1 |
| SP-09 | Нагрузочный тест GET /topics и порог p95 | NFR-09 | Medium | Hardening |
| SP-10 | (При DB) атомарность изменений через транзакции | NFR-10 | Medium | Release-2 |

## Как использовать в PR (рекомендация)
- В PR описании укажите ссылки на Issues (например, `Closes #12`, `Refs #13`) и Milestone.
- Для задач уровня Hardening добавляйте критерии приёмки из `NFR_BDD.md`.
