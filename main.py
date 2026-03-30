"""Главный скрипт парсера."""

import os
from src.parser import WildberriesParser
from src.excel_writer import ExcelWriter
from src.config import (
    SEARCH_QUERY,
    OUTPUT_DIR,
    FULL_CATALOG_FILE,
    FILTERED_CATALOG_FILE,
    FILTER_RATING_MIN,
    FILTER_PRICE_MAX,
    FILTER_COUNTRY
)


def main():
    """Основная функция."""
    print("=" * 70)
    print("ПАРСЕР WILDBERRIES")
    print("=" * 70)

    parser = WildberriesParser()

    try:
        print(f"\n1. Парсинг каталога по запросу: '{SEARCH_QUERY}'")
        print("-" * 70)
        products = parser.parse_catalog(SEARCH_QUERY)

        if not products:
            print("\n❌ Товары не найдены")
            return

        print(f"\n2. Сохранение полного каталога")
        print("-" * 70)
        full_catalog_path = os.path.join(OUTPUT_DIR, FULL_CATALOG_FILE)
        ExcelWriter.write_catalog(products, full_catalog_path)

        print(f"\n3. Фильтрация товаров")
        print("-" * 70)
        filtered_products = parser.filter_products(
            products,
            min_rating=FILTER_RATING_MIN,
            max_price=FILTER_PRICE_MAX,
            country=FILTER_COUNTRY
        )

        print(f"\n4. Сохранение отфильтрованного каталога")
        print("-" * 70)
        filtered_catalog_path = os.path.join(OUTPUT_DIR, FILTERED_CATALOG_FILE)
        ExcelWriter.write_catalog(filtered_products, filtered_catalog_path)

        print("\n" + "=" * 70)
        print("✅ ПАРСИНГ ЗАВЕРШЁН")
        print("=" * 70)
        print(f"Всего товаров: {len(products)}")
        print(f"После фильтрации: {len(filtered_products)}")
        print(f"\nФайлы:")
        print(f"  - {full_catalog_path}")
        print(f"  - {filtered_catalog_path}")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

    finally:
        parser.close()


if __name__ == "__main__":
    main()