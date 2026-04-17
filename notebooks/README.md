# Ноутбуки (`notebooks/`)

Инструкции для локального запуска ноутбуков с зависимостями из группы `research` в `pyproject.toml`.

## Требования

- Python 3.11+
- `uv`

## Настройка среды

Из корня проекта выполните:

```bash
uv venv
uv sync --frozen --no-dev --group research --no-install-project
```

Команда установит:
- базовые зависимости проекта (`[project].dependencies`);
- зависимости для исследований (`[dependency-groups].research`), включая `ipykernel`, `matplotlib` и OCR-стек (`paddleocr`, `paddlepaddle`).

## Активация окружения

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

## Запуск ноутбука

Выберите созданную среду `.venv`
в качестве ядра (kernel) для выполнения ячеек.
