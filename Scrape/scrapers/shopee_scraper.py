# scrapers/shopee_scraper_template.py
# Ini adalah templat untuk membuat scraper baru, contoh untuk Shopee.
# Cukup salin file ini, ganti nama kelas, dan isi bagian yang ditandai #TODO.

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from .base_scraper import BaseScraper
from utils.data_cleaner import clean_price, clean_sold_count
import datetime

class ShopeeScraper(BaseScraper): # Ganti nama kelas
    """
    Scraper spesifik untuk Shopee.
    """
    def _get_url(self, search_query, page):
        """Membuat URL pencarian untuk Shopee."""
        # TODO: Ganti dengan format URL pencarian Shopee yang benar.
        search_query_formatted = search_query.replace(" ", "%20")
        # Halaman di Shopee seringkali menggunakan 'page=0' untuk halaman pertama.
        return f"https://shopee.co.id/search?keyword={search_query_formatted}&page={page-1}"

    def _find_product_cards(self):
        """Mencari kartu produk di Shopee."""
        # TODO: Ganti dengan selector CSS untuk kartu produk di Shopee.
        # Anda perlu melakukan inspeksi elemen (inspect element) di halaman Shopee untuk menemukannya.
        # Contoh selector (mungkin perlu diubah):
        selector = 'div[data-sqe="item"]'
        try:
            cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if cards:
                self.logger.info(f"Ditemukan {len(cards)} kartu produk dengan selector '{selector}'")
                return cards
        except NoSuchElementException:
            pass
        self.logger.warning("Tidak ada kartu produk yang ditemukan.")
        return []

    def _extract_product_data(self, card):
        """Mengekstrak data dari satu kartu produk Shopee."""
        
        # TODO: Ganti semua selector di bawah ini dengan yang sesuai untuk Shopee.
        # Ini adalah bagian terpenting yang membutuhkan penyesuaian.
        
        try:
            # Selector untuk nama produk di Shopee
            name_element = card.find_element(By.CSS_SELECTOR, 'div[data-sqe="name"] > div')
            product_name = name_element.text
        except NoSuchElementException:
            return None

        try:
            # Selector untuk harga di Shopee
            price_element = card.find_element(By.CSS_SELECTOR, 'div._3_NTr6 span.ZEgDH9')
            price_text = price_element.text
        except NoSuchElementException:
            price_text = "0"
            
        try:
            # Selector untuk lokasi di Shopee
            location_element = card.find_element(By.CSS_SELECTOR, 'div._1_U22_')
            location = location_element.text
        except NoSuchElementException:
            location = "Lokasi tidak tersedia"

        try:
            # Selector untuk jumlah terjual di Shopee
            sold_element = card.find_element(By.CSS_SELECTOR, 'div.z-ve1m')
            sold_text = sold_element.text
        except NoSuchElementException:
            sold_text = "0 terjual"
            
        try:
            # URL biasanya ada di tag <a> pembungkus
            url_element = card.find_element(By.CSS_SELECTOR, 'a')
            product_url = url_element.get_attribute('href')
        except NoSuchElementException:
            product_url = "URL tidak tersedia"

        return {
            "timestamp_scrape": datetime.datetime.now().isoformat(),
            "ecommerce": "Shopee",
            "product_name": product_name,
            "price_raw": price_text,
            "price_clean": clean_price(price_text),
            "shop_name": "N/A on card", # Nama toko sering tidak ada di kartu produk utama Shopee
            "location": location,
            "sold_count_raw": sold_text,
            "sold_count_clean": clean_sold_count(sold_text),
            "product_url": product_url
        }
