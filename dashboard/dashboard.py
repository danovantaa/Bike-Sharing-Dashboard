import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from scipy.cluster.hierarchy import linkage, dendrogram

def create_rfm_df(df):
    user_rfm = df.groupby(by='registered', as_index = False).agg({
        'dteday': ['max','count'],
        'cnt': 'sum'
    })
    user_rfm.columns = ["registered", "max_order_timestamp", "frequency", "monetary"]
    user_rfm["max_order_timestamp"] = user_rfm["max_order_timestamp"].dt.date
    recent_date = df["dteday"].dt.date.max()
    user_rfm["recency"] = user_rfm["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    return user_rfm

def create_year_summary(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    df['Day_type'] = df['workingday'].map({1: 'Hari Kerja', 0: 'Hari Libur'})
    df['year'] = df['dteday'].dt.year
    day_type_year_summary = df.groupby(['year','Day_type'])['cnt'].mean().reset_index()
    return day_type_year_summary

def create_season(df):
    season_labels = {
        1: 'Spring',
        2: 'Summer',
        3: 'Fall',
        4: 'Winter'
    }
    season_summary = all_df.groupby('season')['cnt'].mean().reset_index()
    season_summary['season_label'] = season_summary['season'].map(season_labels)
    return season_summary

def create_hourly_count(df):
    hourly_counts = df.groupby('hr')['cnt'].mean().reset_index()
    return hourly_counts
    
def create_weather(df):
    weather_summary = df.groupby('weathersit')['cnt'].sum().reset_index()
    weather_labels = {
        1: 'Baik',
        2: 'Sedang',
        3: 'Sedikit Buruk',
        4: 'Buruk'
    }
    weather_summary['weather_label'] = weather_summary['weathersit'].map(weather_labels)
    return weather_summary

def create_clustering(df):
    hourly_data = df.groupby('hr').agg(
    total_rentals=('cnt', 'sum')
    ).reset_index()

    # Membuat linkage
    Z = linkage(hourly_data[['hr', 'total_rentals']], method = 'ward')
    return Z
    
day_df = pd.read_csv("../data/day.csv")
hour_df = pd.read_csv("../data/hour.csv")
all_df = pd.read_csv("all.csv")

all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)
all_df['dteday'] = pd.to_datetime(all_df['dteday'])

min_date = all_df["dteday"].min().date()
max_date = all_df["dteday"].max().date()

with st.sidebar :
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
# main_df = all_df[(all_df["dteday"]>= str(start_date)) &
#                 (all_df["dteday"]<= str (end_date))]
main_df = all_df[(all_df["dteday"] >= pd.to_datetime(start_date)) &
                 (all_df["dteday"] <= pd.to_datetime(end_date))]

user_rfm = create_rfm_df(main_df)
day_type_year_summary = create_year_summary(main_df)
season_summary = create_season(main_df)
hourly_counts = create_hourly_count(main_df)
Z=create_clustering(main_df)

total_rentals = main_df["cnt"].sum()
avg_rentals = main_df["cnt"].mean()

total_registered = main_df["registered"].sum()
avg_registered = main_df["registered"].mean()

st.header('Bike Sharing Dashboard :bike:')
st.subheader('Daily Orders')

col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="Total Penyewaan Sepeda",
        value=f"{total_rentals:,}",
        delta=f"{total_rentals - all_df['cnt'].mean():,} dari rata rata keseluruhan",
    )
    st.metric(
        label="Rata-rata Penyewaan",
        value=f"{avg_rentals:.2f}",
    )
    
with col2:
    st.metric(
        label="Total Pengguna Terdaftar",
        value=f"{total_registered:,}",
        delta=f"{total_registered - all_df['registered'].mean():,} dari rata rata keseluruhan",
    )
    st.metric(
        label="Rata-rata Pengguna Terdaftar",
        value=f"{avg_registered:.2f}",
    )

st.subheader('Grafik Penyewaan Sepeda Berdasarkan Waktu')

col1, col2= st.columns(2)

