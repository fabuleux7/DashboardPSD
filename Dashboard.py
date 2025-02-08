import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from streamlit_option_menu import option_menu

@st.cache_data
def load_data(filename):
    return pd.read_csv(filename)

# Load semua dataset dari file lokal
df_customers = load_data("customers_dataset.csv")
df_geolocation = load_data("geolocation_dataset.csv")
df_order_items = load_data("order_items_dataset.csv")
df_order_payments = load_data("order_payments_dataset.csv")
df_order_reviews = load_data("order_reviews_dataset.csv")
df_orders = load_data("orders_dataset.csv")
df_product_category_translation = load_data("product_category_name_translation.csv")
df_products = load_data("products_dataset.csv")
df_sellers = load_data("sellers_dataset.csv")

# **Fungsi utama untuk menggabungkan dataset dan melakukan analisis**
def Analisis_Kepuasan():
    global keterlambatan_vs_review, produk_vs_review, pembayaran_vs_review, kategori_vs_review  # Buat variabel global agar bisa dipakai di fungsi lain

    # Menggabungkan dataset yang relevan
    df_merged = df_orders.merge(df_order_reviews, on='order_id', how='inner')
    df_merged = df_merged.merge(df_order_items, on='order_id', how='inner')
    df_merged = df_merged.merge(df_order_payments, on='order_id', how='inner')
    df_merged = df_merged.merge(df_products, on='product_id', how='left')

    # Konversi tanggal ke format datetime
    df_merged['order_delivered_customer_date'] = pd.to_datetime(df_merged['order_delivered_customer_date'])
    df_merged['order_estimated_delivery_date'] = pd.to_datetime(df_merged['order_estimated_delivery_date'])

    # Menghitung keterlambatan pengiriman
    df_merged['Terlambat'] = np.where(df_merged['order_delivered_customer_date'] > df_merged['order_estimated_delivery_date'], 1, 0)

    # Menghitung jumlah produk dalam pesanan
    df_merged['Jumlah Produk'] = df_merged.groupby('order_id')['order_item_id'].transform('count')

    # Analisis keterlambatan terhadap review
    keterlambatan_vs_review = df_merged.groupby('Terlambat')['review_score'].mean().reset_index()

    # Analisis jumlah produk terhadap review
    produk_vs_review = df_merged.groupby('Jumlah Produk')['review_score'].mean().reset_index()

    # Analisis metode pembayaran terhadap review
    pembayaran_vs_review = df_merged.groupby('payment_type')['review_score'].mean().reset_index()

    # Analisis kategori produk terhadap review
    kategori_vs_review = df_merged.groupby('product_category_name')['review_score'].mean().reset_index()

#CASE 1

# **1. Distribusi Skor Review**
def distribusi_review():
    st.header("Distribusi Skor Review")
    st.dataframe(df_order_reviews['review_score'].value_counts().reset_index().rename(columns={'index': 'Review Score', 'review_score': 'Jumlah'}))

    fig, ax = plt.subplots(figsize=(8,5))
    sns.countplot(x=df_order_reviews['review_score'], palette="viridis", ax=ax)
    ax.set_xlabel("Review Score")
    ax.set_ylabel("Jumlah Ulasan")
    ax.set_title("Distribusi Skor Review")
    st.pyplot(fig)

# **2. Pengaruh Keterlambatan Pengiriman terhadap Review Score**
def keterlambatan_vs_review_score():
    st.header("Pengaruh Keterlambatan Pengiriman terhadap Kepuasan Pelanggan")
    st.dataframe(keterlambatan_vs_review)

    fig, ax = plt.subplots(figsize=(6,4))
    sns.barplot(x=['Tepat Waktu', 'Terlambat'], y=keterlambatan_vs_review['review_score'], palette=['green', 'red'], ax=ax)
    ax.set_ylabel("Rata-rata Skor Review")
    ax.set_title("Pengaruh Keterlambatan Pengiriman terhadap Kepuasan Pelanggan")
    st.pyplot(fig)

