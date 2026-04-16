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
      schemas.py             # DTO контракты
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



