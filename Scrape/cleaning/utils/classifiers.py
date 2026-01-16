def classify_product_briket(text):
    text = text.lower()
    bentuk = "hexagonal" if "hex" in text else "cube" if "cube" in text or "kotak" in text else "lain"
    kegunaan = "shisha" if "shisha" in text else "bbq" if "bbq" in text else "lain"
    kualitas = "export" if "export" in text or "ekspor" in text else "lokal"
    return bentuk, kegunaan, kualitas

def classify_product_gula_aren(text):
    text = text.lower()
    bentuk = "cair" if "cair" in text or "syrup" in text else "bubuk" if "bubuk" in text or "semut" in text else "lain"
    kualitas = "organik" if "organik" in text else "murni" if "murni" in text else "umum"
    return bentuk, kualitas

def classify_product_vco(text):
    text = text.lower()
    kegunaan = "mpasi" if "mpasi" in text else "hewan" if "kucing" in text or "anjing" in text else "rambut" if "rambut" in text else "umum"
    jenis = "evco" if "evco" in text else "vco" if "vco" in text else "lain"
    return kegunaan, jenis
