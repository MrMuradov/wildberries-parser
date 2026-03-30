"""Конфигурация парсера."""

SEARCH_QUERY = "пальто из натуральной шерсти"

FILTER_RATING_MIN = 4.5
FILTER_PRICE_MAX = 10000
FILTER_COUNTRY = "Россия"

WB_SEARCH_URL = "https://search.wb.ru/exactmatch/ru/common/v4/search"
WB_CATALOG_URL = "https://catalog.wb.ru/catalog/{category}/catalog"
WB_CARD_URL = "https://card.wb.ru/cards/detail"

REQUEST_DELAY = 1.0
MAX_RETRIES = 3
TIMEOUT = 30

OUTPUT_DIR = "output"
FULL_CATALOG_FILE = "full_catalog.xlsx"
FILTERED_CATALOG_FILE = "filtered_catalog.xlsx"
