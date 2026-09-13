# Retail Automation

Автоматизация сбора и загрузки данных о продажах торговой сети.

## Описание

Каждый день из кассового софта в папку `data/` выгружаются CSV-файлы с информацией по чекам и продажам. Скрипт `generator` эмулирует эту выгрузку, `loader` загружает её в PostgreSQL. Обе задачи запускаются автоматически по расписанию.

## Стек

- **Python 3.10+** (проверено на 3.13)
- **PostgreSQL 14+** (проверено на 18.1)
- **Windows Task Scheduler** (или cron для Linux/macOS)
- Библиотеки: `psycopg2-binary`, `PyYAML`

## Структура проекта

```
retail-automation/
├── config/
│   └── config.yaml       # параметры подключения и путей
├── data/                 # CSV-выгрузки из касс (в git не попадают)
│   └── example.csv       # пример формата
├── img/                  # изображения для README
├── logs/                 # логи работы скриптов
├── sql/
│   └── schema.sql        # схема БД
├── src/
│   ├── __init__.py
│   ├── config_loader.py  # загрузка config.yaml
│   ├── db.py             # подключение к PostgreSQL
│   ├── generator.py      # эмуляция выгрузки CSV
│   └── loader.py         # загрузка CSV в PostgreSQL
├── run_generator.bat     # запуск генератора (для Task Scheduler)
├── run_loader.bat        # запуск загрузчика (для Task Scheduler)
├── requirements.txt
└── README.md
```

## Установка

```bash
git clone https://github.com/sustavovarimma/retail-automation.git
cd retail-automation

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
```

## Настройка

Параметры подключения к БД и пути к данным — в `config/config.yaml`. Перед первым запуском создайте схему:

```bash
psql -U postgres -d retail -f sql/schema.sql
```

## Запуск

Вручную:

```bash
.venv\Scripts\python.exe src\generator.py
.venv\Scripts\python.exe src\loader.py
```

Или через `.bat`-файлы (они же используются планировщиком):

```bash
run_generator.bat
run_loader.bat
```

## Расписание

Задачи зарегистрированы в **Windows Task Scheduler** и запускаются ежедневно:

| Задача | Время | Что делает |
|--------|-------|------------|
| `RetailGenerator` | 23:30 | Генерирует CSV-файлы (эмуляция выгрузки из касс) |
| `RetailLoader`    | 23:45 | Загружает новые CSV в PostgreSQL (идемпотентно) |

### Создание задач

PowerShell **от имени администратора**:

```powershell
$root = "C:\Users\susta\Desktop\retail-automation"

$actionG  = New-ScheduledTaskAction -Execute "$root\run_generator.bat" -WorkingDirectory $root
$actionL  = New-ScheduledTaskAction -Execute "$root\run_loader.bat"    -WorkingDirectory $root

$triggerG = New-ScheduledTaskTrigger -Daily -At "23:30"
$triggerL = New-ScheduledTaskTrigger -Daily -At "23:45"

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName "RetailGenerator" -Action $actionG -Trigger $triggerG -Settings $settings -Force
Register-ScheduledTask -TaskName "RetailLoader"    -Action $actionL -Trigger $triggerL -Settings $settings -Force
```

### Проверка и ручной запуск

```powershell
schtasks /Query /TN "RetailGenerator" /V /FO LIST
schtasks /Run   /TN "RetailGenerator"
schtasks /Run   /TN "RetailLoader"
```

Логи: `logs/generator_cron.log`, `logs/loader_cron.log`.

## Лицензия

MIT
