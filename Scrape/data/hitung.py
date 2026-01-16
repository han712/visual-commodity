import json

def hitung_produk_json(nama_file):
    """
    Fungsi untuk menghitung jumlah produk dari file JSON.

    Args:
      nama_file (str): Nama file JSON yang akan dibaca.

    Returns:
      int: Jumlah produk dalam file.
    """
    try:
        with open(nama_file, 'r') as f:
            data = json.load(f)
            return len(data)
    except FileNotFoundError:
        print(f"Error: File '{nama_file}' tidak ditemukan.")
        return 0
    except json.JSONDecodeError:
        print(f"Error: Gagal mendekode JSON dari file '{nama_file}'.")
        return 0

# Daftar file JSON yang diunggah
daftar_file = [
    'Result_db.products_tokopedia_gula_aren.json',
    'Result_db.products_tokopedia_briket_kelapa.json',
    'Result_db.products_tokopedia_coconut_sugar.json',
    'Result_db.products_tokopedia_virgin_coconut_oil.json'
]

total_produk = 0
for file in daftar_file:
    jumlah_produk = hitung_produk_json(file)
    print(f"Jumlah produk di file '{file}': {jumlah_produk}")
    total_produk += jumlah_produk

print(f"\nTotal semua produk: {total_produk}")