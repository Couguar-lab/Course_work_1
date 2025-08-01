import pandas as pd

from src.reports import spending_by_category


def test_spending_by_category():
    # Создаём DataFrame с преобразованием даты
    sample_transactions = pd.DataFrame(
        {
            "Дата операции": ["05.09.2023 11:30:32", "06.09.2023 12:00:00"],
            "Номер карты": ["1234567...0", "1234567890127512"],
            "Сумма платежа": [10.0, -500.0],
            "Кэшбэк": [0.0, 5.0],
            "Категория": ["Супермаркеты", "Переводы"],
            "Описание": ["Лента", "Перевод"],
        }
    )
    sample_transactions["Дата операции"] = pd.to_datetime(
        sample_transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    )

    # Устанавливаем дату, включающую первую транзакцию
    result = spending_by_category(sample_transactions, "Супермаркеты", "2023-09-05 11:30:32")
    assert len(result) == 1  # Ожидаем одну транзакцию до 05.09.2023 12:00:00
    assert result["Категория"].iloc[0] == "Супермаркеты"
    assert result["Дата операции"].iloc[0].strftime("%d.%m.%Y %H:%M:%S") == "05.09.2023 11:30:32"


def test_spending_by_category_error():
    df = pd.DataFrame({"Категория": ["Супермаркеты"], "Дата операции": ["invalid_date"]})
    result = spending_by_category(df, "Супермаркеты", "2023-09-06 12:00:00")
    assert len(result) == 0
