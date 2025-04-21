# Logs Parser

## Описание
CLI-приложение для анализа логов и генерации отчетов на основе шаблонов. Основные функции:
* Разбор логов по заданному шаблону.
* Генерация отчётов по определённым меткам и фильтрам.
* Поддержка разных форматов отчетов.
* Каждый файл обрабатывается в отдельном процессе.

## Стек
* Python3: argparse, os, multiprocessing, regex
* **Тестирование**: pytest, pytest-cov

## Навигация
* [Предварительные требования](#предварительные-требования)
* [Деплой](#деплой)
* [Конфигурация приложения](#конфигурация-приложения)
* [Тестирование](#тестирование)
  * [Pytest](#pytest)

## Предварительные требования:
* [Python 3.11+](https://www.python.org/downloads/)

## Деплой
Клонируйте репозиторий:

```bash
git clone https://github.com/iamshelldy/logs-parser.git
cd logs-parser
```

Выполните из корня проекта следующие команды:\
Создайте виртуальное окружение:
```bash
python3 -m venv venv  
source venv/bin/activate  # На Windows: venv\Scripts\activate  
```
Установите зависимости Python:
```bash
pip install -r requirements.txt
```
Запустите приложение:
```bash
python main.py samples\app1.log samples\app2.log samples\app3.log --report handlers
```
или для краткости
```bash
python main.py samples\app1.log samples\app2.log samples\app3.log -r handlers
```
Также вы можете вывести отчет в файл, указав имя файла через ключ `--output` или `-o`:
```bash
python main.py samples\app1.log samples\app2.log samples\app3.log -r handlers -o out.txt
```

## Конфигурация приложения
Путь к файлу шаблонов отчетов можно настроить в файле конфигурации `app/config.py`:
```python
TEMPLATES_FILE = "templates.json"
```
Шаблоны создаются в указанном выше файле.
Чтобы создать новый отчет, добавьте шаблон в файл:
```json
[
  ...
    "handlers": {
    "log_formats": [
      "<date> <time> <levelname> <name>: <method> <handler> <status_code> <status> [<ip>]",
      "<date> <time> <levelname> <name>: <error>: <handler> [<ip>] - <description>"
    ],
    "filters": {
      "name": "django.request"
    },
    "x_axis": "levelname",
    "y_axis": "handler",
    "total": "requests"
  },
  ...
]
```
Примечание: в примере выше вместо фильтра ```"name": "django.request"``` можно также использовать форматы логов с вложенным фильтром:
```json
[
  "<date> <time> <levelname> django.request: <method> <handler> <status_code> <status> [<ip>]",
  "<date> <time> <levelname> django.request: <error>: <handler> [<ip>] - <description>"
]
```
Части шаблона лога именуются с помощью <> синтаксиса.\
В примере выше, "hanlders" - название отчета;\
"x_axis" - часть шаблона, используемая в качестве шапки отчета;\
"y_axis" - часть шаблона, используемая в первой колонке отчета;\
значение ключа "total" используется для подставления в отчет "Total объектов".

Чтобы "перевернуть" результирующую таблицу в отчете, поменяйте значения "x_axis" и "y_axis" друг с другом.

## Тестирование

### Pytest
Запуск тестов, из корня проекта:
```bash
pytest tests
```
Проверка покрытия проекта тестами:
```bash
pytest --cov=.
```
