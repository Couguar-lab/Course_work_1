import json
from unittest.mock import patch

import pandas as pd

from src.utils import load_settings, load_transactions


def test_load_transactions(tmp_path):
    file = tmp_path / "test.xlsx"
    df = pd.DataFrame(
        [
            {
                "Дата операции": "31.12.2021 16:44:00",
                "Дата платежа": "31.12.2021",
                "Номер карты": "*7197",
                "Статус": "OK",
                "Сумма операции": "-160,89",
                "Валюта операции": "RUB",
                "Сумма платежа": "-160,89",
                "Валюта платежа": "RUB",
                "Кэшбэк": "",
                "Категория": "Супермаркеты",
                "MCC": "5411",
                "Описание": "Колхоз",
                "Бонусы (включая кэшбэк)": "3,00",
                "Округление на инвесткопилку": "0,00",
                "Сумма операции с округлением": "160,89",
            }
        ]
    )
    df.to_excel(file, index=False, engine="openpyxl")
    result = load_transactions(str(file))
    assert len(result) == 1
    assert result[0]["Дата операции"] == "31.12.2021 16:44:00"
    assert result[0]["Сумма платежа"] == -160.89
    assert result[0]["Номер карты"] == "*7197"
    assert result[0]["Кэшбэк"] == 0.0


def test_load_settings(tmp_path):
    file = tmp_path / "settings.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump({"user_currencies": ["USD"], "user_stocks": ["AAPL"]}, f)
    result = load_settings(str(file))
    assert result == {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}


def test_load_settings_missing_file():
    with patch("os.path.exists", return_value=False):
        settings = load_settings()
        assert settings == {
            "user_currencies": ["USD", "EUR"],
            "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"],
        }
