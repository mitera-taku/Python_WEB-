import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st
from datetime import datetime, timedelta

st.title('株価可視アプリ')

st.sidebar.write("""
# 株価
このアプリは株価可視化ツールです。
以下のオプションから表示日数を指定することが出来ます！
""")

st.sidebar.write('# 表示日数')

days = st.sidebar.slider('日数', 1, 50, 20)

st.write(f"""
         ### 過去 **{days}日間** の株価
""")

@st.cache_data
def get_data(days, tickers):
    df = pd.DataFrame()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    for company, ticker in tickers.items():
        try:
            tkr = yf.Ticker(ticker)
            hist = tkr.history(start=start_date, end=end_date)
            
            # indexをdatetime型に変換
            hist.index = pd.to_datetime(hist.index)
            
            # Close価格のデータのみを選択
            hist = hist[['Close']]
            hist.columns = [company]
            hist = hist.reset_index()  # インデックスをリセットして、日付を列として追加
            hist.rename(columns={'Date': 'Date'}, inplace=True)
            df = pd.merge(df, hist, on='Date', how='outer') if not df.empty else hist
        except Exception as e:
            st.warning(f"{company} のデータ取得中にエラーが発生しました: {e}")
    return df

try:  
    st.sidebar.write('### 株価の範囲指定')

    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください',
        0.0, 4000.0, (0.0, 4000.0)
    )

    tickers = {
        'apple': 'AAPL',
        'facebook': 'META',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN',
        'TOYOTA': 'TYO'
    }
    df = get_data(days, tickers)
    if df.empty:
        st.error('データが取得できませんでした。')
    else:
        companies = st.multiselect(
            '会社を選択してください',
            list(df.columns),
            ['google', 'apple', 'facebook', 'amazon']
        )
        
        if not companies:
            st.error('一社は選んでください！！！！')
        else:
            data = df[['Date'] + companies]
            st.write("### 株価(USD)", data.sort_values('Date'))
            data = pd.melt(data, id_vars=['Date']).rename(
                columns={'value': 'Stock Prices(USD)'}
            )
            chart = (
                alt.Chart(data)
                .mark_line(opacity=0.8, clip=True)
                .encode(
                    x="Date:T",
                    y=alt.Y("Stock Prices(USD):Q", stack=None,
                            scale=alt.Scale(domain=[ymin, ymax])),
                    color='variable:N'
                )
            )
            st.altair_chart(chart, use_container_width=True)
except Exception as e:
    st.error(f"何かエラーが発生してしまったようです: {e}")
