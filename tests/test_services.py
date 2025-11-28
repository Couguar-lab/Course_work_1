import json

import pytest

from src.services import simple_search


@pytest.mark.parametrize(
    "search_term, expected_len, expected_desc",
    [
        ("Перевод", 1, "Перевод"),
        ("лента", 1, "Лента"),
        ("", 2, None),
        ("одежда", 0, None),
    ],
)
def test_simple_search(sample_transactions_list, search_term, expected_len, expected_desc):
    result_json = simple_search(search_term, sample_transactions_list)
    result = json.loads(result_json)
    assert len(result["transactions"]) == expected_len
    if expected_desc is not None:
        assert any(t["Описание"] == expected_desc for t in result["transactions"])
