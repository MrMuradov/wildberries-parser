"""HTTP клиент для работы с Wildberries API."""

import time
import requests
from typing import Optional, Dict, Any
from fake_useragent import UserAgent

from src.config import REQUEST_DELAY, MAX_RETRIES, TIMEOUT


class WildberriesAPIClient:
    """Клиент для взаимодействия с API Wildberries."""

    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.last_request_time = 0

    def _get_headers(self) -> Dict[str, str]:
        """Генерирует headers как у обычного браузера."""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://www.wildberries.ru',
            'Referer': 'https://www.wildberries.ru/',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site'
        }

    def _rate_limit(self):
        """Rate limiting между запросами."""
        elapsed = time.time() - self.last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()

    def get(self, url: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Выполняет GET запрос с retry логикой.
        """
        self._rate_limit()

        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=TIMEOUT
                )

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                print(f"Попытка {attempt + 1}/{MAX_RETRIES} failed: {e}")

                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                else:
                    print(f"Все попытки исчерпаны для {url}")
                    return None

    def close(self):
        """Закрывает session."""
        self.session.close()