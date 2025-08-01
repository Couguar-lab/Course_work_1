import json
import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


def spending_by_category(df: pd.DataFrame, category: str, date_time: str = None) -> pd.DataFrame:
    """Генерирует отчет по тратам по категории."""
    logger.debug(f"Генерация отчета по категории: {category}, дата: {date_time}")
    try:
        if date_time:
            dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            start_date = dt.replace(day=1, hour=0, minute=0, second=0)
        else:
            dt = datetime.now()
            start_date = dt.replace(day=1, hour=0, minute=0, second=0)
        logger.debug(f"Диапазон: {start_date} - {dt}")

        # Преобразуем Дата операции в datetime, если это строка
        if df["Дата операции"].dtype == "object":
            df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")
            logger.debug("Преобразован столбец Дата операции в datetime")

        # Фильтрация данных
        filtered_df = df[df["Категория"] == category]
        if not filtered_df.empty and "Дата операции" in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df["Дата операции"] >= start_date) & (filtered_df["Дата операции"] <= dt)
            ]
        logger.info(f"Найдено {len(filtered_df)} транзакций для категории {category}")

        # Преобразуем Timestamp в строку для JSON-сериализации
        filtered_df_for_json = filtered_df.copy()
        if "Дата операции" in filtered_df_for_json.columns:
            filtered_df_for_json["Дата операции"] = filtered_df_for_json["Дата операции"].apply(
                lambda x: x.strftime("%d.%m.%Y %H:%M:%S") if pd.notna(x) else None
            )

        # Сохранение отчета
        report = filtered_df_for_json[["Дата операции", "Сумма платежа", "Категория", "Описание"]].to_dict()
        with open("report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
        logger.info("Отчет сохранён в report.json")

        return filtered_df
    except Exception as e:
        logger.error(f"Ошибка при генерации отчета: {str(e)}")
        return pd.DataFrame()