# **3. Pengaruh Jumlah Produk dalam Pesanan terhadap Review Score**
def jumlah_produk_vs_review():
    st.header("Pengaruh Jumlah Produk dalam Pesanan terhadap Kepuasan Pelanggan")
    st.dataframe(produk_vs_review)

    fig, ax = plt.subplots(figsize=(8,5))
    sns.lineplot(x=produk_vs_review['Jumlah Produk'], y=produk_vs_review['review_score'], marker='o', ax=ax)
    ax.set_xlabel("Jumlah Produk dalam Pesanan")
    ax.set_ylabel("Rata-rata Skor Review")
    ax.set_title("Jumlah Produk dalam Pesanan vs Kepuasan Pelanggan")
    st.pyplot(fig)

# **4. Pengaruh Metode Pembayaran terhadap Review Score**
def metode_pembayaran_vs_review():
    st.header("Pengaruh Metode Pembayaran terhadap Kepuasan Pelanggan")
    st.dataframe(pembayaran_vs_review)

    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(x=pembayaran_vs_review['payment_type'], y=pembayaran_vs_review['review_score'], palette="magma", ax=ax)
    ax.set_xlabel("Metode Pembayaran")
    ax.set_ylabel("Rata-rata Skor Review")
    ax.set_title("Metode Pembayaran vs Kepuasan Pelanggan")
    plt.xticks(rotation=45)
    st.pyplot(fig)

# **5. Pengaruh Kategori Produk terhadap Review Score**
def kategori_produk_vs_review():
    st.header("Pengaruh Kategori Produk terhadap Kepuasan Pelanggan")
    top_10_kategori = kategori_vs_review.sort_values(by='review_score', ascending=False).head(10)
    bottom_10_kategori = kategori_vs_review.sort_values(by='review_score', ascending=True).head(10)

    st.subheader("Top 10 Kategori Produk dengan Kepuasan Tertinggi")
    st.dataframe(top_10_kategori)

    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(y=top_10_kategori['product_category_name'], x=top_10_kategori['review_score'], palette="coolwarm", ax=ax)
    ax.set_xlabel("Rata-rata Skor Review")
    ax.set_ylabel("Kategori Produk")
    ax.set_title(" 10 Kategori Produk dengan Kepuasan Tertinggi")
    st.pyplot(fig)

    st.subheader(" 10 Kategori Produk dengan Kepuasan Terendah")
    st.dataframe(bottom_10_kategori)

    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(y=bottom_10_kategori['product_category_name'], x=bottom_10_kategori['review_score'], palette="coolwarm_r", ax=ax)
    ax.set_xlabel("Rata-rata Skor Review")
    ax.set_ylabel("Kategori Produk")
    ax.set_title("Bottom 10 Kategori Produk dengan Kepuasan Terendah")
    st.pyplot(fig)

# CASE 2
def Analisis_Pola_Pembelian():
    st.header("Analisis Pola Pembelian Pelanggan")

    # Menghitung jumlah pesanan per pelanggan
    df_customer_orders = df_orders.groupby('customer_id').size().reset_index(name='Total_Pesanan')
    top_customers = df_customer_orders.sort_values(by='Total_Pesanan', ascending=False).head(10)

    # Menghitung rata-rata jumlah barang per pelanggan
    df_order_items_merged = df_order_items.merge(df_orders[['order_id', 'customer_id']], on='order_id', how='left')
    df_customer_items = df_order_items_merged.groupby('customer_id')['order_item_id'].count().reset_index(name='Total_Barang')
    avg_items_per_customer = df_customer_items['Total_Barang'].mean()

    # Visualisasi 1: Distribusi pesanan per pelanggan
    fig, ax = plt.subplots(figsize=(8,5))
    sns.histplot(df_customer_orders['Total_Pesanan'], bins=30, kde=True, color='blue', ax=ax)
    ax.set_xlabel("Jumlah Pesanan per Pelanggan")
    ax.set_ylabel("Jumlah Pelanggan")
    ax.set_title("Distribusi Jumlah Pesanan per Pelanggan")
    st.pyplot(fig)

    # Visualisasi 2: Top 10 pelanggan dengan pesanan terbanyak
    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(y=top_customers['customer_id'], x=top_customers['Total_Pesanan'], palette="coolwarm", ax=ax)
    ax.set_xlabel("Total Pesanan")
    ax.set_ylabel("Customer ID")
    ax.set_title("Top 10 Pelanggan dengan Pesanan Terbanyak")
    st.pyplot(fig)

