import logging
from typing import Any, Dict, List

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s", filename="logs/services.log")
logger = logging.getLogger(__name__)


def simple_search(search: str, transactions: List[Dict[str, Any]]) -> dict:
    """Возвращает JSON с транзакциями, где в описании или категории есть строка поиска."""
    logger.debug(f"Поиск по строке: {search}")
    try:
        if not search:
            logger.info("Пустая строка поиска, возвращаем все транзакции")
            return {"transactions": transactions}

        filtered = [
            t
            for t in transactions
            if search.lower() in str(t.get("Описание", "")).lower()
            or search.lower() in str(t.get("Категория", "")).lower()
        ]
        logger.info(f"Найдено {len(filtered)} транзакций")
        return {"transactions": filtered}
    except Exception as e:
        logger.error(f"Ошибка в simple_search: {str(e)}")
        return {"transactions": []}
