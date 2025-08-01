import json
import logging
import os
from typing import Any, Dict, List

import pandas as pd

# Глобальная настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    filename="logs/all.log",  # Единый лог-файл
    encoding="utf-8",
    force=True,
)
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """Читает транзакции из Excel/JSON/CSV файла."""
    logger.debug(f"Попытка чтения файла: {file_path}")
    try:
        # Исправляем путь, если file_path указывает на data/operations.xlsx
        if file_path == "data/operations.xlsx":
            file_path = os.path.join(os.path.dirname(__file__), "..", "data", "operations.xlsx")
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            raise FileNotFoundError(f"Файл {file_path} не существует")
        # Остальной код без изменений
        if file_path.endswith(".xlsx"):
            try:
                df = pd.read_excel(file_path, engine="openpyxl")
                logger.debug(f"Файл успешно прочитан. Столбцы: {df.columns.tolist()}")
            except UnicodeDecodeError:
                logger.warning("Ошибка кодировки при чтении Excel, пробуем альтернативный подход")
                with open(file_path, "rb") as f:
                    df = pd.read_excel(f, engine="openpyxl")
            except Exception as e:
                logger.error(f"Не удалось прочитать Excel: {str(e)}")
                raise
        elif file_path.endswith(".csv"):
            encodings = ["utf-8", "cp1251", "latin1"]
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.debug(f"CSV прочитан с кодировкой: {encoding}")
                    break
                except UnicodeDecodeError:
                    logger.debug(f"Кодировка {encoding} не подошла, пробуем следующую")
            if df is None:
                raise ValueError("Не удалось определить кодировку для CSV")
        elif file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                df = pd.DataFrame(data)
        else:
            raise ValueError("Неподдерживаемый формат файла")

        column_mapping = {
            "Дата операции": "Дата операции",
            "Номер карты": "Номер карты",
            "Сумма платежа": "Сумма платежа",
            "Кэшбэк": "Кэшбэк",
            "Категория": "Категория",
            "Описание": "Описание",
        }
        df = df.rename(columns=lambda x: column_mapping.get(x, x))

        for col in ["Сумма платежа", "Кэшбэк"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(",", ".").replace("nan", "0").astype(float)
                logger.debug(f"Преобразован столбец {col}: {df[col].head().to_list()}")

        required_columns = ["Дата операции", "Номер карты", "Сумма платежа", "Кэшбэк", "Категория", "Описание"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Отсутствуют столбцы: {missing_columns}. Заполняем значениями по умолчанию.")
            for col in missing_columns:
                df[col] = None

        logger.info(f"Прочитано {len(df)} транзакций из {file_path}")
        return df.to_dict("records")
    except Exception as e:
        logger.error(f"Ошибка при чтении файла {file_path}: {str(e)}")
        return []


def load_settings(file_path: str = "user_settings.json") -> Dict[str, Any]:
    """Загружает пользовательские настройки из JSON."""
    logger.debug(f"Чтение настроек из {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        logger.info("Настройки успешно загружены")
        return settings
    except FileNotFoundError:
        logger.warning(f"Файл настроек {file_path} не найден, используются настройки по умолчанию")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}
    except Exception as e:
        logger.error(f"Ошибка при загрузке настроек: {str(e)}")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}
