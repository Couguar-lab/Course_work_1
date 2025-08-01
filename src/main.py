import logging
import os
import sys

import pandas as pd
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    filename="logs/all.log",
    encoding="utf-8",
    force=True,
)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

# Добавляем корневую директорию в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
logger.debug(f"sys.path обновлён: {sys.path}")

# Явная загрузка .env
load_dotenv()
exchange_rate_key = os.getenv("EXCHANGE_RATE_API_KEY")
finnhub_key = os.getenv("FINNHUB_API_KEY")
logger.debug(f"EXCHANGE_RATE_API_KEY: {exchange_rate_key}")
logger.debug(f"FINNHUB_API_KEY: {finnhub_key}")

try:
    from src.reports import spending_by_category
    from src.views import home_page
except ImportError as e:
    logger.error(f"Ошибка импорта модулей: {str(e)}")
    raise


def main():
    logger.debug("Запуск программы")
    try:
        # Тестовый вызов home_page с датой из данных
        result = home_page("2021-12-31 17:00:00")
        logger.debug(f"Результат home_page: {result}")

        # Тестовый вызов отчета с преобразованием даты
        test_transactions = [
            {
                "Дата операции": "31.12.2021 16:44:00",
                "Номер карты": "*7197",
                "Сумма платежа": -160.89,
                "Кэшбэк": 0.0,
                "Категория": "Супермаркеты",
                "Описание": "Колхоз",
            }
        ]
        df = pd.DataFrame(test_transactions)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        df = spending_by_category(df, "Супермаркеты", "2021-12-31 17:00:00")
        logger.debug(f"Результат spending_by_category: {df.to_dict()}")
    except Exception as e:
        logger.error(f"Ошибка в main: {str(e)}")
        raise


if __name__ == "__main__":
    main()
