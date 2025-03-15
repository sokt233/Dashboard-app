import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import geopandas as gpd

# Set style seaborn
sns.set(style='dark')

# Load data
all_df = pd.read_csv('all_data.csv')

# Konversi kolom tanggal ke datetime
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# Sidebar untuk filter data
st.sidebar.header('Rangkuman')

# Filter Rentang Harga
min_price, max_price = st.sidebar.slider('Rentang Harga (R$)', 
                                         float(all_df['price'].min()), 
                                         float(all_df['price'].max()), 
                                         (float(all_df['price'].min()), float(all_df['price'].max())))

# Terapkan Filter
filtered_df = all_df[
    (all_df['price'].between(min_price, max_price))
]

st.sidebar.metric('Total Transaksi', f"{len(filtered_df):,}")
st.sidebar.metric('Total Revenue', f"R$ {filtered_df['payment_value'].sum():,.2f}")
st.sidebar.metric('Rata-rata Harga', f"R$ {filtered_df['price'].mean():,.2f}")


# Header dashboard
st.title('E-Commerce Dashboard')
st.markdown("""
    Dashboard ini visual analisis dari penjualan, pelanggan, dan produk dari data e-commerce. Bentuk utama dari visual ini bisa dilihat pada [link ini](https://colab.research.google.com/drive/13QyUb3k8VCP4tCl4pAdQR37EEcZ72bRB?usp=sharing).
""")

# Distribusi Harga Produk
if 'order_purchase_timestamp' in all_df.columns:
    st.header('Distribusi Harga Produk')
    all_df['order_date'] = pd.to_datetime(all_df['order_purchase_timestamp'])
    average_price = all_df['price'].mean()
    st.write(f"Rata-rata harga produk: {average_price:.2f}")
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    sns.boxplot(y=all_df['price'], color='skyblue', ax=axes[0, 0])
    axes[0, 0].set_title('Boxplot Harga Produk')
    axes[0, 0].set_ylabel('Harga')
    axes[0, 0].axhline(average_price, color='red', linestyle='--', label=f'Rata-rata: {average_price:.2f}')
    axes[0, 0].legend()
    
    sns.violinplot(y=all_df['price'], color='lightgreen', ax=axes[0, 1])
    axes[0, 1].set_title('Violin Plot Harga Produk')
    axes[0, 1].set_ylabel('Harga')
    axes[0, 1].axhline(average_price, color='red', linestyle='--')
    
    sns.kdeplot(all_df['price'], fill=True, color='salmon', ax=axes[1, 0])
    axes[1, 0].axvline(average_price, color='black', linestyle='--', label=f'Rata-rata: {average_price:.2f}')
    axes[1, 0].set_title('KDE Plot Harga Produk')
    axes[1, 0].set_xlabel('Harga')
    axes[1, 0].set_ylabel('Density')
    axes[1, 0].legend()
    
    sns.ecdfplot(all_df['price'], color='purple', ax=axes[1, 1])
    axes[1, 1].axvline(average_price, color='red', linestyle='--', label=f'Rata-rata: {average_price:.2f}')
    axes[1, 1].set_title('ECDF Plot Harga Produk')
    axes[1, 1].set_xlabel('Harga')
    axes[1, 1].set_ylabel('Proporsi Kumulatif')
    axes[1, 1].legend()
    
    plt.tight_layout()
    st.pyplot(fig)

st.header('Pertanyaan pertama - Bagaimanakah tren revenue penjualan selama perusahaan berdiri?')
def load_data():
    all_df = pd.read_csv('all_data.csv')  # Ganti dengan nama file yang benar
    all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])
    return all_df

# Ekstrak bulan dari order_purchase_timestamp
all_df['order_purchase_month'] = all_df['order_purchase_timestamp'].dt.to_period('M')

# Groupby bulan dan hitung total revenue
total_revenue_by_month = all_df.groupby('order_purchase_month')['payment_value'].sum().reset_index()
total_revenue_by_month['order_purchase_month'] = total_revenue_by_month['order_purchase_month'].astype(str)

# **1️⃣ Total Revenue Selama Produksi**
st.header("📊 Total Revenue Selama Produksi")

# Buat visualisasi
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(total_revenue_by_month['order_purchase_month'], 
              total_revenue_by_month['payment_value'],
              color='skyblue', edgecolor='navy')

