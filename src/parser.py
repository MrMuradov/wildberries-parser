"""Основной парсер Wildberries."""

from typing import List, Dict, Any
from urllib.parse import urlencode

from src.api_client import WildberriesAPIClient
from src.config import WB_SEARCH_URL, WB_CARD_URL


class WildberriesParser:
    """Парсер каталога Wildberries."""

    def __init__(self):
        self.client = WildberriesAPIClient()
        self.products = []

    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """
        Ищет товары по поисковому запросу.
        """
        print(f"Ищем товары по запросу: '{query}'")

        page = 1
        all_products = []

        while True:
            print(f"Загружаем страницу {page}...")

            params = {
                'appType': '1',
                'curr': 'rub',
                'dest': '-1257786',
                'query': query,
                'page': page,
                'resultset': 'catalog',
                'sort': 'popular',
                'spp': '30',
                'suppressSpellcheck': 'false'
            }

            data = self.client.get(WB_SEARCH_URL, params=params)

            if not data or 'data' not in data or 'products' not in data['data']:
                print("Больше товаров нет")
                break

            products = data['data']['products']

            if not products:
                break

            all_products.extend(products)
            print(f"Найдено {len(products)} товаров на странице {page}")

            page += 1

            if page > 100:
                break

        print(f"Всего найдено {len(all_products)} товаров")
        return all_products

    def get_product_details(self, product_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Получает детальную информацию о товарах.
        """
        print(f"Получаем детальную информацию о {len(product_ids)} товарах...")

        chunk_size = 100
        all_details = []

        for i in range(0, len(product_ids), chunk_size):
            chunk = product_ids[i:i + chunk_size]

            params = {
                'appType': '1',
                'curr': 'rub',
                'dest': '-1257786',
                'spp': '30',
                'nm': ';'.join(map(str, chunk))
            }

            data = self.client.get(WB_CARD_URL, params=params)

            if data and 'data' in data and 'products' in data['data']:
                all_details.extend(data['data']['products'])
                print(f"Загружено {len(all_details)}/{len(product_ids)} товаров")

        return all_details

    def parse_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсит информацию о товаре в нужный формат.
        """
        product_id = product.get('id', '')

        product_url = f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx"

        article = product.get('id', '')

        name = product.get('name', '')

        # Цена (в копейках, переводим в рубли)
        price_data = product.get('salePriceU', 0) or product.get('priceU', 0)
        price = price_data / 100 if price_data else 0

        description = product.get('description', '')

        images = []
        if 'pics' in product and product['pics']:
            vol = str(product_id)[:4]
            part = str(product_id)[:6]
            for pic in range(1, product['pics'] + 1):
                img_url = f"https://basket-{vol[:2]}.wb.ru/vol{vol}/part{part}/{product_id}/images/big/{pic}.jpg"
                images.append(img_url)

        images_str = ', '.join(images)

        characteristics = {}
        if 'options' in product:
            for option in product['options']:
                char_name = option.get('name', '')
                char_value = option.get('value', '')
                if char_name and char_value:
                    characteristics[char_name] = char_value

        chars_str = '; '.join([f"{k}: {v}" for k, v in characteristics.items()])

        country = characteristics.get('Страна производства', '')

        # Селлер
        seller_name = product.get('supplier', '') or product.get('brand', '')
        seller_id = product.get('supplierId', '')
        seller_url = f"https://www.wildberries.ru/seller/{seller_id}" if seller_id else ''

        sizes = []
        if 'sizes' in product:
            for size in product['sizes']:
                size_name = size.get('name', '')
                if size_name:
                    sizes.append(size_name)
        sizes_str = ', '.join(sizes)

        stock = 0
        if 'sizes' in product:
            for size in product['sizes']:
                if 'stocks' in size:
                    for warehouse in size['stocks']:
                        stock += warehouse.get('qty', 0)

        rating = product.get('rating', 0)

        reviews_count = product.get('feedbacks', 0)

        return {
            'Ссылка на товар': product_url,
            'Артикул': article,
            'Название': name,
            'Цена': price,
            'Описание': description,
            'Ссылки на изображения': images_str,
            'Характеристики': chars_str,
            'Страна производства': country,
            'Название селлера': seller_name,
            'Ссылка на селлера': seller_url,
            'Размеры': sizes_str,
            'Остатки': stock,
            'Рейтинг': rating,
            'Количество отзывов': reviews_count
        }

    def parse_catalog(self, query: str) -> List[Dict[str, Any]]:
        """
        Парсит полный каталог по запросу.
        """
        search_results = self.search_products(query)

        if not search_results:
            print("Товары не найдены")
            return []

        # Получаем ID товаров
        product_ids = [p['id'] for p in search_results]

        detailed_products = self.get_product_details(product_ids)

        # Парсим каждый товар
        parsed_products = []
        for product in detailed_products:
            try:
                parsed = self.parse_product(product)
                parsed_products.append(parsed)
            except Exception as e:
                print(f"Ошибка при парсинге товара {product.get('id')}: {e}")
                continue

        self.products = parsed_products
        return parsed_products

    def filter_products(
            self,
            products: List[Dict[str, Any]],
            min_rating: float = 4.5,
            max_price: float = 10000,
            country: str = "Россия"
    ) -> List[Dict[str, Any]]:
        """
        Фильтрует товары по критериям.
        """
        print(f"\nФильтруем товары:")
        print(f"  - Рейтинг >= {min_rating}")
        print(f"  - Цена <= {max_price} руб")
        print(f"  - Страна: {country}")

        filtered = []

        for product in products:
            rating = product.get('Рейтинг', 0)
            if rating < min_rating:
                continue

            price = product.get('Цена', 0)
            if price > max_price:
                continue

            product_country = product.get('Страна производства', '')
            if country.lower() not in product_country.lower():
                continue

            filtered.append(product)

        print(f"После фильтрации осталось {len(filtered)} товаров")
        return filtered

    def close(self):
        """Закрывает клиент."""
        self.client.close()