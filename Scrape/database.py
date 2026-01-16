# database.py
# Modul ini bertanggung jawab untuk semua interaksi dengan database MongoDB.

import pymongo
from urllib.parse import quote_plus
from utils.logger_setup import get_logger # Menggunakan logger yang sudah dikonfigurasi

class Database:
    """
    Kelas untuk mengelola koneksi dan operasi database MongoDB.
    """
    def __init__(self, db_uri, db_name="ecommerce_data"):
        """
        Inisialisasi koneksi ke database.
        
        Args:
            db_uri (str): Connection string untuk MongoDB Atlas.
            db_name (str): Nama database yang akan digunakan.
        """
        self.logger = get_logger("database")
        self.client = None
        try:
            self.client = pymongo.MongoClient(db_uri)
            # Verifikasi koneksi
            self.client.admin.command('ping')
            self.db = self.client[db_name]
            self.logger.info(f"Berhasil terhubung ke MongoDB. Database: '{db_name}'.")
        except pymongo.errors.ConnectionFailure as e:
            self.logger.error(f"Gagal terhubung ke MongoDB: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Terjadi error saat inisialisasi database: {e}")
            raise
        
    def save_products(self, products, collection_name):
        """
        Menyimpan daftar produk ke dalam collection yang ditentukan.
        
        Args:
            products (list): Daftar dictionary produk yang akan disimpan.
            collection_name (str): Nama collection (tabel) tempat menyimpan data.
        """
        if not products:
            self.logger.warning("Tidak ada produk untuk disimpan.")
            return

        try:
            collection = self.db[collection_name]
            result = collection.insert_many(products)
            self.logger.info(f"Berhasil menyimpan {len(result.inserted_ids)} produk ke collection '{collection_name}'.")
        except Exception as e:
            self.logger.error(f"Gagal menyimpan produk ke collection '{collection_name}': {e}")

    def close_connection(self):
        """
        Menutup koneksi database.
        """
        if self.client:
            self.client.close()
            self.logger.info("Koneksi ke MongoDB ditutup.")
    def get_collection_data(self, collection_name, as_df=False):
        """
        Mengambil data dari collection. Jika as_df=True, return DataFrame.
        """
        try:
            collection = self.db[collection_name]
            data = list(collection.find())
            if as_df:
                import pandas as pd
                return pd.DataFrame(data)
            return data
        except Exception as e:
            self.logger.error(f"Gagal membaca data dari '{collection_name}': {e}")
            return []
