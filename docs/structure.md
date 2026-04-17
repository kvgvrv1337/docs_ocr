# Файловая структура проекта и зоны ответственности

```text
docs_ocr/
  .github/
    workflows/
      ci.yml                      # CI: lint + формат + CI-safe тест
  docs/
    prd.md                        # постановка задачи
    architecture.md               # описание архитектуры и roadmap
    structure.md                  # текущий файл
  models/
    .gitkeep                      # плейсхолдер каталога под локальные артефакты
  notebooks/
    README.md                     # инструкции по запуску исследований
    research.ipynb                # ноутбук с exploratory/research логикой
  src/
    core/
      services/
        ocr_service.py            # контракт OCR-сервиса
        extraction_service.py     # контракт сервиса извлечения ФИО
      schemas.py                  # DTO/схемы пайплайна
    providers/
      ocr_provider.py             # PaddleOCR-провайдер (2 прохода, crop по anchor)
      extraction_provider.py      # rule-based извлечение ФИО из OCR-текста
    main.py                       # CLI и оркестрация пайплайна
  tests/
    README.md                     # как запускать тесты
    test_application.py           # тесты оркестрации/CLI
    test_extraction_service.py    # тесты извлечения ФИО
    test_ocr_service.py           # интеграционный OCR-тест (опционально)
  .dockerignore
  .gitignore
  docker-compose.yaml
  Dockerfile
  pyproject.toml
  README.md
  uv.lock
```

## Разделение ответственности

- `src/core` — доменные контракты и структуры данных без тяжелых зависимостей.
- `src/providers` — конкретные реализации OCR и извлечения сущностей.
- `src/main.py` — композиция зависимостей, CLI-парсинг, запуск и сохранение результата.
- `tests` — unit/integration покрытие и документация по запуску.
- `docs` — продуктовые и архитектурные артефакты проекта.

## Локальные (игнорируемые) каталоги

- `data/` — входные изображения для локальной проверки (не хранится в репозитории).
- `outputs/` — выходные JSON-файлы при локальном запуске.