with col1:
    fig, ax = plt.subplots()
    sns.barplot(
    data=day_type_year_summary,
    x="Day_type",
    y="cnt",
    hue="year",
    palette="viridis",
    ax=ax
    )
    ax.set_title("Penyewaan Sepeda Berdasarkan Tipe Hari dan Tahun", fontsize=14)
    ax.set_xlabel("Tipe Hari", fontsize=12)
    ax.set_ylabel("Rata-rata Penyewaan Sepeda", fontsize=12)
    ax.tick_params(axis='x', labelsize=11)
    ax.tick_params(axis='y', labelsize= 11)
    ax.legend(title="Tahun")
    st.pyplot(fig)
    
with col2:
    fig, ax = plt.subplots()
    sns.lineplot(
        x=hourly_counts['hr'], 
        y=hourly_counts['cnt'], 
        marker="o", 
        ax=ax
    )

    ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Jam", fontsize=14)
    ax.set_xlabel("Hour (0-23)", fontsize=12)
    ax.set_ylabel("Rata-rata Penyewaan", fontsize=12)
    ax.tick_params(axis='x', labelsize=11)
    ax.tick_params(axis='y', labelsize=11)
    ax.grid(True)
    st.pyplot(fig)

st.subheader('Grafik Penyewaan Sepeda Berdasarkan Iklim')

col1, col2 = st.columns(2)

with col1 :
    explode = (0, 0, 0.1, 0)  
    fig, ax = plt.subplots()
    ax.pie(
        season_summary['cnt'],
        labels=season_summary['season_label'],
        autopct='%1.1f%%',
        colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'],
        explode=explode
    )
    ax.set_title('Distribusi Penyewaan Sepeda Berdasarkan Musim', fontsize=14)
    ax.axis('equal')
    st.pyplot(fig)
    
with col2:
    weather_labels = {
        1: 'Baik',
        2: 'Sedang',
        3: 'Sedikit Buruk',
        4: 'Buruk'
    }
    fig, ax = plt.subplots()
    sns.boxplot(data=all_df, x='weathersit', y='cnt', ax=ax)
    ax.set_xticklabels([weather_labels.get(label, 'Tidak Diketahui') for label in sorted(all_df['weathersit'].unique())])
    ax.set_title('Distribusi Penyewaan Sepeda Berdasarkan Cuaca', fontsize=14)
    ax.set_xlabel('Cuaca', fontsize=12)
    ax.set_ylabel('Jumlah Penyewaan Sepeda', fontsize=12)
    ax.tick_params(axis='x', labelsize=11)
    ax.tick_params(axis='y', labelsize=11)
    st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")
tabs = st.tabs(["Frequency", "Recency", "Monetary"])

with tabs[0]:
    st.header("Histogram Data Frequency")
    st.write("Berikut adalah grafik histogram dari data frequency pengguna")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(user_rfm["frequency"], kde=True, ax=ax)
    ax.set_title("Distribusi Frequency Pengguna")
    st.pyplot(fig)

with tabs[1]:
    st.header("Histogram Data Recency")
    st.write("Berikut adalah grafik histogram dari data recency pengguna")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(user_rfm["recency"], kde=True, ax=ax)
    ax.set_title("Distribusi Recency Pengguna")
    st.pyplot(fig)

with tabs[2]:
    st.header("Histogram Data Monetary")
    st.write("Berikut adalah grafik histogram dari data monetary pengguna")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(user_rfm["monetary"], kde=True, ax=ax)
    ax.set_title("Distribusi Monetary Pengguna")
    st.pyplot(fig)
    
st.header('Clustering Penyewaan Sepeda per Jam')
fig, ax = plt.subplots(figsize=(8, 6))
dendrogram(Z, ax=ax)
ax.set_title('Dendrogram Clustering Penyewaan Sepeda per Jam', fontsize=14)
ax.set_xlabel('Jam', fontsize=12)
ax.set_ylabel('Jumlah Penyewaan Sepeda', fontsize=12)
st.pyplot(fig)