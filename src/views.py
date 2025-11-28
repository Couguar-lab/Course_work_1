# src/views.py
import json
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
    elif 17 <= hour < 24:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_currency_rates(currencies: List[str], api_key: str) -> List[Dict[str, Any]]:
    """Получает курсы валют из API."""
    logger.debug(f"Запрос курсов валют: {currencies}")
    rates = []
    if not api_key:
        logger.error("API-ключ для курсов валют отсутствует")
        return [{"currency": c, "rate": 0.0} for c in currencies]
    try:
        response = requests.get(f"https://api.exchangerate-api.com/v4/latest/RUB?apiKey={api_key}")
        response.raise_for_status()
        data = response.json().get("rates", {})
        for currency in currencies:
            rate = data.get(currency, 0.0)
            rates.append({"currency": currency, "rate": round(float(rate), 4)})
        logger.info(f"Курсы валют получены: {rates}")
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {str(e)}")
        rates = [{"currency": c, "rate": 0.0} for c in currencies]
    return rates


def get_stock_prices(stocks: List[str], api_key: str) -> List[Dict[str, Any]]:
    """Получает цены акций из API Finnhub."""
    logger.debug(f"Запрос цен акций: {stocks}")
    prices = []
    if not api_key:
        logger.error("API-ключ для акций отсутствует")
        return [{"stock": s, "price": 0.0} for s in stocks]
    try:
        for stock in stocks:
            response = requests.get(f"https://finnhub.io/api/v1/quote?symbol={stock}&token={api_key}")
            response.raise_for_status()
            price = response.json().get("c", 0.0)
            prices.append({"stock": stock, "price": round(float(price), 2)})
        logger.info(f"Цены акций получены: {prices}")
    except Exception as e:
        logger.error(f"Ошибка при получении цен акций: {str(e)}")
        prices = [{"stock": s, "price": 0.0} for s in stocks]
    return prices


def home_page(date_time: str) -> str:
    """
    Главная страница: возвращает JSON-строку с приветствием, картами,
    топ-5 тратами, курсами валют и ценами акций за текущий месяц до указанной даты.
    """
    logger.debug(f"Генерация главной страницы для даты: {date_time}")
    try:
        # Парсим дату
        dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        start_date = dt.replace(day=1, hour=0, minute=0, second=0)
        logger.debug(f"Период анализа: {start_date} — {dt}")

        # Загружаем транзакции
        transactions = load_transactions("data/operations.xlsx")
        if not transactions:
            raise ValueError("Файл с транзакциями не найден или пуст")

        df = pd.DataFrame(transactions)

        # Преобразуем дату операции
        if df["Дата операции"].dtype == "object":
            df["Дата операции"] = pd.to_datetime(
                df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
            )

        # Фильтруем по периоду
        df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= dt)]

        # Информация по картам
        cards_info = []
        if not df.empty:
            cards = (
                df.groupby("Номер карты")
                .agg({"Сумма платежа": "sum", "Кэшбэк": "sum"})
                .reset_index()
            )
            for _, row in cards.iterrows():
                if pd.notna(row["Номер карты"]) and row["Сумма платежа"] < 0:
                    cards_info.append({
                        "last_digits": str(row["Номер карты"])[-4:],
                        "total_spent": round(abs(float(row["Сумма платежа"])), 2),
                        "cashback": round(float(row["Кэшбэк"]), 2),
                    })

        # Топ-5 трат
        top_transactions_info = []
        if not df.empty:
            top_df = df[df["Сумма платежа"] < 0].nlargest(5, "Сумма платежа")[
                ["Дата операции", "Сумма платежа", "Категория", "Описание"]
            ]
            for _, row in top_df.iterrows():
                top_transactions_info.append({
                    "date": row["Дата операции"].strftime("%d.%m.%Y") if pd.notna(row["Дата операции"]) else "",
                    "amount": round(abs(float(row["Сумма платежа"])), 2),
                    "category": str(row["Категория"]) if pd.notna(row["Категория"]) else "",
                    "description": str(row["Описание"]) if pd.notna(row["Описание"]) else "",
                })

        # Настройки пользователя
        settings = load_settings()
        currencies = settings.get("user_currencies", ["USD", "EUR"])
        stocks = settings.get("user_stocks", ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])

        api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        finnhub_key = os.getenv("FINNHUB_API_KEY")

        result = {
            "greeting": get_greeting(dt.hour),
            "cards": cards_info,
            "top_transactions": top_transactions_info,
            "currency_rates": get_currency_rates(currencies, api_key),
            "stock_prices": get_stock_prices(stocks, finnhub_key),
        }

        logger.info("Главная страница успешно сформирована")
        return json.dumps(result, ensure_ascii=False, indent=2, default=str)

    except Exception as e:
        logger.error(f"Критическая ошибка в home_page: {str(e)}", exc_info=True)
        error_response = {
            "greeting": "Ошибка",
            "cards": [],
            "top_transactions": [],
            "currency_rates": [],
            "stock_prices": [],
            "error": str(e),
        }
        return json.dumps(error_response, ensure_ascii=False, indent=2)
