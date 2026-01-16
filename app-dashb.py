import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
import warnings
import re

warnings.filterwarnings('ignore')

# KONFIGURASI HALAMAN

st.set_page_config(
    page_title="Dashboard Analisis Pasar Produk Kelapa Indonesia - Modular",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FUNGSI UNTUK MEMUAT CSS DARI FILE EKSTERNAL
def load_css(file_name):
    """Fungsi untuk memuat dan merender file CSS eksternal."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File CSS '{file_name}' tidak ditemukan. Pastikan file tersebut berada di direktori yang sama dengan app.py.")

# DEFINISI KEYWORD UNTUK KLASIFIKASI & PENANGANAN NOISE

CLASSIFICATION_KEYWORDS = {
    "Gula Aren": {
        "noise": [
            'kopi', 'coffee', 'latte', 'cappuccino', 'espresso', 'mocha', 'americano',
            'susu', 'milk', 'creamer', 'dairy', 'ultra milk', 'dancow', 'frisian flag',
            'jahe', 'wedang', 'minuman', 'drink', 'beverage', 'instant', 'sachet drink',
            'teh', 'tea', 'green tea', 'black tea', 'oolong', 'earl grey',
            'coklat', 'chocolate', 'cocoa', 'milo', 'ovaltine', 'hot chocolate',
            'telur gabus', 'kue', 'bolu', 'cake', 'bakery', 'roti', 'bread',
            'jenang', 'dodol', 'cemilan', 'snack', 'keripik', 'crackers',
            'biskuit', 'cookies', 'wafer', 'pie', 'tart', 'pastry',
            'permen', 'candy', 'lollipop', 'gummy', 'marshmallow',
            'scrub', 'lulur', 'masker', 'mask', 'facial', 'body scrub',
            'sabun', 'soap', 'shampoo', 'body wash', 'shower gel',
            'lotion', 'cream', 'moisturizer', 'serum', 'toner',
            'parfum', 'perfume', 'fragrance', 'cologne', 'eau de toilette',
            'lilin', 'candle', 'aromatherapy', 'essential oil',
            'toples', 'jar', 'bottle', 'kemasan', 'packaging',
            'sendok', 'spoon', 'cup', 'gelas', 'mug', 'piring',
            'mesin', 'machine', 'alat', 'tool', 'blender', 'mixer',
            'flavour', 'flavor', 'rasa', 'taste', 'aroma', 'essence',
            'extract', 'ekstrak', 'powder', 'tepung', 'bubuk non-gula',
            'sirup non-aren', 'artificial', 'synthetic', 'tiruan',
            'kap', 'food grade', 'pabrik', 'pengering', 'pemanas', 
            'tebu', 'gula tebu'
        ],
        "positive_indicators": [
            'gula aren', 'palm sugar', 'coconut palm sugar', 'sugar palm',
            'nira aren', 'nira kelapa', 'organic palm sugar', 'gula merah aren',
            'brown sugar aren', 'raw palm sugar', 'unrefined palm sugar',
            'tradisional', 'traditional', 'asli', 'murni', 'pure', 'natural',
            'organik', 'organic', 'non-refined', 'unprocessed'
        ],
        "features": {
            "Bentuk Produk": {
                "Cair": ['cair', 'sirup', 'syrup', 'liquid', 'molasses'],
                "Bubuk": ['bubuk', 'semut', 'kristal', 'powder', 'granule', 'granulated'],
                "Padat": ['batok', 'cetak', 'gandu', 'koin', 'toros', 'solid', 'cube', 'block']
            },
            "Klaim Kualitas": {
                "Organik": ['organik', 'organic', 'bio', 'natural'],
                "Murni/Asli": ['asli', 'murni', 'nira', 'pure', 'natural', 'authentic'],
                "Premium": ['premium', 'super', 'grade a', 'quality', 'high grade']
            }
        }
    },
    "Gula Kelapa": {
        "noise": [
            'scrub', 'lulur', 'exfoliate', 'peeling', 'body scrub', 'face scrub',
            'parfum', 'perfume', 'fragrance', 'cologne', 'deodorant', 'antiperspirant',
            'lotion', 'sabun', 'soap', 'shampoo', 'body wash', 'shower gel',
            'lip oil', 'lipstick', 'lip balm', 'lip gloss', 'cosmetic', 'beauty',
            'moisturizer', 'cream', 'serum', 'toner', 'cleanser', 'mask',
            'snack', 'bar', 'protein bar', 'energy bar', 'granola bar',
            'chocolate', 'coklat', 'candy', 'permen', 'sweet', 'dessert',
            'vsoy', 'soy milk', 'milk', 'susu', 'dairy', 'yogurt',
            'kopi', 'coffee', 'latte', 'cappuccino', 'minuman', 'drink',
            'pet', 'hamster', 'sugar glider', 'kucing', 'cat', 'dog', 'anjing',
            'bird', 'burung', 'fish', 'ikan', 'pet food', 'animal feed',
            'aren', 'palm sugar', 'vco', 'virgin coconut oil', 'coconut oil',
            'minyak kelapa', 'oil', 'minyak', 'santan', 'coconut milk',
            'kelapa parut', 'desiccated coconut', 'coconut flakes',
            'tepung', 'flour', 'protein', 'supplement', 'vitamin', 'nutrisi',
            'garam', 'salt', 'msg', 'penyedap', 'seasoning', 'bumbu',
            'kemasan', 'packaging', 'jar', 'toples', 'bottle', 'botol',
            'sendok', 'spoon', 'cup', 'gelas', 'mesin', 'machine', 'tebu', 'gula tebu'
        ],
        "positive_indicators": [
            'gula kelapa', 'coconut sugar', 'coconut palm sugar', 'coco sugar',
            'brown coconut sugar', 'organic coconut sugar', 'natural coconut sugar',
            'unrefined coconut sugar', 'raw coconut sugar', 'pure coconut sugar',
            'tradisional', 'traditional', 'asli', 'murni', 'organic', 'natural'
        ],
        "features": {
            "Bentuk Produk": {
                "Cair": ['cair', 'syrup', 'liquid', 'sirup', 'molasses'],
                "Bubuk": ['bubuk', 'semut', 'kristal', 'powder', 'granule', 'granulated'],
                "Padat": ['cetak', 'cube', 'solid', 'block', 'brick'],
                "Sachet": ['stick', 'sachet', 'packet', 'pouch', 'individual pack']
            },
            "Klaim Kualitas": {
                "Organik": ['organik', 'organic', 'bio', 'natural'],
                "Murni/Asli": ['murni', 'pure', 'natural', 'asli', 'authentic'],
                "Warna": ['white', 'brown', 'golden', 'putih', 'coklat', 'keemasan']
            }
        }
    },
    "Briket Kelapa": {
        "noise": [
            'tepung', 'powder', 'flour', 'dust', 'serbuk', 'sawdust',
            'limbah', 'waste', 'sampah', 'refuse', 'debris',
            'sekam', 'husk', 'kulit', 'tempurung mentah',
            'box', 'packaging', 'kardus', 'carton', 'container',
            'plastik', 'plastic', 'bag', 'kantong', 'sack', 'karung',
            'mesin', 'machine', 'alat', 'tool', 'equipment', 'apparatus',
            'press', 'mold', 'cetakan', 'pencetak', 'compressor',
            'oven', 'stove', 'kompor', 'burner', 'grill pan',
            'panggangan listrik', 'electric grill', 'gas grill',
            'roaster', 'smoker', 'barbecue pit',
            'penetral abu', 'ash neutralizer', 'abu', 'ash', 'residue',
            'binder', 'perekat', 'lem', 'glue', 'adhesive', 'binding agent',
            'aktivator', 'activator', 'kimia', 'chemical', 'additive',
            'pengawet', 'preservative', 'stabilizer', 'catalyst',
            'arang aktif', 'activated charcoal', 'karbon aktif', 'activated carbon',
            'filter', 'penyaring', 'purifier', 'pembersih', 'cleaner', 'tebu', 'gula tebu'  
        ],
        "positive_indicators": [
            'briket', 'briquette', 'charcoal briquette', 'coconut briquette',
            'briket kelapa', 'coconut charcoal', 'arang briket', 'compressed charcoal',
            'hexagonal briquette', 'cube briquette', 'finger briquette',
            'barbecue briquette', 'bbq briquette', 'shisha briquette', 'hookah charcoal'
        ],
        "features": {
            "Bentuk Briket": {
                "Hexagonal": ['hexagonal', 'segi enam', 'hex', 'hexagon'],
                "Kubus": ['cube', 'kubus', 'kotak', 'dadu', 'square', 'cubic'],
                "Jari": ['finger', 'jari', 'stick', 'batang', 'rod'],
                "Bantal": ['bantal', 'pillow', 'oval', 'cushion']
            },
            "Tujuan Penggunaan": {
                "BBQ": ['bbq', 'barbeque', 'grill', 'panggangan', 'sate', 'roasting', 'grilling'],
                "Shisha": ['shisha', 'sisha', 'hookah', 'waterpipe', 'narghile'],
                "Spa/Aromaterapi": ['ratus', 'dupa', 'buhur', 'aromatherapy', 'spa', 'incense']
            },
            "Kualitas": {
                "Ekspor": ['ekspor', 'export', 'international', 'overseas'],
                "Premium": ['premium', 'super', 'grade a', 'quality', 'high grade'],
                "Low Ash": ['low ash', 'abu rendah', 'clean burning', 'minimal ash']
            }
        }
    },
    "Virgin Coconut Oil": {
        "noise": [
            'zaitun', 'olive', 'olive oil', 'extra virgin olive oil',
            'sunflower', 'minyak bunga matahari', 'sunflower oil',
            'canola', 'canola oil', 'rapeseed oil', 'corn oil', 'jagung',
            'palm oil', 'minyak sawit', 'crude palm oil', 'cpo',
            'soybean oil', 'minyak kedelai', 'sesame oil', 'wijen',
            'vitamin', 'supplement', 'suplemen', 'nutrisi', 'nutrition',
            'capsule', 'kapsul', 'tablet', 'pill', 'softgel',
            'omega', 'fish oil', 'minyak ikan', 'cod liver oil',
            'granola', 'cereal', 'sereal', 'oats', 'havermut',
            'muesli', 'corn flakes', 'breakfast', 'sarapan',
            'nuts', 'kacang', 'almond', 'walnut', 'peanut',
            'sabun', 'soap', 'hand soap', 'body soap', 'facial soap',
            'shampoo', 'sampo', 'conditioner', 'hair mask', 'hair treatment',
            'lotion', 'cream', 'moisturizer', 'body lotion', 'hand cream',
            'massage oil', 'minyak pijat', 'essential oil', 'aromatherapy oil',
            'buku', 'book', 'panduan', 'guide', 'manual', 'cookbook',
            'resep', 'recipe', 'tutorial', 'dvd', 'video', 'cd',
            'blend', 'mixed', 'campuran', 'mixture', 'combination',
            'infused', 'flavored', 'rasa', 'taste', 'aroma'
        ],
        "positive_indicators": [
            'virgin coconut oil', 'vco', 'coconut oil', 'minyak kelapa',
            'virgin coconut', 'extra virgin coconut oil', 'cold pressed coconut oil',
            'organic coconut oil', 'pure coconut oil', 'natural coconut oil',
            'unrefined coconut oil', 'raw coconut oil'
        ],
        "features": {
            "Target Penggunaan": {
                "MPASI": ['mpasi', 'baby food', 'bayi', 'infant', 'complementary food'],
                "Hewan": ['hewan', 'kucing', 'anjing', 'pet', 'animal', 'cat', 'dog'],
                "Kecantikan": ['rambut', 'kulit', 'wajah', 'beauty', 'skincare', 'hair', 'skin'],
                "Kesehatan": ['minum', 'kesehatan', 'health', 'therapy', 'therapeutic'],
                "Masak": ['masak', 'cooking', 'frying', 'goreng', 'culinary', 'kitchen']
            }
        }
    }
}

# ======================================================================================
# FUNGSI-FUNGSI UTILITY
# ======================================================================================

def advanced_product_classifier(product_name, category):
    """
    Classifier untuk memastikan relevansi.
    Logika untuk memprioritaskan deteksi kata kunci 'noise'. Jika ada kata kunci
    'noise' yang ditemukan, produk akan langsung diklasifikasikan sebagai tidak relevan.
    Jika tidak ada noise dan tidak ada indikator positif, produk juga dianggap tidak relevan
    untuk memastikan filter bekerja secara ketat.
    """
    if pd.isna(product_name):
        return False, "No product name", []

    product_lower = str(product_name).lower()
    category_config = CLASSIFICATION_KEYWORDS.get(category, {})
    noise_keywords = category_config.get("noise", [])
    positive_indicators = category_config.get("positive_indicators", [])

    # Langkah 1: Deteksi noise sebagai prioritas utama.
    noise_matches = [noise for noise in noise_keywords if noise in product_lower]
            
    if noise_matches:
        # Jika ada noise, langsung kembalikan False.
        return False, f"Noise detected: {', '.join(noise_matches)}", noise_matches

    # Langkah 2: Jika tidak ada noise, baru periksa indikator positif.
    positive_score = sum(1 for indicator in positive_indicators if indicator in product_lower)
    
    if positive_score > 0:
        return True, "Positive indicator found", []
    
    # Langkah 3: Jika tidak ada noise dan tidak ada indikator positif, anggap TIDAK relevan.
    # Ini adalah perubahan kunci untuk membuat filter lebih ketat dan akurat.
    return False, "Ambiguous: No clear positive or noise keywords", []

def calculate_data_quality_score(row):
    """Menghitung skor kualitas data berdasarkan kelengkapan informasi."""
    score = 0
    max_score = 10
    
    if pd.notna(row.get('product_name')) and len(str(row.get('product_name'))) > 10: score += 2
    elif pd.notna(row.get('product_name')): score += 1
    
    if pd.notna(row.get('price_clean')) and row.get('price_clean', 0) > 0: score += 2
    if pd.notna(row.get('sold_count_clean')) and row.get('sold_count_clean', 0) >= 0: score += 1
    if pd.notna(row.get('shop_name')) and len(str(row.get('shop_name'))) > 2: score += 1
    if pd.notna(row.get('weight_kg')) and row.get('weight_kg', 0) > 0: score += 1
    if pd.notna(row.get('product_url')) and 'tokopedia.com' in str(row.get('product_url')): score += 1
    if pd.notna(row.get('description')) and len(str(row.get('description'))) > 20: score += 1
    
    return min(score, max_score)

def classify_row(name, keywords_dict):
    """Fungsi helper untuk mengklasifikasikan satu baris berdasarkan nama produk."""
    if pd.isna(name):
        return "Tidak Diketahui"
    name_lower = str(name).lower()
    for key, keywords in keywords_dict.items():
        if any(keyword in name_lower for keyword in keywords):
            return key
    return "Lainnya"

def calculate_competition_level(df):
    """Menghitung tingkat kompetisi berdasarkan jumlah produk dan toko."""
    if df.empty:
        return "Tidak Ada Data", "#64748b"
    total_products = len(df)
    unique_shops = df['shop_name'].nunique()
    
    if total_products > 100 and unique_shops > 30:
        return "Tinggi", "#ef4444"
    elif total_products > 50 and unique_shops > 15:
        return "Sedang", "#f59e0b"
    else:
        return "Rendah", "#10b981"


def convert_df_to_csv(df):
    """Konversi DataFrame ke CSV untuk di-download."""
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data(ttl=3600)
def load_and_process_data():
    """Memuat, menggabungkan, dan melakukan rekayasa fitur pada semua dataset."""
    data_folder = "data"
    if not os.path.exists(data_folder):
        st.error(f"📁 Folder '{data_folder}' tidak ditemukan. Pastikan Anda membuat folder 'data' dan meletakkan file JSON di dalamnya.")
        return pd.DataFrame()

    data_files = {
        "Briket Kelapa": os.path.join(data_folder, "cleaned_briket_kelapa.json"),
        "Gula Kelapa": os.path.join(data_folder, "cleaned_coconut_sugar.json"),
        "Gula Aren": os.path.join(data_folder, "cleaned_gula_aren.json"),
        "Virgin Coconut Oil": os.path.join(data_folder, "cleaned_virgin_coconut_oil.json")
    }
    
    all_df = []
    loading_placeholder = st.empty()
    
    for i, (category, filepath) in enumerate(data_files.items()):
        loading_placeholder.info(f"🔄 Memuat data {category}... ({i+1}/{len(data_files)})")
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)
                if not data: continue
                
                df = pd.DataFrame(data)
                df['product_category'] = category
                
                required_cols = ['product_name', 'price_clean', 'sold_count_clean']
                if any(col not in df.columns for col in required_cols): continue
                
                classification_results = df.apply(lambda row: advanced_product_classifier(row['product_name'], category), axis=1)
                df['is_relevant_product'] = [result[0] for result in classification_results]
                df['classification_reason'] = [result[1] for result in classification_results]
                df['noise_keywords_found'] = [result[2] for result in classification_results]
                df['noise_keyword_count'] = df['noise_keywords_found'].apply(len)
                
                cat_keywords = CLASSIFICATION_KEYWORDS.get(category, {})
                feature_defs = cat_keywords.get("features", {})
                for feature_name, keywords_map in feature_defs.items():
                    df[feature_name] = df['product_name'].apply(lambda x: classify_row(x, keywords_map))

                df['data_quality_score'] = df.apply(calculate_data_quality_score, axis=1)
                all_df.append(df)
        except Exception as e:
            st.sidebar.error(f"❌ Gagal memuat {filepath}: {str(e)}")
            continue
            
    loading_placeholder.empty()
    if not all_df:
        st.error("❌ Tidak ada data yang berhasil dimuat.")
        return pd.DataFrame()

    combined_df = pd.concat(all_df, ignore_index=True)
    
    numeric_cols = ['price_clean', 'sold_count_clean', 'weight_kg']
    for col in numeric_cols:
        if col in combined_df.columns:
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

    combined_df.dropna(subset=['price_clean', 'sold_count_clean'], inplace=True)
    combined_df = combined_df[(combined_df['price_clean'] > 0) & (combined_df['sold_count_clean'] >= 0)]
    
    if 'weight_kg' in combined_df.columns:
        combined_df = combined_df[combined_df['weight_kg'] > 0]
        combined_df['price_per_kg'] = combined_df['price_clean'] / combined_df['weight_kg']
    else:
        combined_df['price_per_kg'] = combined_df['price_clean']
    
    combined_df['total_revenue'] = combined_df['price_clean'] * combined_df['sold_count_clean']
    combined_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    combined_df.dropna(subset=['price_per_kg'], inplace=True)
    
    combined_df['is_price_outlier'] = False
    if len(combined_df) > 10:
        for category in combined_df['product_category'].unique():
            cat_df = combined_df[combined_df['product_category'] == category]
            if len(cat_df) > 5:
                Q1 = cat_df['price_per_kg'].quantile(0.25)
                Q3 = cat_df['price_per_kg'].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                combined_df.loc[
                    (combined_df['product_category'] == category) & 
                    ((combined_df['price_per_kg'] < lower_bound) | (combined_df['price_per_kg'] > upper_bound)),
                    'is_price_outlier'
                ] = True

    final_count = len(combined_df)
    relevant_count = len(combined_df[combined_df['is_relevant_product']])
    noise_count = final_count - relevant_count
    
    st.success(f"""
    ✅ **Data berhasil dimuat dan diproses**
    - 📊 Total produk valid: **{final_count:,}** | ✅ Relevan: **{relevant_count:,}** ({(relevant_count/final_count*100):.1f}%) | 🗑️ Noise: **{noise_count:,}** ({(noise_count/final_count*100):.1f}%)
    """)
    return combined_df


# SIDEBAR / PANEL KONTROL

def setup_sidebar(df):
    """Membuat dan mengelola semua widget filter di sidebar."""
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #10b981, #3b82f6); border-radius: 12px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🎛️ Panel Kontrol</h2>
        <img src="https://i.gifer.com/XHXt.gif" alt="Control Icon" style="width: 100px; height: 100px; margin-top: 0.5rem;">
        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Filter & Analisis Data</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("### 🏷️ Pilih Kategori Produk")
    all_categories = sorted(list(df['product_category'].unique()))
    category_counts = df['product_category'].value_counts()
    category_options = [f"{cat} ({category_counts.get(cat, 0):,})" for cat in all_categories]
    
    selected_category_labels = st.sidebar.multiselect(
        "Kategori tersedia:", 
        options=category_options, 
        default=[],
        help="Pilih satu atau lebih kategori untuk dianalisis"
    )
    selected_categories = [label.split(' (')[0] for label in selected_category_labels]

    st.sidebar.markdown("### 🎯 Filter Kualitas & Relevansi")
    filter_relevant = st.sidebar.checkbox("Hanya produk relevan", value=True, help="Menyembunyikan data noise atau produk non-komoditas")
    

    
    filtered_df = df.copy()
    if not selected_categories:
        st.warning("⚠️ Pilih setidaknya satu kategori produk untuk melanjutkan analisis.")
        return pd.DataFrame(columns=df.columns), selected_categories
    
    filtered_df = filtered_df[filtered_df['product_category'].isin(selected_categories)]
    if filter_relevant: filtered_df = filtered_df[filtered_df['is_relevant_product']]
    
    original_count = len(df[df['product_category'].isin(selected_categories)])
    filtered_count = len(filtered_df)
    
    if filtered_count < original_count:
        st.sidebar.success(f"✅ Filter diterapkan: {filtered_count:,} dari {original_count:,} produk ditampilkan.")
    
    return filtered_df, selected_categories


# FUNGSI UNTUK TABS KONTEN

def display_summary_tab(df):
    """Tab ringkasan eksekutif."""
    st.markdown('<h2 class="section-header">🚀 Ringkasan Eksekutif Pasar</h2>', unsafe_allow_html=True)
    
    if df.empty:
        st.warning("⚠️ Tidak ada data untuk ditampilkan berdasarkan filter yang Anda pilih.")
        return

    total_omzet = int(df['total_revenue'].sum())
    total_penjualan = int(df['sold_count_clean'].sum())
    rata_harga_kg = int(df['price_per_kg'].median())

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f'''<div class="metric-card"><h3>💰 Total Estimasi Omzet</h3><p>Rp {total_omzet:,}</p></div>''', unsafe_allow_html=True)
    with col2: st.markdown(f'''<div class="metric-card"><h3>📈 Volume Penjualan</h3><p>{total_penjualan:,}</p></div>''', unsafe_allow_html=True)
    with col3: st.markdown(f'''<div class="metric-card"><h3>⚖️ Harga Median/Kg</h3><p>Rp {rata_harga_kg:,}</p></div>''', unsafe_allow_html=True)
    with col4: st.markdown(f'''<div class="metric-card"><h3>🏪 Jumlah Toko Unik</h3><p>{df['shop_name'].nunique():,}</p></div>''', unsafe_allow_html=True)

    
    st.markdown('<h2 class="section-header">🏆 Entitas Unggulan & Performa</h2>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("#### 🔥 Top 10 Produk Terlaris (Unit)")
        top_sold = df.nlargest(10, 'sold_count_clean')
        for i, (_, row) in enumerate(top_sold.iterrows(), 1):
            name = str(row['product_name'])
            product_url = row.get('product_url', '#')
            
            st.markdown(f"""
                <div class="tokopedia-card">
                    <div style="display: flex; align-items: center;">
                        <span style="background: #10b981; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; margin-right: 8px;">{i}</span>
                        <strong style="font-size: 0.9rem;">{name}</strong>
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="profit-highlight">{int(row["sold_count_clean"]):,}</span> terjual
                    </div>
                    <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">
                        {row["product_category"]} • {str(row.get("shop_name", "N/A"))[:20]}
                    </div>
                    <a href="{product_url}" target="_blank" style="color: #42B883; font-size: 0.8rem; text-decoration: none;">Lihat di Tokopedia 🔗</a>
                </div>
            """, unsafe_allow_html=True)
    with col_b:
        st.markdown("#### 💎 Top 10 Produk Menguntungkan (Omzet)")
        top_revenue = df.nlargest(10, 'total_revenue')
        for i, (_, row) in enumerate(top_revenue.iterrows(), 1):
            name = str(row['product_name'])
            product_url = row.get('product_url', '#')
            
            st.markdown(f"""
                <div class="tokopedia-card">
                    <div style="display: flex; align-items: center;">
                        <span style="background: #3b82f6; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; margin-right: 8px;">{i}</span>
                        <strong style="font-size: 0.9rem;">{name}</strong>
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="profit-highlight">Rp{int(row["total_revenue"]):,}</span> omzet
                    </div>
                    <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">
                        Rp{int(row["price_clean"]):,} × {int(row["sold_count_clean"]):,} terjual
                    </div>
                    <a href="{product_url}" target="_blank" style="color: #42B883; font-size: 0.8rem; text-decoration: none;">Lihat di Tokopedia 🔗</a>
                </div>
            """, unsafe_allow_html=True)
    with col_c:
        st.markdown("#### 🏪 Top 10 Toko Performa Terbaik (Omzet)")
        if 'shop_name' in df.columns:
            top_shops = df.groupby('shop_name').agg(total_revenue=('total_revenue', 'sum'), total_sold=('sold_count_clean', 'sum'), product_count=('product_name', 'count')).nlargest(10, 'total_revenue')
            for i, (shop_name, row) in enumerate(top_shops.iterrows(), 1):
                st.markdown(f'<div class="tokopedia-card"><div style="display: flex; align-items: center;"><span style="background: #6366f1; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; margin-right: 8px;">{i}</span><strong style="font-size: 0.9rem;">{shop_name[:50]}</strong></div><div style="margin-top: 8px;"><span class="profit-highlight">Rp{int(row["total_revenue"]):,}</span> omzet</div><div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">{int(row["total_sold"]):,} unit dari {int(row["product_count"])} produk</div></div>', unsafe_allow_html=True)

    display_seller_insights(df)
  
def display_product_attribute_analysis(df):
    st.markdown('<h2 class="section-header">📊 Ringkasan Statistik per Komoditas</h2>', unsafe_allow_html=True)

    if not df.empty:
      # Menghitung ringkasan statistik
      stats_summary = df.groupby('product_category')[['price_per_kg', 'sold_count_clean', 'total_revenue']].agg(['mean', 'median', 'min', 'max', 'std']).reset_index()
      
      # Merapikan nama kolom
      stats_summary.columns = ['Komoditas', 'Harga/Kg (Rata-rata)', 'Harga/Kg (Median)', 'Harga/Kg (Min)', 'Harga/Kg (Maks)', 'Harga/Kg (Std Dev)',
                              'Terjual (Rata-rata)', 'Terjual (Median)', 'Terjual (Min)', 'Terjual (Maks)', 'Terjual (Std Dev)',
                              'Revenue (Rata-rata)', 'Revenue (Median)', 'Revenue (Min)', 'Revenue (Maks)', 'Revenue (Std Dev)']

      st.dataframe(stats_summary.style.format({
          'Harga/Kg (Rata-rata)': "Rp {:,.0f}", 'Harga/Kg (Median)': "Rp {:,.0f}", 'Harga/Kg (Min)': "Rp {:,.0f}", 'Harga/Kg (Maks)': "Rp {:,.0f}", 'Harga/Kg (Std Dev)': "Rp {:,.0f}",
          'Terjual (Rata-rata)': "{:,.0f}", 'Terjual (Median)': "{:,.0f}", 'Terjual (Min)': "{:,.0f}", 'Terjual (Maks)': "{:,.0f}", 'Terjual (Std Dev)': "{:,.0f}",
          'Revenue (Rata-rata)': "Rp {:,.0f}", 'Revenue (Median)': "Rp {:,.0f}", 'Revenue (Min)': "Rp {:,.0f}", 'Revenue (Maks)': "Rp {:,.0f}", 'Revenue (Std Dev)': "Rp {:,.0f}",
      }), use_container_width=True)
    else:
      st.info("Pilih komoditas untuk melihat ringkasan statistiknya.")
    
    
    """Menganalisis performa produk berdasarkan atribut."""
    st.markdown('<h2 class="section-header">🔬 Analisis Atribut & Fitur Produk</h2>', unsafe_allow_html=True)
    if df.empty:
        st.info("Pilih data pada sidebar untuk memulai analisis atribut.")
        return

    st.markdown("Visualisasi di bawah ini menampilkan distribusi berbagai fitur yang teridentifikasi secara otomatis untuk setiap kategori produk yang Anda pilih.")
    selected_categories = df['product_category'].unique()

    for category in selected_categories:
        st.markdown(f"##### Fitur Produk untuk: **{category}**")
        df_cat = df[df['product_category'] == category]
        feature_defs = CLASSIFICATION_KEYWORDS.get(category, {}).get("features", {})
        if not feature_defs:
            st.warning(f"Tidak ada definisi fitur untuk kategori '{category}'.")
            continue

        feature_names = list(feature_defs.keys())
        num_cols = min(len(feature_names), 3) 
        if num_cols == 0: continue
        
        cols = st.columns(num_cols)
        for i, feature in enumerate(feature_names):
            with cols[i % num_cols]:
                analysis_df = df_cat[~df_cat[feature].isin(['Lainnya', 'Tidak Diketahui'])]
                if analysis_df.empty or len(analysis_df[feature].unique()) < 2:
                    st.write(f"**Distribusi {feature}**")
                    st.caption("Data tidak cukup untuk visualisasi.")
                    continue

                counts = analysis_df[feature].value_counts()
                fig = px.pie(counts, values=counts.values, names=counts.index, title=f"<b>Distribusi {feature}</b>", template='plotly_dark', color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(title_x=0.5, legend_title_text='', showlegend=True, margin=dict(l=20, r=20, t=50, b=20), height=400)
                fig.update_traces(textposition='inside', textinfo='percent+label', hole=.3)
                st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")

def display_noise_analysis_tab(full_df, selected_categories):
    """Menganalisis dan menampilkan data noise."""
    st.markdown('<h2 class="section-header">🗑️ Analisis Data Noise</h2>', unsafe_allow_html=True)
    st.info("Tab ini menganalisis produk yang terdeteksi sebagai 'noise' (tidak relevan).")
    if not selected_categories:
        st.warning("⚠️ Pilih setidaknya satu kategori produk di sidebar untuk memulai analisis noise.")
        return
        
    noise_df = full_df[(full_df['is_relevant_product'] == False) & (full_df['product_category'].isin(selected_categories))]

    if noise_df.empty:
        st.success("🎉 Tidak ada data noise yang terdeteksi untuk kategori yang dipilih.")
        return

    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("#### 🔍 Top 15 Keyword Noise Paling Sering Muncul")
        all_noise_keywords = noise_df['noise_keywords_found'].explode().dropna()
        if not all_noise_keywords.empty:
            top_keywords = all_noise_keywords.value_counts().nlargest(15)
            fig = px.bar(top_keywords, x=top_keywords.values, y=top_keywords.index, orientation='h', labels={'x': 'Frekuensi', 'y': 'Keyword Noise'}, color_discrete_sequence=['#ef4444'])
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
      st.markdown("#### 📋 Contoh Produk Noise")
      # Mengambil sampel acak dari data noise untuk ditampilkan
      for _, row in noise_df.sample(min(len(noise_df), 7)).iterrows():
          name = row['product_name']
          keywords = "".join([f'<span class="noise-keyword-tag">{k}</span>' for k in row['noise_keywords_found']])
          # Mengambil URL produk, dengan fallback '#' jika tidak ada
          product_url = row.get('product_url', '#')
          
          # Menambahkan link <a> di akhir konten kartu
          st.markdown(f"""
              <div class="noise-card">
                  <strong>{name}</strong>
                  <div style="font-size:0.8rem;color:#d1d5db;margin-top:4px;">Kategori: {row['product_category']}</div>
                  <div style="margin-top:8px;">{keywords}</div>
                  <a href="{product_url}" target="_blank" style="color: #42B883; font-size: 0.8rem; text-decoration: none; margin-top: 8px; display: block;">Lihat di Tokopedia 🔗</a>
              </div>
          """, unsafe_allow_html=True)

def display_seller_insights(df):
    """Menampilkan bagian Insight Bisnis untuk Seller Tokopedia."""
    if df.empty or 'price_per_kg' not in df.columns:
        return

    st.markdown('<h2 class="section-header">💡 Insight Bisnis untuk Seller Tokopedia</h2>', unsafe_allow_html=True)

    # Kalkulasi metrik harga dari data yang telah difilter
    price_min = df['price_per_kg'].min()
    price_max = df['price_per_kg'].max()
    price_median = df['price_per_kg'].median()

    col1, col2 = st.columns(2)

    with col1:
        # Kotak hijau kustom untuk Analisis Harga
        st.markdown(f"""
        <div style="background-color: rgba(16, 185, 129, 0.15); border-left: 5px solid #10b981; padding: 1.5rem; border-radius: 12px; height: 100%;">
            <h4 style="color: #6ee7b7; margin-top: 0; margin-bottom: 1rem;">🎯 Analisis Harga per KG</h4>
            <ul style="padding-left: 20px; list-style-position: outside;">
                <li><strong>Harga Terendah:</strong> Rp{int(price_min):,} /kg</li>
                <li><strong>Harga Tertinggi:</strong> Rp{int(price_max):,} /kg</li>
                <li><strong>Harga Tengah (Median):</strong> Rp{int(price_median):,} /kg</li>
            </ul>
            <p style="margin-top: 2rem; padding: 0.8rem; background: rgba(16, 185, 129, 0.2); border-radius: 8px; text-align: center;">
                <strong>Rekomendasi:</strong> Jual sekitar <strong>Rp{int(price_median):,}</strong> agar kompetitif.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Menggunakan class .insight-box yang sudah ada di style.css
        st.markdown("""
        <div class="insight-box" style="height: 100%;">
            <h4 style="color: #60a5fa;">💡 Cara Memanfaatkan Data</h4>
            <p>Gunakan data di samping untuk menyusun strategi penetapan harga yang efektif:</p>
            <ul style="padding-left: 20px; list-style-position: outside;">
                <li><b>Harga Terendah:</b> Gunakan sebagai patokan batas bawah agar tidak merugi.</li>
                <li><b>Harga Tertinggi:</b> Menunjukkan adanya potensi pasar untuk produk premium atau niche.</li>
                <li><b>Harga Tengah:</b> Titik harga paling umum dan diterima oleh mayoritas pasar.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
                 
  
def display_data_explorer_tab(df):
    """Menampilkan data mentah yang telah difilter dalam bentuk tabel."""
    st.markdown('<h2 class="section-header">🔬 Penjelajah Data</h2>', unsafe_allow_html=True)
    if df.empty:
        st.warning("⚠️ Tidak ada data untuk ditampilkan. Sesuaikan filter Anda.")
        return
    st.dataframe(df, use_container_width=True, height=600)

# FUNGSI UTAMA (MAIN)

def main():
    """Fungsi utama untuk menjalankan aplikasi Streamlit."""
    st.markdown('<h1 class="main-header">🥥 Dashboard Pasar Produk Kelapa & Gula Aren</h1>', unsafe_allow_html=True)

    # Memuat CSS dari file eksternal
    load_css('style.css')
    
    with st.spinner('Memuat dan memproses data... Ini mungkin memakan waktu beberapa saat.'):
        full_df = load_and_process_data()

    if full_df.empty:
        st.stop()

    filtered_df, selected_categories = setup_sidebar(full_df)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💾 Export Data")
    csv_data = convert_df_to_csv(filtered_df)
    st.sidebar.download_button(
        label="📥 Download sebagai CSV",
        data=csv_data,
        file_name=f"analisis_pasar_kelapa_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
        disabled=filtered_df.empty
    )

    tab_titles = [
        "🚀 Ringkasan Eksekutif", 
        "🔬 Analisis Sederhana",
        "🗑️ Data Noise",
        "💾 Dataset"
    ]
    tab1, tab2, tab3, tab4 = st.tabs(tab_titles)

    with tab1:
        display_summary_tab(filtered_df)
    with tab2:
        display_product_attribute_analysis(filtered_df)
    with tab3:
        display_noise_analysis_tab(full_df, selected_categories)
    with tab4:
        display_data_explorer_tab(filtered_df)
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 0.8rem;'>Dashboard dikembangkan oleh Hanif Fauzi Hakim. Data diambil dari platform E-commerce per Juli 2024.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()