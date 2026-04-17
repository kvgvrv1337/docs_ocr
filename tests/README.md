# Тесты (`tests/`)

Инструкции для локального запуска тестов с зависимостями из группы `test` в `pyproject.toml`.

## Требования

- Python 3.11+
- `uv`

## Настройка среды

Из корня проекта выполните:

```bash
uv venv
uv sync --frozen --no-dev --group test --no-install-project
```

Команда установит:
- основные зависимости проекта (`[project].dependencies`);
- зависимости для тестов (`[dependency-groups].test`), включая `pytest`.

## Активация окружения

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

## Запуск тестов

Запуск всего набора:

```bash
pytest
```

Запуск только CI-safe теста с мокнутым OCR (без реального инференса):

```bash
pytest tests/test_application.py::test_application_run_and_save_with_stubbed_ocr
```

Примечания:
- тесты, которые используют реальные изображения, могут быть пропущены при отсутствии файлов в `data/`;
- для OCR-тестов также нужны модели PaddleOCR (первый запуск может занять время из-за загрузки).
