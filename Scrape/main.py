# main.py

import os
from dotenv import load_dotenv
from database import Database
from scrapers.tokopedia_scraper import TokopediaScraper
from utils.logger_setup import get_logger

load_dotenv()

def main():
    logger = get_logger("main")

    MONGO_DB_URI = os.getenv("MONGO_URI")
    if not MONGO_DB_URI:
        logger.error("Variabel lingkungan MONGO_URI tidak ditemukan. Buat file .env.")
        return

    SEARCH_QUERIES = ["gula aren"]
    MAX_PRODUCTS_PER_QUERY = 500  
    MAX_PAGES_PER_QUERY = 50       
    RUN_IN_HEADLESS = False         

    try:
        db = Database(db_uri=MONGO_DB_URI, db_name="harga_komoditas_db")
    except Exception:
        return

    for query in SEARCH_QUERIES:
        logger.info(f"===== Memulai Scraping untuk Query: '{query}' =====")
        
        scraper = TokopediaScraper(headless=RUN_IN_HEADLESS)
        
        try:
            products = scraper.scrape(
                search_query=query,
                max_products=MAX_PRODUCTS_PER_QUERY,
                max_pages=MAX_PAGES_PER_QUERY
            )
            
           
            for p in products:
                p["search_query"] = query
            
            if products:
                # Simpan dengan nama collection yang spesifik per query
                collection_name = f"products_tokopedia_{query.replace(' ', '_')}"
                db.save_products(products, collection_name)
                logger.info(f"Berhasil menyimpan {len(products)} produk untuk query '{query}'")
            else:
                logger.warning(f"Tidak ada produk yang berhasil diambil untuk query '{query}'")
                
        except Exception as e:
            logger.error(f"Error saat scraping query '{query}': {e}")
        finally:
            # Pastikan scraper ditutup untuk setiap query
            scraper.close()

    db.close_connection()
    logger.info("===== Semua Proses Scraping Selesai =====")

if __name__ == "__main__":
    main()