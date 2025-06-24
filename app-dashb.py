import streamlit as st
import pandas as pd
import json
import re
from pathlib import Path
import plotly.express as px

st.set_page_config(
    page_title="Dasbor Analisis Produk Kelapa",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_and_process_data():
   
    
    base_path = Path(__file__).parent / 'data'

    files_to_load = {
        'Briket Kelapa': [base_path / 'cleaned_briket_kelapa.json'],
        'Gula Aren': [ 
            base_path / 'cleaned_gula_aren.json',
            base_path / 'cleaned_coconut_sugar.json'
        ],
        'Virgin Coconut Oil': [base_path / 'cleaned_virgin_coconut_oil.json']
    }
    
    df_list = []
    for category, file_paths in files_to_load.items():
        for path in file_paths:
            if not path.is_file():
                st.error(f"File tidak ditemukan: {path}. Pastikan struktur folder dan nama file sudah benar.")
                continue
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data: 
                        temp_df = pd.DataFrame(data)
                        temp_df['kategori'] = category
                        df_list.append(temp_df)
            except json.JSONDecodeError:
                st.warning(f"Gagal memproses file JSON: {path}. File mungkin rusak atau kosong.")
                continue

    if not df_list:
        return pd.DataFrame()

    df = pd.concat(df_list, ignore_index=True)

    for col in ['price_clean', 'sold_count_clean']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['product_name', 'price_clean', 'sold_count_clean'], inplace=True)
    df['sold_count_clean'] = df['sold_count_clean'].astype(int)
    
    def get_unit(name):
        name_lower = str(name).lower()
        
        patterns = {
            'kg': r'(\d+\.?\d*)\s*kg',
            'g': r'(\d+\.?\d*)\s*(g|gr)',
            'l': r'(\d+\.?\d*)\s*(l|liter)',
            'ml': r'(\d+\.?\d*)\s*ml'
        }
        
        weight_kg = 0
        vol_l = 0

        # Konversi ke KG
        for match in re.finditer(patterns['kg'], name_lower): weight_kg += float(match.group(1))
        for match in re.finditer(patterns['g'], name_lower): weight_kg += float(match.group(1)) / 1000
        
        # Konversi ke Liter
        for match in re.finditer(patterns['l'], name_lower): vol_l += float(match.group(1))
        for match in re.finditer(patterns['ml'], name_lower): vol_l += float(match.group(1)) / 1000

        return weight_kg if weight_kg > 0 else None, vol_l if vol_l > 0 else None

    df[['berat_kg', 'volume_l']] = df['product_name'].apply(lambda x: pd.Series(get_unit(x)))

    # Kalkulasi Harga per Unit
    df['harga_per_kg'] = df.apply(lambda row: row['price_clean'] / row['berat_kg'] if row['berat_kg'] else None, axis=1)
    df['harga_per_l'] = df.apply(lambda row: row['price_clean'] / row['volume_l'] if row['volume_l'] else None, axis=1)

    # Klasifikasi Produk
    df['is_organik'] = df['product_name'].str.contains('organik|organic', case=False, na=False)
    
    # Gula Aren
    df.loc[df['kategori'] == 'Gula Aren', 'bentuk_produk'] = 'Lainnya'
    df.loc[(df['kategori'] == 'Gula Aren') & df['product_name'].str.contains('cair|liquid|syrup', case=False, na=False), 'bentuk_produk'] = 'Cair'
    df.loc[(df['kategori'] == 'Gula Aren') & df['product_name'].str.contains('bubuk|powder|semut', case=False, na=False), 'bentuk_produk'] = 'Bubuk/Semut'
    df.loc[(df['kategori'] == 'Gula Aren') & df['product_name'].str.contains('batok|gandu|cetak', case=False, na=False), 'bentuk_produk'] = 'Batok/Cetak'

    # VCO
    df.loc[df['kategori'] == 'Virgin Coconut Oil', 'kegunaan_vco'] = 'Kesehatan/Umum'
    df.loc[(df['kategori'] == 'Virgin Coconut Oil') & df['product_name'].str.contains('mpasi|bayi|anak|baby|kids', case=False, na=False), 'kegunaan_vco'] = 'MPASI/Anak'
    df.loc[(df['kategori'] == 'Virgin Coconut Oil') & df['product_name'].str.contains('kucing|anjing|cat|dog|hewan|pet', case=False, na=False), 'kegunaan_vco'] = 'Hewan Peliharaan'
    
    return df

# --- Tampilan Utama Streamlit ---
st.title("📊 Dasbor Analisis Produk Kelapa di Tokopedia")
st.markdown("Dasbor interaktif untuk menganalisis data produk **Briket Kelapa**, **Gula Aren**, dan **Virgin Coconut Oil**.")

df = load_and_process_data()

if df.empty:
    st.error("Gagal memuat data. Tidak ada data untuk ditampilkan.")
