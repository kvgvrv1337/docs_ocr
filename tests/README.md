# Тесты (`tests/`)

Инструкции для локального запуска тестов с зависимостями из группы `test` в `pyproject.toml`.

## Требования

- Python 3.11+
- `uv`

## Настройка среды (быстрый CI-safe вариант)

Из корня проекта выполните:

```bash
uv venv
uv sync --frozen --no-dev --group test --no-install-project
```

Команда установит:
- базовые зависимости проекта (`[project].dependencies`);
- зависимости группы `test` (`pytest`, `ruff`);
- без тяжелых OCR-зависимостей (`paddleocr`, `paddlepaddle`).

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

Запуск только CI-safe теста с мокнутым OCR (без реального инференса):

```bash
pytest tests/test_application.py::test_application_run_and_save_with_stubbed_ocr
```

Запуск линтера (как в CI):

```bash
ruff check src tests
ruff format --check tests
```

## Полный прогон тестов с OCR

Если хотите запускать OCR-тесты локально (не только CI-safe), установите дополнительно группу `ocr`:

```bash
uv sync --frozen --no-dev --group test --group ocr --no-install-project
pytest
```

Примечания:
- тесты, которые используют реальные изображения, могут быть пропущены при отсутствии файлов в `data/`;
- OCR-тесты и CLI-прогон с реальным OCR требуют `paddleocr/paddlepaddle` и могут скачивать модели при первом запуске.
