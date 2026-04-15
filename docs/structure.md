# Файловая структура проекта и зоны ответственности


```text
docs_ocr/
  data/
    ...                      # изображения/примеры для локальной проверки
  docs/
    prd.md
    architecture.md
    structure.md
  src/
    core/
      ocr_service.py         # интерфейс OCR-сервиса (поведение/сигнатуры)
      extraction_service.py  # интерфейс extraction-сервиса (поведение/сигнатуры)
      schemas.py             # сквозные контракты данных: OCRResult, FioResult, PipelineResult
    providers/
      ocr_provider.py       # OCR-реализация + preprocessing внутри
      extraction_provider.py# Реализация извлечения сущностей
  main.py                    # оркестрация: image -> OCR -> extraction -> JSON
  pyproject.toml
  uv.lock
  README.md
  .gitignore
```

## Разделение ответственности

- `src/core` содержит только контракты и структуры данных.
- `src/providers` содержит конкретную прикладную логику распознавания и извлечения.
- `main.py` связывает шаги пайплайна и не хранит тяжелую бизнес-логику.

## Где хранить контракты результатов

- Контракты, используемые между модулями (`OCRResult`, `FioResult`, итог пайплайна), хранятся в `src/core/schemas.py`.
- Файлы `src/core/ocr_service.py` и `src/core/extraction_service.py` содержат только интерфейсы сервисов (методы и ожидаемые входы/выходы через схемы).
- Локальные вспомогательные типы, которые нужны только внутри одного провайдера, можно оставлять рядом с ним.