else:
    st.sidebar.header("🔎 Filter Data")
    kategori_pilihan = st.sidebar.multiselect(
        "Pilih Kategori:",
        options=df['kategori'].unique(),
        default=df['kategori'].unique()
    )
    
    # Filter DataFrame berdasarkan pilihan di sidebar
    df_selection = df[df['kategori'].isin(kategori_pilihan)].copy()

    if df_selection.empty:
        st.warning("Silakan pilih minimal satu kategori untuk menampilkan data.")
    else:
        st.header("📈 Ringkasan Metrik Utama")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Produk Unik", f"{len(df_selection):,}")
        col2.metric("Total Unit Terjual", f"{int(df_selection['sold_count_clean'].sum()):,}")
        col3.metric("Rata-rata Harga", f"Rp {int(df_selection['price_clean'].mean()):,}")

        st.markdown("---")
        st.header("🏆 Analisis Popularitas Produk dan Toko")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Produk Terlaris")
            top_produk = df_selection.nlargest(10, 'sold_count_clean')
            fig = px.bar(top_produk, x='sold_count_clean', y='product_name', orientation='h', color='kategori',
                         labels={'sold_count_clean': 'Jumlah Terjual', 'product_name': ''}, text_auto='.2s',
                         title="Top 10 Produk Terlaris")
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Toko Terpopuler")
            top_toko = df_selection.groupby('shop_name')['sold_count_clean'].sum().nlargest(10).sort_values()
            fig = px.bar(top_toko, x=top_toko.values, y=top_toko.index, orientation='h',
                         labels={'x': 'Total Unit Terjual', 'y': ''}, text_auto='.2s',
                         title="Top 10 Toko Berdasarkan Penjualan")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.header("💰 Analisis Harga")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribusi Harga per Kategori")
            fig = px.box(df_selection, x='kategori', y='price_clean', color='kategori',
                         labels={'kategori': 'Kategori', 'price_clean': 'Harga (Rp)'})
            fig.update_yaxes(range=[0, df_selection['price_clean'].quantile(0.95)])
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Distribusi Harga per Unit Standar")
            df_unit_price = pd.concat([
                df_selection[['kategori', 'harga_per_kg']].rename(columns={'harga_per_kg': 'harga_per_unit'}).assign(unit='per KG'),
                df_selection[['kategori', 'harga_per_l']].rename(columns={'harga_per_l': 'harga_per_unit'}).assign(unit='per Liter')
            ]).dropna(subset=['harga_per_unit'])
            
            fig = px.box(df_unit_price, x='kategori', y='harga_per_unit', color='unit',
                         labels={'kategori': 'Kategori', 'harga_per_unit': 'Harga per Unit (Rp)', 'unit': 'Satuan'})
            fig.update_yaxes(range=[0, df_unit_price[df_unit_price['harga_per_unit'] < df_unit_price['harga_per_unit'].quantile(0.99)]['harga_per_unit'].quantile(0.95)]) # Improved outlier handling
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.header("🔬 Analisis Segmen Pasar")
        
        # Filter untuk memastikan tab hanya muncul jika ada data
        available_tabs = [cat for cat in ["Gula Aren", "Virgin Coconut Oil", "Briket Kelapa"] if cat in df_selection['kategori'].unique()]
        
        if available_tabs:
            tabs = st.tabs(available_tabs)
            for i, tab_name in enumerate(available_tabs):
                with tabs[i]:
                    if tab_name == 'Gula Aren':
                        col1, col2 = st.columns(2)
                        with col1:
                            bentuk_counts = df_selection[df_selection['kategori'] == 'Gula Aren']['bentuk_produk'].value_counts()
                            fig = px.pie(values=bentuk_counts.values, names=bentuk_counts.index, title="Proporsi Bentuk Produk Gula Aren")
                            st.plotly_chart(fig, use_container_width=True)
                        with col2:
                            organik_price = df_selection[df_selection['kategori'] == 'Gula Aren'].groupby('is_organik')['price_clean'].mean().reset_index()
                            organik_price['is_organik'] = organik_price['is_organik'].map({True: 'Organik', False: 'Non-Organik'})
                            fig = px.bar(organik_price, x='is_organik', y='price_clean', color='is_organik',
                                         title="Harga Rata-rata: Organik vs Non-Organik",
                                         labels={'is_organik': 'Klaim', 'price_clean': 'Harga Rata-rata (Rp)'}, text_auto=True)
                            st.plotly_chart(fig, use_container_width=True)
                    
                    elif tab_name == 'Virgin Coconut Oil':
                        vco_counts = df_selection[df_selection['kategori'] == 'Virgin Coconut Oil']['kegunaan_vco'].value_counts()
                        fig = px.pie(values=vco_counts.values, names=vco_counts.index, title="Proporsi Pasar VCO Berdasarkan Kegunaan")
                        st.plotly_chart(fig, use_container_width=True)
                        
                    elif tab_name == 'Briket Kelapa':
                        df_briket_segment = df_selection[df_selection['kategori'] == 'Briket Kelapa']
                        bbq_count = df_briket_segment['product_name'].str.contains('bbq', case=False).sum()
                        shisha_count = df_briket_segment['product_name'].str.contains('shisha', case=False).sum()
                        kegunaan_briket = pd.DataFrame({'Kegunaan': ['BBQ', 'Shisha'], 'Jumlah': [bbq_count, shisha_count]})
                        if kegunaan_briket['Jumlah'].sum() > 0:
                            fig = px.pie(kegunaan_briket, values='Jumlah', names='Kegunaan', title="Penyebutan Kegunaan Briket (BBQ vs Shisha)")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Tidak ditemukan kata kunci 'BBQ' atau 'Shisha' pada nama produk briket yang difilter.")

        with st.expander("Lihat Data Lengkap yang Telah Diolah"):
            st.dataframe(df_selection)