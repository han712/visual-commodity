# scrapers/tokopedia_scraper.py

import datetime
from .base_scraper import BaseScraper
from utils.data_cleaner import clean_price, clean_sold_count
import re

class TokopediaScraper(BaseScraper):
    """
    Scraper spesifik untuk Tokopedia.
    """
    
    def _get_url(self, search_query, page):
        """Mendefinisikan format URL pencarian Tokopedia."""
        search_query_formatted = search_query.replace(" ", "%20")
        if page == 1:
            return f"https://www.tokopedia.com/search?st=&q={search_query_formatted}"
        else:
            return f"https://www.tokopedia.com/search?st=&q={search_query_formatted}&page={page}"

    def _get_defaults(self):
        """Nilai default jika data tidak ditemukan."""
        return {
            "product_name": "Nama produk tidak tersedia",
            "price": "Harga tidak tersedia",
            "shop_name": "Nama toko tidak tersedia",
            "location": "Lokasi tidak tersedia",
            "sold_count": "0 terjual",
            "product_url": "URL tidak tersedia"
        }

    def _get_initial_container_selectors(self):
        """Selector untuk container utama yang menandakan halaman telah dimuat."""
        return [
            'div[data-testid="divSRPContentProducts"]',
            '.css-jza1fo',
            '.css-5wh65g'
        ]

    def _get_card_selectors(self):
        """
        Daftar selector untuk menemukan setiap kartu produk.
        """
        return [
            '.css-jza1fo',    # Main selector
            '.css-5wh65g',    # Alternative selector
            'div[data-testid="divProductWrapper"]',
            'div[data-testid="divSRPContentProducts"] > div > div'
        ]
        
    def _get_name_selectors(self):
        """Daftar selector untuk nama produk """
        return [
            'span[class*="_0T8-iGxMpV6NEsYEhwkqEg"]',
            'span[class*="0T8-iGxMpV6NEsYEhwkqEg"]',
            'div > div > div > span',
            'span[data-testid="spnSRPProdName"]',
            '.prd_link-product-name',
            'div > a > div > div > div > span'
        ]

    def _get_price_selectors(self):
        """Daftar selector untuk harga produk """
        return [
            'div[class*="_67d6E1xDKIzw"]',
            'div[class*="67d6E1xDKIzw"]',
            'div[class*="t4jWW3NandT5hvCFAiotYg"]',
            'span[data-testid="spnSRPProdPrice"]',
            'div[class*="price"]'
        ]

    def _get_shop_selectors(self):
        """Daftar selector untuk nama toko"""
        return [
            'span[class*="T0rpy-LEwYNQifsgB-3SQw"]',
            'span[class*="pC8DMVkBZGW7-egObcWMFQ"]',
            'span[data-testid="spnSRPProdSellerName"]',
            'span[class*="shop"]'
        ]
        
    def _get_location_selectors(self):
        """Daftar selector untuk lokasi toko."""
        return [
            'span[class*="pC8DMVkBZGW7-egObcWMFQ"]:last-child',
            'span[data-testid="spnSRPProdTabShopLoc"]'
        ]

    def _get_sold_count_selectors(self):
        """Daftar selector untuk jumlah produk terjual."""
        return [
            'span[class*="se8WAnkjbVXZNA8mT+Veuw"]',
            'span[class*="se8WAnkjbVXZNA8mT"]',
            'span[class*="sold"]',
            'div > div > span:contains("terjual")'
        ]

    def _get_url_selectors(self):
        """Daftar selector untuk URL produk."""
        return ['a']

    def _extract_product_data(self, card):
        """
        Mengekstrak semua data dari satu kartu produk.
        """
        defaults = self._get_defaults()

        try:
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
            import time
            time.sleep(0.5)
        except:
            pass

        # Ekstraksi nama produk 
        name = self._extract_text_with_fallback(card, self._get_name_selectors(), defaults["product_name"])
        
        # Ekstraksi harga 
        price_raw = self._extract_price_with_fallback(card, self._get_price_selectors(), defaults["price"])
        
        # Ekstraksi data lainnya
        shop = self._extract_text_with_fallback(card, self._get_shop_selectors(), defaults["shop_name"])
        location = self._extract_text_with_fallback(card, self._get_location_selectors(), defaults["location"])
        
        # Ekstraksi sold count
        sold_raw = self._extract_sold_count_with_fallback(card, self._get_sold_count_selectors(), defaults["sold_count"])
        
        # URL extraction
        url = card.get_attribute('href') or self._extract_attribute_with_fallback(card, 'a', 'href', defaults["product_url"])
        
        # Hanya return data jika nama produk berhasil diekstrak
        if name == defaults["product_name"]:
            return None

        return {
            "timestamp_scrape": datetime.datetime.now().isoformat(),
            "ecommerce": "Tokopedia",
            "product_name": name,
            "price_raw": price_raw,
            "price_clean": clean_price(price_raw),
            "shop_name": shop,
            "location": location,
            "sold_count_raw": sold_raw,
            "sold_count_clean": clean_sold_count(sold_raw),
            "product_url": url
        }

    def _extract_text_with_fallback(self, parent_element, selectors, default_text):
        """
        Implementasi extract_element_text .
        """
        # Coba selector normal dulu
        for selector in selectors:
            try:
                element = parent_element.find_element(self.By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    return text
            except:
                continue
        
        return default_text

    def _extract_price_with_fallback(self, parent_element, selectors, default_text):
        """
        Implementasi khusus untuk harga.
        """
        # Coba selector normal dulu
        for selector in selectors:
            try:
                element = parent_element.find_element(self.By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    return text
            except:
                continue
        
        # Fallback: cari semua div dan span yang mengandung "Rp"
        try:
            elements = parent_element.find_elements(self.By.CSS_SELECTOR, "div, span")
            for element in elements:
                text = element.text.strip()
                if text and "Rp" in text:
                    # Gunakan regex untuk ekstrak bagian harga saja
                    price_match = re.search(r'Rp[\d.,]+', text)
                    if price_match:
                        return price_match.group(0)
                    return text
        except:
            pass
        
        return default_text

    def _extract_sold_count_with_fallback(self, parent_element, selectors, default_text):
        """
        Implementasi khusus untuk sold count.
        """
        # Coba selector normal dulu
        for selector in selectors:
            try:
                element = parent_element.find_element(self.By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    return text
            except:
                continue
        
        # Fallback: cari semua div dan span yang mengandung "terjual"
        try:
            elements = parent_element.find_elements(self.By.CSS_SELECTOR, "div, span")
            for element in elements:
                text = element.text.strip()
                if text and "terjual" in text:
                    return text
        except:
            pass
        
        return default_text

    def _extract_attribute_with_fallback(self, parent_element, selector, attribute_name, default_value):
        """
        Implementasi extract_attribute.
        """
        try:
            element = parent_element.find_element(self.By.CSS_SELECTOR, selector)
            value = element.get_attribute(attribute_name)
            if value:
                return value
        except:
            pass
        
        # Fallback: cari semua anchor tag
        try:
            elements = parent_element.find_elements(self.By.TAG_NAME, "a")
            for element in elements:
                value = element.get_attribute(attribute_name)
                if value:
                    return value
        except:
            pass
        
        return default_value