# docs_ocr

MVP-пайплайн для извлечения ФИО из изображений СТС.

Исходные изображения содержат персональные данные, поэтому они исключены из VCS и Docker context.  
Перед запуском вручную положите входные файлы в папку `data/`.

## Быстрый старт

1. Создайте папки (если их еще нет):
   - `data/` — входные изображения.
   - `outputs/` — выходные JSON.
2. Добавьте изображение, например `data/test3.png`.
3. Выберите запуск:
   - через Docker (рекомендуется для одинакового окружения),
   - или локально через `venv`.

## Запуск через Docker

Требования:
- Docker Desktop / Docker Engine с Compose.

Сборка образа:

```bash
docker compose build docs-ocr
```

Проверка CLI-параметров:

```bash
docker compose run --rm docs-ocr --help
```

Запуск распознавания:

```bash
docker compose run --rm docs-ocr --input_path /app/data/test3.png
```

Где смотреть результат:
- по умолчанию `--output_path` и `--max_side` опциональные.
- если `--output_path` не указан, JSON сохраняется рядом со входным файлом.
- для примера выше результат появится в `data/test3.json`.
- при необходимости можно явно задать:
  - `--output_path /app/outputs/test3.json`
  - `--max_side 2500`

Примечания:
- Первый запуск может скачать OCR-модели.
- В `docker-compose.yaml` подключены именованные volume для кэша моделей (`paddlex-cache`, `paddle-cache`), поэтому повторные запуски обычно не скачивают модели заново.

## Локальный запуск через venv

Требования:
- Python 3.11+
- `uv` (рекомендуется для установки зависимостей из lock-файла)

Создание окружения и установка runtime-зависимостей:

```bash
uv venv
uv sync --frozen --no-dev --no-install-project
```

Активация окружения:

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Запуск приложения:

```bash
python -m src.main --input_path data/test3.png --output_path outputs/test3.json --max_side 2500
```

## Параметры CLI

- `--input_path` (обязательно): путь к входному изображению.
- `--output_path` (опционально): путь к выходному JSON.  
  Если не указан, JSON создается рядом с входным файлом (`<input>.json`).
- `--max_side` или `--max-side` (опционально, по умолчанию `2500`):  
  максимальная сторона изображения для даунскейла; `<= 0` отключает ресайз.