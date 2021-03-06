# 参考
# pip install japanmap
# pip install openpyxl
# pip install plotly

# ライブラリの読み込み
from datetime import datetime as dt
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from japanmap import picture

# オープンデータのURL 使用していないものもある
newly_confirmed_cases_daily = "https://covid19.mhlw.go.jp/public/opendata/newly_confirmed_cases_daily.csv"
requiring_inpatient_care_etc_daily = "https://covid19.mhlw.go.jp/public/opendata/requiring_inpatient_care_etc_daily.csv"
deaths_cumulative_daily = "https://covid19.mhlw.go.jp/public/opendata/deaths_cumulative_daily.csv"
severe_cases_daily = "https://covid19.mhlw.go.jp/public/opendata/severe_cases_daily.csv"
population = "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032110815&fileKind=0"

# オープンデータを読み込んみデータフレームを作成
df01 = pd.read_csv(newly_confirmed_cases_daily, index_col="Date")
df01.index = pd.DatetimeIndex(df01.index).date
df02 = pd.read_csv(severe_cases_daily, index_col="Date")
df02.index = pd.DatetimeIndex(df02.index).date
df03 = pd.read_csv(deaths_cumulative_daily, index_col="Date")
df03.index = pd.DatetimeIndex(df03.index).date

df_today = df01.iloc[-1]
df_today = df_today.rename({"Hokkaido": "北海道",
                            "Aomori": "青森", "Akita": "秋田", "Iwate": "岩手", "Miyagi": "宮城", "Yamagata": "山形",
                            "Fukushima": "福島",
                            "Ibaraki": "茨城", "Tochigi": "栃木", "Gunma": "群馬", "Saitama": "埼玉", "Chiba": "千葉",
                            "Tokyo": "東京", "Kanagawa": "神奈川",
                            "Niigata": "新潟", "Toyama": "富山", "Ishikawa": "石川", "Fukui": "福井", "Yamanashi": "山梨",
                            "Nagano": "長野",
                            "Gifu": "岐阜", "Shizuoka": "静岡", "Aichi": "愛知", "Mie": "三重",
                            "Shiga": "滋賀", "Kyoto": "京都", "Osaka": "大阪", "Hyogo": "兵庫", "Nara": "奈良", "Wakayama": "和歌山",
                            "Tottori": "鳥取", "Shimane": "島根", "Okayama": "岡山", "Hiroshima": "広島", "Yamaguchi": "山口",
                            "Kagawa": "香川", "Tokushima": "徳島", "Ehime": "愛媛", "Kochi": "高知",
                            "Fukuoka": "福岡", "Saga": "佐賀", "Nagasaki": "長崎", "Kumamoto": "熊本", "Oita": "大分",
                            "Miyazaki": "宮崎", "Kagoshima": "鹿児島", "Okinawa": "沖縄"})
df_today = df_today[1:]

df_population = pd.read_excel(population, header=5, skipfooter=1)
df_population = df_population.rename(columns={"人": "人口"})
df_population = df_population[["都道府県名", "人口"]].iloc[1:, :]
df_population["陽性患者数"] = df_today.values
df_population["人口あたりの陽性患者数"] = df_population["陽性患者数"] / df_population["人口"]

# タイトル
st.title("Covid-19陽性者数ダッシュボード")

# 　本日の新規陽性者数
st.metric(label="新規陽性者数", value=df01["ALL"].values[-1])

# グラフの描画
# 都道府県の選択
prefecture_slection = st.multiselect("都道府県を選択してください", df01.columns, default="ALL")

min_period = df01.index.min()
start_period = st.slider("開始日付", df01.index.min(), df01.index.max(), value=df01.index.min())
end_period = st.slider("終了日付", df01.index.min(), df01.index.max(), df01.index.max())

# 移動平均の設定
moving_average = st.slider("移動平均の日数", 1, 30, value=7)
df01 = df01.rolling(moving_average, min_periods=1).mean().round(1)
df02 = df02.rolling(moving_average, min_periods=1).mean().round(1)

if end_period < start_period:
    st.write("期間の設定に誤りがあります")
else:

    if prefecture_slection:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        pre = prefecture_slection

        for idx, prefecture in enumerate(pre):
            fig.add_trace(go.Bar(x=df01.index, y=df01[prefecture], name=(prefecture + "_新規陽性者数")))
            fig.add_trace(go.Bar(x=df02.index, y=df02[prefecture], name=(prefecture + "_重症者数")))
            fig.update_layout(barmode='overlay', xaxis=dict(range=(start_period, end_period)))
            fig.add_trace(go.Scatter(x=df03.index, y=df03[prefecture], name=(prefecture + "_累計死者数")))

        st.plotly_chart(fig, use_container_width=True)

    # 日本地図で可視化
st.markdown("### 日本地図で可視化")

# 新規陽性者総数
st.write("新規陽性者数")
cmap = plt.get_cmap('Blues')
norm = plt.Normalize(vmin=df_today.min(), vmax=df_today.max())
fcol = lambda x: '#' + bytes(cmap(norm(x), bytes=True)[:3]).hex()
fig = plt.figure(figsize=(4, 4))
plt.colorbar(plt.cm.ScalarMappable(norm, cmap))
plt.imshow(picture(df_today.apply(fcol)))
st.pyplot(fig)

# 人口あたり新規陽性者総数
st.write("人口あたり新規陽性者数")
cmap = plt.get_cmap('Blues')
norm = plt.Normalize(vmin=df_population["人口あたりの陽性患者数"].min(), vmax=df_population["人口あたりの陽性患者数"].max())
fcol = lambda x: '#' + bytes(cmap(norm(x), bytes=True)[:3]).hex()
fig = plt.figure(figsize=(4, 4))
plt.colorbar(plt.cm.ScalarMappable(norm, cmap))
plt.imshow(picture(df_population["人口あたりの陽性患者数"].apply(fcol)))
st.pyplot(fig)

# データフレーム
st.table(df_population)

st.write("-----------------")
st.markdown("#### オープンデータリンク")
st.write("厚生労働省")
st.write("https://www.mhlw.go.jp/stf/covid-19/open-data.html")
st.write("e-stat")
st.write("https://www.e-stat.go.jp/")
