# NFR BDD — Security/Quality Acceptance (Gherkin)

Сценарии приёмки для ключевых NFR. Пороги в `Then` — **конкретные и измеримые**.

Feature: Единый формат ошибок и отсутствие утечек
  Scenario: Ошибка валидации возвращается в едином формате без PII
    Given сервис Study Planner запущен
    When клиент отправляет POST /topics с пустым title
    Then ответ имеет HTTP 422
    And тело ответа содержит поле error.code = "validation_error"
    And поле error.message не содержит e-mail, токены или трассировку стека

  Scenario: Неизвестный ресурс возвращает not_found без внутренних деталей
    Given сервис Study Planner запущен
    When клиент запрашивает GET /topics/999999
    Then ответ имеет HTTP 404
    And error.code = "not_found"
    And error.message не содержит внутренних путей файлов или названий исключений

Feature: Защита от злоупотреблений (rate limiting) — негативный сценарий
  Scenario: Превышение лимита запросов приводит к 429
    Given на публичном endpoint включён rate limit 60 req/min/IP
    When клиент отправляет 61 запрос к GET /topics за 60 секунд с одного IP
    Then не менее 1 ответа имеет HTTP 429

Feature: Зависимости без просроченных уязвимостей
  Scenario: Critical/High уязвимости не старше 7 дней
    Given в CI включён SCA (Dependabot/OSV)
    When создаётся Pull Request в main
    Then отчёт не содержит нерешённых Critical/High уязвимостей старше 7 дней

Feature: Производительность чтения списка тем
  Scenario: p95 latency укладывается в порог на stage
    Given сервис развернут на stage и нагрузка 50 RPS
    When запускается 5-минутный нагрузочный тест для GET /topics
    Then p95 времени ответа <= 250 ms
