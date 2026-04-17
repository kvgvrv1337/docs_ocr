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
- основные зависимости проекта (`[project].dependencies`);
- зависимости для исследований (`[dependency-groups].research`), включая `ipykernel` и `matplotlib`.

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

Откройте `notebooks/research.ipynb` в вашей IDE и выберите созданную среду `.venv`
в качестве ядра (kernel) для выполнения ячеек.
