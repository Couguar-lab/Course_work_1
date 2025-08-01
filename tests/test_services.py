from src.services import simple_search


def test_simple_search_found(sample_transactions_list):
    result = simple_search("Перевод", sample_transactions_list)
    assert len(result["transactions"]) == 1
    assert result["transactions"][0]["Описание"] == "Перевод"


def test_simple_search_empty_string(sample_transactions_list):
    result = simple_search("", sample_transactions_list)
    assert len(result["transactions"]) == 2


def test_simple_search_not_found(sample_transactions_list):
    result = simple_search("Одежда", sample_transactions_list)
    assert len(result["transactions"]) == 0