# Tambahkan nilai di atas setiap bar
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 0.02*max(total_revenue_by_month['payment_value']),
            f'{height:.1f}', ha='center', fontsize=8)

# Tambahkan garis trend
ax.plot(total_revenue_by_month['order_purchase_month'], 
        total_revenue_by_month['payment_value'], 'r--', linewidth=2)

# Styling
ax.set_title('Total Revenue selama produksi', fontsize=14, fontweight='bold')
ax.set_xlabel('Waktu produksi', fontsize=12)
ax.set_ylabel('Total Revenue (R$)', fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Anotasi nilai tertinggi dan terendah
max_revenue = total_revenue_by_month['payment_value'].max()
min_revenue = total_revenue_by_month['payment_value'].min()
max_month = total_revenue_by_month.loc[total_revenue_by_month['payment_value'] == max_revenue, 'order_purchase_month'].iloc[0]
min_month = total_revenue_by_month.loc[total_revenue_by_month['payment_value'] == min_revenue, 'order_purchase_month'].iloc[0]

ax.annotate(f'Tertinggi: {max_revenue:.1f}', 
            xy=(max_month, max_revenue), xytext=(0, 15),
            textcoords='offset points', ha='center',
            arrowprops=dict(arrowstyle='->', color='green'))

ax.annotate(f'Terendah: {min_revenue:.1f}', 
            xy=(min_month, min_revenue), xytext=(0, -25),
            textcoords='offset points', ha='center',
            arrowprops=dict(arrowstyle='->', color='red'))

st.pyplot(fig)

# **2️⃣ Distribusi Revenue - Scatter Plot**
st.header("📌 Distribusi Revenue - Scatter Plot")

# Scatter plot harga produk berdasarkan waktu
if 'order_purchase_timestamp' in all_df.columns and 'price' in all_df.columns:
    fig, ax = plt.subplots(figsize=(10, 6))
    all_df['order_date'] = pd.to_datetime(all_df['order_purchase_timestamp'])

    ax.scatter(all_df['order_date'], all_df['price'], alpha=0.5, s=10)

    # Rata-rata harga produk
    average_price = all_df['price'].mean()
    ax.axhline(average_price, color='red', linestyle='--', label=f'Rata-rata: {average_price:.2f}')

    ax.set_title('Distribusi Revenue - Scatter Plot', fontsize=14, fontweight='bold')
    ax.set_xlabel('Waktu Produksi', fontsize=12)
    ax.set_ylabel('Harga', fontsize=12)
    ax.legend()
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig)

st.header('Pertanyaan kedua - Apa Kategori Produk dengan Revenue Tertinggi')
# Load dataset
def load_data():
    all_df = pd.read_csv('all_data.csv')  # Ganti dengan nama file yang benar
    return all_df

all_df = load_data()

# **1️⃣ Top 12 Kategori Produk dengan Revenue Tertinggi**
st.header("🔝Top 12 Kategori Produk dengan Revenue Tertinggi")

# Groupby kategori produk dan hitung total revenue
revenue_by_category = all_df.groupby('product_category_name')['payment_value'].sum().reset_index()

# Urutkan berdasarkan revenue tertinggi
revenue_by_category = revenue_by_category.sort_values(by='payment_value', ascending=False)

# Menampilkan data di Streamlit
st.dataframe(revenue_by_category.head(12))

# **Visualisasi Bar Chart**
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    x=revenue_by_category.head(12)['payment_value'], 
    y=revenue_by_category.head(12)['product_category_name'], 
    palette='coolwarm',
    ax=ax
)

ax.set_title('Top 12 Kategori Produk dengan Revenue Tertinggi', fontsize=16, fontweight='bold')
ax.set_xlabel('Total Revenue', fontsize=14)
ax.set_ylabel('Kategori Produk', fontsize=14)

st.pyplot(fig)

st.header('Pertanyaan ketiga - Persebaran wilayah manakah dengan Distribusi customer/pelanggan tertinggi?')
all_df = load_data()

# **1️⃣ Distribusi Pelanggan Berdasarkan 10 Kota Teratas**
st.header("🏙️ Distribusi Pelanggan Berdasarkan 10 Kota Teratas")

