# Course Work 1: Transaction Analysis

## Описание проекта

Этот проект представляет собой приложение для анализа финансовых транзакций, которое позволяет пользователям загружать данные о транзакциях из файлов Excel, CSV или JSON, генерировать отчёты по категориям расходов и отображать финансовую информацию, включая курсы валют и цены акций. Проект реализован на Python с использованием библиотек `pandas`, `requests`, и `python-dotenv` для работы с данными, API и конфигурацией.

## Установка

**1. Клонируйте репозиторий**:

git clone git@github.com:Couguar-lab/Course_work_1

**2. Создайте и активируйте виртуальное окружение**:

python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

**3. Установите зависимости**:

pip install pytest pandas openpyxl requests python-dotenv

**4. Настройте переменные окружения**:
Создайте файл .env в корне проекта.
  
**5. Добавьте API-ключи для курсов валют и цен акций**:

EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key

FINNHUB_API_KEY=your_finnhub_api_key

Получите ключи на ExchangeRate-API и Finnhub.

# Запуск приложения
python src/main.py

Это вызовет функцию home_page для генерации финансовой сводки и отчёт по категории "Супермаркеты" за указанную дату.
  
Логирование:
Логи записываются в logs/all.log (общие логи) и logs/services.log (логи сервисов).

Логи также выводятся в консоль.

# Тестирование
Запустите тесты:  pytest

# ЗависимостиPython 3.13.3
Зависимости внесены в файл pyproject.toml


**Курсовая работа по программированию на Python, 2025 год.**

ЛицензияMIT License. См. файл LICENSE (если применимо).