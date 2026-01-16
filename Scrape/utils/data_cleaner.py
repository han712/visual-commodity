# utils/data_cleaner.py
# Modul ini berisi fungsi-fungsi untuk membersihkan data mentah dari hasil scrape.

import re
from typing import Optional, Union

def clean_price(price_text: Union[str, int]) -> Optional[int]:
    """
    Membersihkan teks harga (misal: "Rp15.000") menjadi integer (15000).
    """
    if isinstance(price_text, int):
        return price_text
    if not isinstance(price_text, str):
        return None
        
    # Menghapus semua karakter non-digit
    match = re.search(r'[\d.,]+', price_text)
    if match:
        # Menghapus titik dan koma, lalu konversi ke integer
        cleaned_string = match.group(0).replace(".", "").replace(",", "")
        return int(cleaned_string)
    return None

def clean_sold_count(sold_text: str) -> int:
    """
    Membersihkan teks jumlah terjual (misal: "500+ terjual") menjadi integer (500).
    """
    if not isinstance(sold_text, str):
        return 0

    # Mengubah 'rb' menjadi '000'
    sold_text = sold_text.lower().replace('rb', '000')

    # Mencari angka dalam teks
    match = re.search(r'[\d.]+', sold_text)
    if match:
        # Menghapus titik lalu konversi ke integer
        cleaned_number = match.group(0).replace('.', '')
        return int(cleaned_number)
    return 0
