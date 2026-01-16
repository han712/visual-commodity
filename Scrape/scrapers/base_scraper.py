# scrapers/base_scraper.py

import time
import random
import os
import re
import datetime
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from utils.logger_setup import get_logger

class BaseScraper(ABC):
    """
    Kelas dasar abstrak.
    """
    def __init__(self, headless=True, debug_dir="debug_pic"):
        self.logger = get_logger(self.__class__.__name__)
        self.driver = self._setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 20)
        self.debug_dir = debug_dir
        # Import By untuk digunakan di subclass
        self.By = By
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)

    def _setup_driver(self, headless=True):
        """Mengkonfigurasi WebDriver"""
        self.logger.info("Menyiapkan Chrome WebDriver...")
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")  # Updated headless argument
        
        
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        
        # User agent 
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Opsi anti-deteksi
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.logger.warning(f"Falling back to default Chrome driver: {e}")
            driver = webdriver.Chrome(options=chrome_options)
        
        
        driver.set_page_load_timeout(30)
        return driver

    def scrape(self, search_query, max_products, max_pages):
        """Fungsi utama scraping dengan logika yang diperbaiki."""
        self.logger.info(f"Initializing scraper for '{search_query}'...")
        all_products = []
        
        try:
            page = 1
            while page <= max_pages and len(all_products) < max_products:
                url = self._get_url(search_query, page)
                
                print(f"\n===== ACCESSING PAGE {page} =====")
                self.logger.info(f"Opening search page: {url}")
                self.driver.get(url)

                
                print("Waiting for page to load completely...")
                self._wait_for_initial_load()
                
              
                time.sleep(random.uniform(2, 4))
                
                print(f"Scrolling page {page} to load more products...")
                self._enhanced_scroll_and_wait()
                
                print(f"Finding product cards on page {page}...")
                cards = self._find_product_cards()
                
                print(f"Total product cards found on page {page}: {len(cards)}")
                
                if len(cards) == 0:
                    print(f"WARNING: No product cards found on page {page}. Taking screenshot for debugging...")
                    self._save_debug_info(f"tokopedia_debug_page_{page}")
                    page += 1
                    continue

                print(f"\n===== STARTING PRODUCT EXTRACTION ON PAGE {page} =====")
                
                for i, card in enumerate(cards):
                    if len(all_products) >= max_products:
                        print(f"Reached maximum number of products ({max_products}). Stopping extraction.")
                        break
                    
                    try:
                        print(f"\nExtracting product {i+1} on page {page}...")
                        
                        product_data = self._extract_product_data(card)
                        if product_data:
                            all_products.append(product_data)
                            print(f"✓ Product {i+1} extracted successfully (Total: {len(all_products)})")
                            print(f"  Nama Produk: {product_data['product_name']}")
                            print(f"  Harga Produk: {product_data['price_raw']}")
                            print(f"  Nama Toko: {product_data['shop_name']}")
                        else:
                            print(f"✗ Failed to extract meaningful data for product {i+1}")
                            
                    except StaleElementReferenceException:
                        print(f"✗ Product element became stale. Skipping product {i+1}.")
                        continue
                    except Exception as e:
                        print(f"✗ Error extracting data from product {i+1}: {str(e)}")
                        continue

                print(f"Total products extracted so far: {len(all_products)}")
                
                if len(all_products) >= max_products:
                    break
                
                page += 1
                
                # Sleep strategy
                if page % 5 == 0:
                    print(f"Taking a break after {page-1} pages...")
                    sleep_time = random.uniform(5, 10)  
                    print(f"Waiting {sleep_time:.1f} seconds before loading next page...")
                    time.sleep(sleep_time)

        except Exception as e:
            self.logger.critical(f"An error occurred: {str(e)}")
            # Debug info
            try:
                self.driver.save_screenshot("error_screenshot.png")
                print("Error screenshot saved as 'error_screenshot.png'")
                with open("error_page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("Error page source saved as 'error_page_source.html'")
            except:
                print("Could not save error debug information")
        finally:
            self.close()
        
        print(f"\n===== EXTRACTION COMPLETE: {len(all_products)} PRODUCTS EXTRACTED =====")
        return all_products

    def _wait_for_initial_load(self):
        """Wait strategy"""
        try:
            selectors = self._get_initial_container_selectors()
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ", ".join(selectors))))
            print("Initial product container loaded.")
        except TimeoutException:
            print("Page timed out while loading initial elements. Taking debug screenshot...")
            self._save_debug_info(f"timeout_page")

    def _find_product_cards(self):
        """Strategy untuk menemukan cards."""
        selectors = self._get_card_selectors()
        
        cards = []
        for selector in selectors:
            try:
                # Wait strategy yang sama
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(cards) > 0:
                    print(f"Found {len(cards)} product cards using selector: {selector}")
                    break
            except:
                continue
        return cards

    def _enhanced_scroll_and_wait(self, scroll_cycles=25):
        """Enhanced scroll strategy"""
        # Get initial scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        
        for i in range(scroll_cycles):
            # Calculate scroll position (incremental)
            scroll_position = (i + 1) * viewport_height
            
            # Scroll to position (smoother than jumping to bottom)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            
            if i % 5 == 0:  # Every 5 scrolls, print status
                print(f"Incremental scrolling... ({i+1}/{scroll_cycles})")
            
            # Dynamic wait - timing
            if i < 3:
                time.sleep(random.uniform(2.5, 3.5))
            else:
                time.sleep(random.uniform(1.5, 2.5))
            
            # Check if we've reached the bottom
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("No more content loading, waiting for a bit...")
                time.sleep(3)
                
                # Check one more time
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("Confirmed no more content, stopping scroll")
                    break
                    
            last_height = new_height
        
        # Final scroll strategy
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Scroll back to top
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

    # Abstract methods
    @abstractmethod
    def _get_url(self, search_query, page): pass
    
    @abstractmethod
    def _get_initial_container_selectors(self): pass
        
    @abstractmethod
    def _get_card_selectors(self): pass

    @abstractmethod
    def _extract_product_data(self, card): pass
        
    @abstractmethod
    def _get_defaults(self): pass

    def _save_debug_info(self, file_prefix):
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            screenshot_path = os.path.join(self.debug_dir, f"{file_prefix}.png")
            self.driver.save_screenshot(screenshot_path)
            source_path = os.path.join(self.debug_dir, f"{file_prefix}.html")
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print(f"Debug info saved: {file_prefix}")
        except Exception as e:
            print(f"Could not save debug info: {e}")

    def close(self):
        """Menutup WebDriver dengan aman."""
        if self.driver:
            print("Closing browser...")
            self.driver.quit()