# Hitung persentase pelanggan berdasarkan kota
city_distribution = all_df['customer_city'].value_counts(normalize=True).head(10) * 100

# Buat stem plot dengan angka yang ditampilkan secara jelas
fig, ax = plt.subplots(figsize=(12, 8))

# Buat stem plot
markerline, stemlines, baseline = ax.stem(
    city_distribution.index, 
    city_distribution.values, 
    basefmt=" ", 
    linefmt='C0-', 
    markerfmt='ro'
)

# Kustomisasi visual
plt.setp(markerline, markersize=10)
plt.setp(stemlines, linewidth=2)

# Tambahkan label persentase di atas setiap marker
for i, value in enumerate(city_distribution.values):
    ax.text(i, value + 0.5, f'{value:.1f}%', 
            ha='center', va='bottom', 
            fontweight='bold', fontsize=10)

# Tambahkan informasi count (jumlah absolut) di bawah nama kota
counts = all_df['customer_city'].value_counts().head(10)
for i, (city, count) in enumerate(counts.items()):
    ax.text(i, -1.5, f'n={count}', 
            ha='center', va='top', 
            fontsize=9, color='navy')

# Styling
ax.set_title('Distribusi Pelanggan Berdasarkan 10 Kota Teratas', fontsize=16, fontweight='bold')
ax.set_xlabel('')
ax.set_ylabel('Persentase Pelanggan (%)', fontsize=14)
ax.set_xticks(range(len(city_distribution.index)))
ax.set_xticklabels(city_distribution.index, rotation=45, ha='right')
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Tambahkan informasi total pelanggan sebagai catatan
total_customers = len(all_df['customer_id'].unique())
fig.text(0.5, 0.01, f'Total Pelanggan: {total_customers:,}', 
         ha='center', fontsize=12, bbox=dict(facecolor='lightgray', alpha=0.5))

# Rentang y-axis dimulai dari sedikit di bawah 0 untuk mengakomodasi label count
ax.set_ylim(-2, max(city_distribution.values) + 3)

plt.tight_layout()

# **Tampilkan plot di Streamlit**
st.pyplot(fig)

# Visualisasi Geospatial
st.header('Analisis Lanjutan - GeoSpatial Analysis')

# Load dataset geolokasi
def load_data():
    geolocation_data = pd.read_csv('geolocation_dataset.csv')
    customers = pd.read_csv('customers_dataset.csv')  # Sesuaikan dengan dataset Anda
    return geolocation_data, customers

# Load data
geolocation_data, customers = load_data()

# Gabungkan data berdasarkan customer_zip_code_prefix
merged_data = pd.merge(
    customers,
    geolocation_data,
    left_on='customer_zip_code_prefix',
    right_on='geolocation_zip_code_prefix',
    how='left'
)

# Hitung jumlah pelanggan per kota
customer_distribution = merged_data.groupby('customer_city')['customer_unique_id'].nunique().reset_index()

# Gabungkan dengan data geolokasi untuk mendapatkan latitude dan longitude
geolocation_data_city = merged_data[['customer_city', 'geolocation_lat', 'geolocation_lng']].drop_duplicates()
customer_distribution = pd.merge(customer_distribution, geolocation_data_city, on='customer_city')

# Buat GeoDataFrame
gdf = gpd.GeoDataFrame(
    customer_distribution,
    geometry=gpd.points_from_xy(customer_distribution['geolocation_lng'], customer_distribution['geolocation_lat'])
)

# Load data peta dunia
world = gpd.read_file('ne_110m_admin_0_countries.shp').to_crs(epsg=4326)

# Streamlit Header
st.header("🗺️ Distribusi Pelanggan pada Peta Dunia")

# Plot peta
fig, ax = plt.subplots(figsize=(15, 8))
world.plot(ax=ax, color='#d9d9d9', edgecolor='black')
ax.scatter(gdf['geolocation_lng'], gdf['geolocation_lat'], color='blue', s=10, alpha=0.7)

# Tambahkan keterangan
plt.title('Distribusi Pelanggan pada Peta Dunia', fontsize=16)
plt.xlabel('Longitude', fontsize=14)
plt.ylabel('Latitude', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.5)

# Tampilkan plot di Streamlit
st.pyplot(fig)

# Footer
st.caption('Copyright © 2025 by Gratia Yudika Morado Silalahi - MC006D5Y1788')