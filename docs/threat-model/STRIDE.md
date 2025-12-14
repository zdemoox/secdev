# STRIDE — Threat Analysis

STRIDE-анализ для ключевых потоков и элементов Study Planner.
Контроли ссылаются на NFR из P03.

| Поток / Элемент | Угроза (STRIDE) | RiskID | Контроль | Ссылка на NFR | Проверка |
|-----------------|------------------|--------|----------|---------------|----------|
| F1 Client→API | S: Spoofing | R1 | HTTPS + TLS | NFR-01 | Конфигурация TLS |
| F1 Client→API | T: Tampering | R2 | Валидация входа | NFR-03 | Негативные тесты |
| APIGW | R: Repudiation | R3 | Correlation ID | NFR-05 | Логи |
| Service API | I: Info Disclosure | R4 | Единый формат ошибок | NFR-02 | Контракт-тест |
| Service API | D: DoS | R5 | Rate limiting | NFR-04 | Нагрузочный тест |
| Database | T: Data corruption | R6 | Атомарные операции | NFR-10 | Интеграционные тесты |
| Build | E: Privilege escalation | R7 | SCA policy | NFR-06 | CI отчёт |
| Repo | I: Secret leakage | R8 | gitleaks | NFR-07 | CI scan |