def Analisis_Penjual():
    st.header("Analisis Penjual (Sellers)")

    # Menghitung jumlah penjual per kota
    df_seller_city = df_sellers['seller_city'].value_counts().reset_index()
    df_seller_city.columns = ['Kota', 'Jumlah_Penjual']

    # Rata-rata rating per penjual
    df_seller_reviews = df_order_reviews.merge(df_order_items, on='order_id', how='inner')
    df_seller_reviews = df_seller_reviews.groupby('seller_id')['review_score'].mean().reset_index()
    df_seller_reviews.columns = ['Seller_ID', 'Rata_Rata_Review']

    # Penjual dengan transaksi terbanyak
    df_seller_orders = df_order_items.groupby('seller_id').size().reset_index(name='Total_Transaksi')
    top_sellers = df_seller_orders.sort_values(by='Total_Transaksi', ascending=False).head(10)

    # Visualisasi 1: Kota dengan jumlah penjual terbanyak
    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(y=df_seller_city['Kota'][:10], x=df_seller_city['Jumlah_Penjual'][:10], palette="magma", ax=ax)
    ax.set_xlabel("Jumlah Penjual")
    ax.set_ylabel("Kota")
    ax.set_title("Top 10 Kota dengan Jumlah Penjual Terbanyak")
    st.pyplot(fig)

    # Visualisasi 2: Penjual dengan transaksi terbanyak
    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(y=top_sellers['seller_id'], x=top_sellers['Total_Transaksi'], palette="viridis", ax=ax)
    ax.set_xlabel("Total Transaksi")
    ax.set_ylabel("Seller ID")
    ax.set_title("Top 10 Penjual dengan Transaksi Terbanyak")
    st.pyplot(fig)

#Case 3
# **CASE 3: Produk dengan Ulasan Terbanyak**
def Produk_Terbanyak_Ulasan():
    

    # Menghitung jumlah ulasan per produk
    df_product_reviews = df_order_reviews.merge(df_order_items, on='order_id', how='inner')
    df_product_reviews = df_product_reviews.groupby('product_id').size().reset_index(name='Total_Ulasan')

    # Menggabungkan dengan dataset produk untuk mendapatkan nama produk
    df_product_reviews = df_product_reviews.merge(df_products[['product_id', 'product_category_name']], on='product_id', how='left')

    # Mengurutkan produk berdasarkan jumlah ulasan terbanyak
    top_reviewed_products = df_product_reviews.sort_values(by='Total_Ulasan', ascending=False).head(10)

    # Menampilkan tabel hasil analisis
    st.dataframe(top_reviewed_products)

    # Visualisasi: Produk dengan jumlah ulasan terbanyak
    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(y=top_reviewed_products['product_category_name'], x=top_reviewed_products['Total_Ulasan'], palette="coolwarm", ax=ax)
    ax.set_xlabel("Total Ulasan")
    ax.set_ylabel("Kategori Produk")
    ax.set_title("Top 10 Produk dengan Ulasan Terbanyak")
    st.pyplot(fig)

