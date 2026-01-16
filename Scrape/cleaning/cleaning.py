# cleaning.py
import json
import os
import re
from pathlib import Path

def classify_product(product_name, category):
    name = product_name.lower()
    if category == "gula_aren":
        if "cair" in name or "liquid" in name:
            return "cair"
        elif "semut" in name or "bubuk" in name or "powder" in name:
            return "bubuk"
        else:
            return "blok"
    elif category == "coconut_sugar":
        if "organik" in name:
            return "organik"
        elif "repack" in name:
            return "repack"
        else:
            return "lainnya"
    elif category == "briket_kelapa":
        if "bbq" in name:
            return "bbq"
        elif "shisha" in name:
            return "shisha"
        else:
            return "umum"
    elif category == "virgin_coconut_oil":
        if "mpasi" in name:
            return "mpasi"
        elif "kulit" in name or "skincare" in name:
            return "kosmetik"
        else:
            return "makanan"
    return "tidak diklasifikasi"

def clean_data(data, category):
    cleaned = []
    for item in data:
        name = item.get('product_name', '')
        price = item.get('price_clean', 0)
        sold = item.get('sold_count_clean', 0)

        if price < 1000 or price > 10000000:
            continue

        subtype = classify_product(name, category)

        cleaned.append({
            "product_name": name,
            "subtype": subtype,
            "price": price,
            "sold": sold,
            "shop_name": item.get('shop_name', ''),
            "url": item.get('product_url', ''),
            "category": category,
            "ecommerce": item.get('ecommerce', 'Tokopedia')
        
        })
    return cleaned

def main():
    base_path = Path(__file__).resolve().parent.parent / "data"
    categories = {
        "gula_aren": base_path / "Result_db.products_tokopedia_gula_aren.json",
        "briket_kelapa": base_path / "Result_db.products_tokopedia_briket_kelapa.json",
        "coconut_sugar": base_path / "Result_db.products_tokopedia_coconut_sugar.json",
        "virgin_coconut_oil": base_path / "Result_db.products_tokopedia_virgin_coconut_oil.json"
    }

    output_path = Path(__file__).resolve().parent.parent / "debug_output"
    output_path.mkdir(parents=True, exist_ok=True)

    for cat, file_path in categories.items():
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            cleaned = clean_data(raw_data, cat)
            with open(output_path / f"cleaned_{cat}.json", 'w', encoding='utf-8') as out:
                json.dump(cleaned, out, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
