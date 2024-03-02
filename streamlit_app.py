import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plost
import seaborn as sns
import numpy as np
import matplotlib.dates as mdates

palet_warna = {
    'A': '#073365',  
    'B': '#81b8df',  
    'C': '#fe2f2f',  
    'D': '#ffb4b4',  
    'E': '#32b2a1',  
}

def get_colors_for_selected_products(selected_products):
    return [palet_warna[product] for product in selected_products if product in palet_warna]

df_transaksi = pd.read_csv('datatransaksi2023.csv', sep=';')
df_transaksi['Date'] = pd.to_datetime(df_transaksi['Date'], format='%d/%m/%Y')
df_produk = pd.read_csv('dataproduk2023.csv', sep=';')
df_user = pd.read_csv('datauser2023.csv', sep=',')


st.set_page_config(layout='wide', initial_sidebar_state='expanded')
st.sidebar.header('Dashboard Monitoring dan Ecommerce Analysis')

st.sidebar.subheader('Produk yang akan dianalisis')
plot_data_product_quantity = st.sidebar.multiselect('Pilih Produk', ['A', 'B', 'C', 'D', 'E'], ['A', 'B', 'C', 'D', 'E'])

if len(plot_data_product_quantity) > 0:
    st.markdown('<div style="text-align: center;"><h3>Performa Penjualan Produk</h3></div>', unsafe_allow_html=True)

    col1_row1, col2_row1 = st.columns(2)
    with col1_row1:
        ### Line Chart untuk menampilkan perkembangan jumlah penjualan produk seiring waktu
        st.markdown('<div style="text-align: center;">Perkembangan Penjualan Produk seiring Waktu</div>', unsafe_allow_html=True)
        df_pivot_transaksi = df_transaksi.pivot_table(index='Date', columns='Product_ID', values='Quantity', fill_value=0)
        df_pivot_transaksi_resample = df_pivot_transaksi.resample('2W').sum()
        df_pivot_transaksi_resample_values = df_pivot_transaksi_resample[plot_data_product_quantity]
        # st.line_chart(df_pivot_transaksi_resample_values, use_container_width=True)
        fig, ax = plt.subplots(figsize=(10, 6))

        # Iterasi melalui setiap kolom pada DataFrame dan membuat line plot untuk setiap satu
        for product_id in df_pivot_transaksi_resample_values.columns:
            ax.plot(df_pivot_transaksi_resample_values.index, df_pivot_transaksi_resample_values[product_id], label=product_id, color=palet_warna.get(product_id, '#333333'), linewidth=2)

        # Menambahkan judul dan label
        ax.set_xlabel('Tanggal', fontsize=12)
        ax.set_ylabel('Total Penjualan', fontsize=12)

        # Menyesuaikan format sumbu x untuk menampilkan tanggal dengan lebih baik
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        plt.xticks(rotation=45)

        # Menambahkan legenda
        ax.legend(title='Product ID')

        # Menambahkan grid
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)

        # Menampilkan plot
        plt.tight_layout()
        st.pyplot(fig)
        #####################
    with col2_row1:
        ### Line Chart untuk menampilkan total pendapatan produk per bulan
        st.markdown('<div style="text-align: center;">Total Pendapatan Produk per Bulan</div>', unsafe_allow_html=True)
        df_transaksi['Month'] = df_transaksi['Date'].dt.month
        df_produk = df_produk.rename(columns={'PRODUCT_ID': 'Product_ID'})
        df_produk['Product_ID'] = df_produk['Product_ID'].str.upper()
        df_transaksi_produk = pd.merge(df_transaksi, df_produk, on='Product_ID', how='left')
        df_transaksi_produk['Total Pendapatan'] = df_transaksi_produk['Quantity'] * df_transaksi_produk['HARGA_SATUAN']
        df_transaksi_produk.drop(columns=['HARGA_SATUAN', 'JUMLAH_DIGUDANG', 'HARUS_RESTOCK_BILA_JUMLAH_GUDANG_TERSISA'], inplace=True)
        pendapatan_produk_bulan = df_transaksi_produk.groupby(['Product_ID', 'Month'])['Total Pendapatan'].sum().reset_index()
        pendapatan_produk_bulan['Month'] = pd.Categorical(pendapatan_produk_bulan['Month'], categories=[1, 2, 3, 4], ordered=True)
        pendapatan_produk_bulan['Month'] = pendapatan_produk_bulan['Month'].cat.rename_categories({
            1 : 'Januari',
            2 : 'Februari',
            3 : 'Maret',
            4 : 'April'
        })

        pivot_pendapatan_produk_bulan = pendapatan_produk_bulan.pivot(index='Month', columns='Product_ID', values='Total Pendapatan')
        pivot_pendapatan_produk_bulan_filtered = pivot_pendapatan_produk_bulan[plot_data_product_quantity]

        warna_kolom = [palet_warna[product] for product in pivot_pendapatan_produk_bulan_filtered.columns if product in palet_warna]
        plt.figure(figsize=(10, 6))
        pivot_pendapatan_produk_bulan_filtered.plot(kind='bar', stacked=False, ax=plt.gca(), color=warna_kolom)
        plt.xlabel('Bulan')
        plt.ylabel('Total Pendapatan')
        plt.legend(title='Produk')
        plt.xticks(rotation=45)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.tight_layout()

        # Menampilkan plot di Streamlit
        st.pyplot(plt.gcf())
        #########################



    ### Persebaran umur pembeli dan status pembeli
    transaksi_user = pd.merge(df_transaksi, df_user, on='User_ID', how='left')

    st.markdown('<div style="text-align: center;"><h3>Distribusi Pelanggan</h3></div>', unsafe_allow_html=True)
    col1_row2, col2_row2, col3_row2= st.columns(3)
    transaksi_user = pd.merge(df_transaksi, df_user, on='User_ID', how='left')
    transaksi_user_filtered = transaksi_user[transaksi_user['Product_ID'].isin(plot_data_product_quantity)]

    with col1_row2:
        st.markdown('<div style="text-align: center;">Persebaran Usia Pembeli Produk</div>', unsafe_allow_html=True)
        fig_1, ax_1 = plt.subplots()
        sns.histplot(data=transaksi_user_filtered, x = 'Age', hue = 'Product_ID', multiple='dodge', element="poly",  bins=6, palette=warna_kolom) 
        ax_1.set_xlabel('Umur')
        ax_1.set_ylabel('Frekuensi Pembelian')
        st.pyplot(fig_1)
    with col2_row2:
        st.markdown('<div style="text-align: center;">Persebaran Status Pembeli Produk</div>', unsafe_allow_html=True)
        fig_2, ax_2 = plt.subplots()
        sns.histplot(data=transaksi_user_filtered, x="Status", hue="Product_ID", multiple="dodge", shrink=.8, palette=warna_kolom)
        ax_2.set_xlabel('Status')
        ax_2.set_ylabel('Frekuensi Pembelian')
        st.pyplot(fig_2)
    with col3_row2:
        st.markdown('<div style="text-align: center;">Pelanggan yang Sering Membali Produk</div>', unsafe_allow_html=True)
        df_transaksi_user = df_transaksi[df_transaksi['Product_ID'].isin(plot_data_product_quantity)].groupby(['User_ID'])['Transaction_ID'].count().reset_index().sort_values(by='Transaction_ID', ascending=False)[:5]
        fig_3, ax_3 = plt.subplots()
        ax = sns.barplot(df_transaksi_user, x="User_ID", y="Transaction_ID", errorbar=None, palette=warna_kolom)
        ax.bar_label(ax.containers[0], fontsize=10)
        ax_3.set_xlabel('Status')
        ax_3.set_ylabel('Frekuensi Pembelian')
        st.pyplot(fig_3)
    #########################

    st.markdown('<div style="text-align: center;"><h3>Sisa Stock</h3></div>', unsafe_allow_html=True)
    df_sisa_produk = pd.merge(df_transaksi, df_produk, on='Product_ID', how='left')
    df_sisa_produk = df_sisa_produk.drop(columns=['User_ID', 'Date', 'Month', 'HARGA_SATUAN', 'Transaction_ID'])
    df_sisa_produk_groupby = df_sisa_produk.groupby('Product_ID')[['Quantity', 'JUMLAH_DIGUDANG', 'HARUS_RESTOCK_BILA_JUMLAH_GUDANG_TERSISA']].agg(
        {'Quantity':'sum', 
        'JUMLAH_DIGUDANG': 'mean',
        'HARUS_RESTOCK_BILA_JUMLAH_GUDANG_TERSISA': 'mean'})
    df_sisa_produk_groupby['Sisa Stock'] = df_sisa_produk_groupby['JUMLAH_DIGUDANG'] - df_sisa_produk_groupby['Quantity']
    df_sisa_produk_groupby['Re-Stock'] = np.where(df_sisa_produk_groupby['Sisa Stock'] < df_sisa_produk_groupby['HARUS_RESTOCK_BILA_JUMLAH_GUDANG_TERSISA'], 'Harus Re-Stock', 'Masih Tersedia')
    df_sisa_produk_groupby = df_sisa_produk_groupby[df_sisa_produk_groupby.index.isin(plot_data_product_quantity)]

    palette_colors = {
        'Harus Re-Stock': '#fe2f2f',
        'Masih Tersedia': '#32b2a1'
    }

    plt.figure(figsize=(20, 6))
    barplot = sns.barplot(x=df_sisa_produk_groupby.index, y=df_sisa_produk_groupby['Sisa Stock'],
                        hue=df_sisa_produk_groupby['Re-Stock'], palette=palette_colors)


    barplot.set_xlabel('Produk')
    barplot.set_ylabel('Sisa Stock')

    barplot.tick_params(labelsize=12)

    plt.legend(title='Status Stock', loc='upper right', frameon=True, shadow=True)
    plt.grid(color='white', linestyle='--', linewidth=0.5, axis='y', alpha=0.7)
    st.pyplot(plt.gcf())
else:
    st.write("Silakan pilih produk untuk dianalisis.")