#Case 4 
# **CASE 4: Analisis Pengaruh Rating Produk terhadap Penjualan**
def Analisis_Rating_vs_Penjualan():
    

    # Menggabungkan dataset review dengan order items
    df_rating_sales = df_order_reviews.merge(df_order_items, on='order_id', how='inner')

    # Menghitung rata-rata rating per produk
    df_avg_rating = df_rating_sales.groupby('product_id')['review_score'].mean().reset_index()
    df_avg_rating.columns = ['product_id', 'Rata_Rata_Rating']

    # Menghitung jumlah penjualan per produk
    df_sales = df_rating_sales.groupby('product_id').size().reset_index(name='Total_Penjualan')

    # Menggabungkan rating dengan penjualan
    df_rating_sales_analysis = df_avg_rating.merge(df_sales, on='product_id', how='left')

    # Menghubungkan dengan kategori produk
    df_rating_sales_analysis = df_rating_sales_analysis.merge(df_products[['product_id', 'product_category_name']], on='product_id', how='left')

    # Menampilkan tabel hasil analisis
    st.dataframe(df_rating_sales_analysis.head(20))

    # Visualisasi 1: Scatter Plot Rating vs Total Penjualan
    fig, ax = plt.subplots(figsize=(10,5))
    sns.scatterplot(x=df_rating_sales_analysis['Rata_Rata_Rating'], y=df_rating_sales_analysis['Total_Penjualan'], alpha=0.7)
    ax.set_xlabel("Rata-rata Rating Produk")
    ax.set_ylabel("Total Penjualan")
    ax.set_title("Pengaruh Rating Produk terhadap Penjualan")
    st.pyplot(fig)

    # Visualisasi 2: Top 10 Produk Berdasarkan Rating
    top_rated_products = df_rating_sales_analysis.sort_values(by='Rata_Rata_Rating', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(y=top_rated_products['product_category_name'], x=top_rated_products['Rata_Rata_Rating'], palette="coolwarm", ax=ax)
    ax.set_xlabel("Rata-rata Rating")
    ax.set_ylabel("Kategori Produk")
    ax.set_title("Top 10 Produk dengan Rating Tertinggi")
    st.pyplot(fig)

# Case 5
def Analisis_Metode_Pembayaran():

    # Menghitung jumlah penggunaan metode pembayaran
    df_payment_count = df_order_payments['payment_type'].value_counts().reset_index()
    df_payment_count.columns = ['Metode_Pembayaran', 'Jumlah_Transaksi']

    # Menampilkan tabel hasil analisis
    st.dataframe(df_payment_count)

    # Visualisasi: Metode pembayaran paling sering digunakan
    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(x=df_payment_count['Metode_Pembayaran'], y=df_payment_count['Jumlah_Transaksi'], palette="coolwarm", ax=ax)
    ax.set_xlabel("Metode Pembayaran")
    ax.set_ylabel("Jumlah Transaksi")
    ax.set_title("Metode Pembayaran Paling Sering Digunakan")
    plt.xticks(rotation=45)
    st.pyplot(fig)


# **🔹 Sidebar Menu untuk Memilih Analisis**
with st.sidebar:
    selected = option_menu(
        'Analisis Data', ['CASE 1', 'CASE 2', 'CASE 3', 'CASE 4', "CASE 5",], 
        icons=["easel2", "clipboard-check", "star", "bar-chart", "credit-card"],
        menu_icon="cast",
        default_index=0
    )

if selected == 'CASE 1':
    st.header("Faktor-Faktor yang Mempengaruhi Kepuasan Pelanggan dalam E-commerce")
    
    # Jalankan analisis kepuasan agar variabel global terisi
    Analisis_Kepuasan()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Distribusi Review", "Waktu Pengiriman", "Produk", "Metode Pembayaran", "Kategori Produk"])
    with tab1:
        distribusi_review()
    with tab2:
        keterlambatan_vs_review_score()
    with tab3:
        jumlah_produk_vs_review()
    with tab4:
        metode_pembayaran_vs_review()
    with tab5:
        kategori_produk_vs_review()

elif selected == 'CASE 2':
    st.header("Analisis Pola Pembelian dan Penjual dalam E-Commerce")
    
    tab1, tab2 = st.tabs(["Pola Pembelian Pelanggan", "Analisis Penjual"])
    with tab1:
        Analisis_Pola_Pembelian()
    with tab2:
        Analisis_Penjual()

elif selected == 'CASE 3':
    st.header("Produk dengan Ulasan Terbanyak")
    Produk_Terbanyak_Ulasan()

elif selected == 'CASE 4':
    st.header("Analisis Pengaruh Rating Produk terhadap Penjualan")
    Analisis_Rating_vs_Penjualan()

elif selected == 'CASE 5':
    st.header("Metode Pembayaran yang Paling Sering Digunakan")
    Analisis_Metode_Pembayaran()

   

    