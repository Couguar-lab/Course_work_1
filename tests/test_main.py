# tests/test_main.py
from unittest.mock import patch

import pandas as pd

from src.main import main


@patch("src.main.home_page")
@patch("src.main.spending_by_category")
def test_main(mock_spending, mock_home):
    mock_home.return_value = {"greeting": "Добрый день"}
    mock_spending.return_value = pd.DataFrame()
    with patch("logging.Logger.debug") as mock_logger:
        main()
        mock_logger.assert_any_call("Запуск программы")
