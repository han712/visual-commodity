import os
import json
import pandas as pd

from utils.cleaner import remove_irrelevant_products, drop_duplicates, clean_weight
from utils.classifiers import (
    classify_product_briket,
    classify_product_gula_aren,
    classify_product_vco
)

# Fungsi utama untuk membersihkan dan klasifikasi
def process_file(filepath, keywords, classify_func=None):
    print(f"🔍 Membuka file: {os.path.abspath(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # Cleaning step
    df = remove_irrelevant_products(df, keywords)
    df = drop_duplicates(df)

    # Tambahkan berat/volume dan hitung harga per unit
    df['weight_kg'] = df['product_name'].apply(clean_weight)
    df['price_per_kg'] = df.apply(
        lambda row: row['price_clean'] / row['weight_kg']
        if row['weight_kg'] else None,
        axis=1
    )

    # Klasifikasi tambahan
    if classify_func:
        classified = df['product_name'].apply(classify_func)
        cat_df = pd.DataFrame(classified.tolist())
        df = pd.concat([df, cat_df], axis=1)

    return df

# Jalankan semua cleaning
if __name__ == "__main__":
    base_path = os.path.dirname(__file__)  # path ke /cleaning

    datasets = [
        {
            "filename": "Result_db.products_tokopedia_briket_kelapa.json",
            "keywords": ["briket", "arang", "kelapa"],
            "classifier": classify_product_briket,
            "output": "cleaned_briket_kelapa.json"
        },
        {
            "filename": "Result_db.products_tokopedia_gula_aren.json",
            "keywords": ["aren", "gula", "semut", "cair"],
            "classifier": classify_product_gula_aren,
            "output": "cleaned_gula_aren.json"
        },
        {
            "filename": "Result_db.products_tokopedia_coconut_sugar.json",
            "keywords": ["coconut", "sugar", "kelapa"],
            "classifier": classify_product_gula_aren,
            "output": "cleaned_coconut_sugar.json"
        },
        {
            "filename": "Result_db.products_tokopedia_virgin_coconut_oil.json",
            "keywords": ["vco", "minyak", "coconut", "kelapa"],
            "classifier": classify_product_vco,
            "output": "cleaned_virgin_coconut_oil.json"
        }
    ]

    for d in datasets:
        input_path = os.path.join(base_path, "data", d["filename"])
        output_path = os.path.join(base_path, "output", d["output"])

        df_cleaned = process_file(input_path, d["keywords"], d["classifier"])
        # Hapus kolom location jika ada
        if 'location' in df_cleaned.columns:
            df_cleaned = df_cleaned.drop(columns=['location'])

        df_cleaned.to_json(output_path, orient="records", force_ascii=False, indent=2)
        print(f"✅ File cleaned (JSON) disimpan ke: {output_path}")

