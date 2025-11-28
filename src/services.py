# src/services.py
import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def simple_search(search: str, transactions: List[Dict[str, Any]]) -> str:
    """Возвращает JSON-строку с найденными транзакциями."""
    logger.debug(f"Поиск по строке: {search}")
    try:
        if not search:
            logger.info("Пустая строка поиска — возвращаем все транзакции")
            result = {"transactions": transactions}
            return json.dumps(result, ensure_ascii=False, indent=2)

        filtered = [
            t for t in transactions
            if search.lower() in str(t.get("Описание", "")).lower()
            or search.lower() in str(t.get("Категория", "")).lower()
        ]
        logger.info(f"Найдено {len(filtered)} транзакций")
        result = {"transactions": filtered}
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка в simple_search: {str(e)}")
        return json.dumps({"transactions": []}, ensure_ascii=False)
