# tests/test_views.py
import json

import pandas as pd
import pytest

from src.views import home_page


@pytest.fixture
def sample_excel(tmp_path):
    df = pd.DataFrame([
        {
            "Дата операции": "15.09.2023 10:20:30",
            "Номер карты": "*1234",
            "Сумма платежа": -2500.0,
            "Кэшбэк": 25.0,
            "Категория": "Супермаркеты",
            "Описание": "Пятёрочка",
        },
        {
            "Дата операции": "15.09.2023 18:45:12",
            "Номер карты": "*5678",
            "Сумма платежа": -8000.0,
            "Кэшбэк": 80.0,
            "Категория": "Рестораны",
            "Описание": "Вкусно и точка",
        },
        {
            "Дата операции": "10.09.2023 14:30:00",
            "Номер карты": "*1234",
            "Сумма платежа": -500.0,
            "Кэшбэк": 5.0,
            "Категория": "Кафе",
            "Описание": "Кофе",
        },
    ])
    path = tmp_path / "operations.xlsx"
    df.to_excel(path, index=False, engine="openpyxl")
    return str(path)


@pytest.mark.parametrize(
    "date_str, expected_greeting, expected_min_cards, expected_min_top",
    [
        ("2023-09-20 12:00:00", "Добрый день", 2, 3),
        ("2023-09-15 07:00:00", "Доброе утро", 1, 1),
        ("2023-09-15 23:59:59", "Добрый вечер", 2, 3),
        ("2023-09-01 03:00:00", "Доброй ночи", 0, 0),
    ],
)
def test_home_page(monkeypatch, sample_excel, date_str, expected_greeting, expected_min_cards, expected_min_top):
    def mock_load_transactions(filepath):
        return pd.read_excel(sample_excel).to_dict("records")

    monkeypatch.setattr("src.views.load_transactions", mock_load_transactions)
    monkeypatch.setattr("src.views.get_currency_rates", lambda *a, **kw: [{"currency": "USD", "rate": 96.0}])
    monkeypatch.setattr("src.views.get_stock_prices", lambda *a, **kw: [{"stock": "AAPL", "price": 175.0}])

    result_json = home_page(date_str)

    assert isinstance(result_json, str), "home_page должен возвращать JSON-строку!"
    data = json.loads(result_json)

    assert data["greeting"] == expected_greeting
    assert len(data["cards"]) >= expected_min_cards
    assert len(data["top_transactions"]) >= expected_min_top
    assert len(data["currency_rates"]) >= 1
    assert len(data["stock_prices"]) >= 1
