## P09 — SBOM & SCA (dependencies)

### Что сделано
- Добавлен workflow **Security - SBOM & SCA**: `.github/workflows/ci-sbom-sca.yml`
- SBOM генерируется Syft в формате CycloneDX JSON → `EVIDENCE/P09/sbom.json`
- SCA выполняется Grype по SBOM → `EVIDENCE/P09/sca_report.json`
- Краткая сводка по severity → `EVIDENCE/P09/sca_summary.md`
- Добавлен шаблон waivers: `policy/waivers.yml`

### Где смотреть артефакты
- В репозитории: `EVIDENCE/P09/*` (после первого успешного прогона замените placeholder-версии на реальные файлы из артефакта Actions)
- В Actions: артефакт **P09_EVIDENCE**

### Что дальше делать с уязвимостями
- Триаж High/Critical → обновление зависимостей (предпочтительно)
- Если фикс невозможен: оформить time-limited waiver в `policy/waivers.yml` со ссылкой на Issue/PR и сроком пересмотра
