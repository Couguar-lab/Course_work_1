import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

from src.utils import load_settings, load_transactions

logger = logging.getLogger(__name__)

load_dotenv()


def get_greeting(hour: int) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    logger.debug(f"Определение приветствия для часа: {hour}")
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 22:
        return "Добрый вечер"
    return "Доброй ночи"


def get_currency_rates(currencies: List[str], api_key: str) -> List[Dict[str, Any]]:
    """Получает курсы валют из API."""
    logger.debug(f"Запрос курсов валют: {currencies}")
    rates = []
    if not api_key:
        logger.error("API-ключ для курсов валют отсутствует")
        return [{"currency": c, "rate": 0} for c in currencies]
    try:
        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/RUB?apiKey={api_key}")
        response.raise_for_status()
        data = response.json().get("rates", {})
        for currency in currencies:
            rate = data.get(currency, 0)
            rates.append({"currency": currency, "rate": round(rate, 4) if rate else 0})
        logger.info(f"Курсы валют получены: {rates}")
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {str(e)}")
        rates = [{"currency": c, "rate": 0} for c in currencies]
    return rates


def get_stock_prices(stocks: List[str], api_key: str) -> List[Dict[str, Any]]:
    """Получает цены акций из API."""
    logger.debug(f"Запрос цен акций: {stocks}")
    prices = []
    if not api_key:
        logger.error("API-ключ для цен акций отсутствует")
        return [{"stock": s, "price": 0} for s in stocks]
    try:
        for stock in stocks:
            response = requests.get(f"https://finnhub.io/api/v1/quote?symbol={stock}&token={api_key}")
            response.raise_for_status()
            price = response.json().get("c", 0)
            prices.append({"stock": stock, "price": round(price, 2)})
        logger.info(f"Цены акций получены: {prices}")
    except Exception as e:
        logger.error(f"Ошибка при получении цен акций: {str(e)}")
        prices = [{"stock": s, "price": 0} for s in stocks]
    return prices


def home_page(date_time: str) -> dict:
    logger.debug(f"Генерация страницы 'Главная' для даты: {date_time}")
    try:
        dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        start_date = dt.replace(day=1, hour=0, minute=0, second=0)
        logger.debug(f"Диапазон анализа: {start_date} - {dt}")

        transactions = load_transactions("data/operations.xlsx")
        logger.debug(f"Загружено транзакций: {len(transactions)}")
        logger.debug(f"Содержимое transactions: {transactions}")
        if not transactions:
            logger.error("Не удалось загрузить транзакции")
            return {}

        df = pd.DataFrame(transactions)
        logger.debug(f"Тип данных 'Дата операции': {df['Дата операции'].dtype}")
        if df["Дата операции"].dtype == "object":
            df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
            if df["Дата операции"].isna().any():
                logger.warning("Некоторые даты в 'Дата операции' не удалось распознать, заполнены как NaT")

        df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= dt)]
        logger.debug(f"Отфильтровано транзакций: {len(df)}")
        if df.empty:
            logger.warning("Нет транзакций за указанный период")
            settings = load_settings()
            currencies = settings.get("user_currencies", ["USD", "EUR"])
            stocks = settings.get("user_stocks", ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])
            api_key = os.getenv("EXCHANGE_RATE_API_KEY")
            finnhub_key = os.getenv("FINNHUB_API_KEY")
            return {
                "greeting": get_greeting(dt.hour),
                "cards": [],
                "top_transactions": [],
                "currency_rates": get_currency_rates(currencies, api_key),
                "stock_prices": get_stock_prices(stocks, finnhub_key),
            }

        cards = df.groupby("Номер карты").agg({"Сумма платежа": "sum", "Кэшбэк": "sum"}).reset_index()
        logger.debug(f"Группировка по картам: {cards.to_dict()}")
        cards_info = [
            {
                "last_digits": str(row["Номер карты"])[-4:] if pd.notna(row["Номер карты"]) else "0000",
                "total_spent": round(float(row["Сумма платежа"]) if pd.notna(row["Сумма платежа"]) else 0, 2),
                "cashback": round(float(row["Кэшбэк"]) if pd.notna(row["Кэшбэк"]) else 0, 2),
            }
            for _, row in cards.iterrows()
            if pd.notna(row["Сумма платежа"]) and row["Сумма платежа"] < 0
        ]
        logger.debug(f"cards_info: {cards_info}")

        top_transactions = df[df["Сумма платежа"] < 0].nlargest(5, "Сумма платежа")[
            ["Дата операции", "Сумма платежа", "Категория", "Описание"]
        ]
        top_transactions_info = [
            {
                "date": row["Дата операции"].strftime("%d.%m.%Y") if pd.notna(row["Дата операции"]) else "01.01.1970",
                "amount": round(float(row["Сумма платежа"]) if pd.notna(row["Сумма платежа"]) else 0, 2),
                "category": str(row["Категория"]) if pd.notna(row["Категория"]) else "Неизвестно",
                "description": str(row["Описание"]) if pd.notna(row["Описание"]) else "Нет данных",
            }
            for _, row in top_transactions.iterrows()
        ]

        settings = load_settings()
        currencies = settings.get("user_currencies", ["USD", "EUR"])
        stocks = settings.get("user_stocks", ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])

        api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        finnhub_key = os.getenv("FINNHUB_API_KEY")
        currency_rates = get_currency_rates(currencies, api_key)
        stock_prices = get_stock_prices(stocks, finnhub_key)

        result = {
            "greeting": get_greeting(dt.hour),
            "cards": cards_info,
            "top_transactions": top_transactions_info,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }
        logger.info("JSON-ответ для страницы 'Главная' сформирован")
        return result
    except Exception as e:
        logger.error(f"Ошибка в home_page: {str(e)}")
        return {}
