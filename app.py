
import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

# 銘柄
tickers = {
  'Hawaiian Electri': 'HE',
  'Altria Group': 'MO',
  'Coca Cola': 'KO',
  'Pepsico': 'PEP',
  'Verizon Commu': 'VZ'
}

# 株価情報を取得する関数
# キャッシュデータとして残しておく（毎回取得しない）
@st.cache_data
def get_data(days, tickers):
  df = pd.DataFrame()
  for company in tickers.keys():
    tkr = yf.Ticker(tickers[company])
    hist = tkr.history(period=f'{days}d')
    hist.index = hist.index.strftime('%d %B %Y')
    hist = hist[['Close']]
    hist.columns = [company]
    hist = hist.T
    hist.index.name = 'Name'
    df = pd.concat([df, hist])
  return df

try:
  # サイドバー
  st.sidebar.write("""
  # 米国市場株価
  ## 表示日数の選択
  """)
  days = st.sidebar.slider('日数', 1, 720, 30)
  st.sidebar.write("""
  ## 株価の範囲指定
  """)
  ymin, ymax = st.sidebar.slider(
    '範囲',
    0.0, 500.0, (0.0, 500.0)
  )

  # メイン
  st.title('米国市場株価可視化アプリ')
  st.write(f"""
  ### 過去 **{days}日間**の株価
  """)

  df = get_data(days, tickers)

  companies = st.multiselect(
    '銘柄を選択する',
    list(df.index),
    ['Hawaiian Electri','Altria Group', 'Coca Cola', 'Pepsico', 'Verizon Commu']
  )
  if not companies:
    st.error('少なくとも一社は選択してください。')
  else:
    data = df.loc[companies]
    st.write('### 株価（USD）', data.sort_index())
    data = data.T.reset_index()
    data = pd.melt(data, id_vars=['Date']).rename(columns={'value': 'Stock Prices(USD)'}
    )
    chart = (
      alt.Chart(data)
      .mark_line(opacity=0.8, clip=True)
      .encode(
        x='Date:T',
        y=alt.Y('Stock Prices(USD):Q', stack=None, scale=alt.Scale(domain=[ymin, ymax])),
        color='Name:N'
      )
    )
    st.altair_chart(chart, use_container_width=True)
except:
  st.error(
    'Error'
  )
