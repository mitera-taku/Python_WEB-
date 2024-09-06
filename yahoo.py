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

st.sidebar.write('# 日付範囲指定')

# 日付範囲を指定するウィジェット
start_date = st.sidebar.date_input('開始日', datetime.now() - timedelta(days=30))
end_date = st.sidebar.date_input('終了日', datetime.now())

if start_date > end_date:
    st.error('終了日は開始日より後の日付を指定してください。')
else:
    st.write(f"""
             ### 過去 **{(end_date - start_date).days}日間** の株価
    """)

    @st.cache_data
    def get_data(start_date, end_date, tickers):
        df = pd.DataFrame()
        ticker_to_name = {}

        for ticker, company_name in tickers.items():
            try:
                tkr = yf.Ticker(ticker)
                hist = tkr.history(start=start_date, end=end_date)
                
                # indexをdatetime型に変換し、時間を削除
                hist.index = pd.to_datetime(hist.index).date  # 時間を削除して日付だけにする
                
                # Close価格のデータのみを選択
                hist = hist[['Close']]
                
                # カラム名を会社名に設定
                hist.columns = [company_name]
                
                # インデックスをリセットして、日付を列として追加
                hist = hist.reset_index() 
                hist.rename(columns={'index': 'Date'}, inplace=True)
                df = pd.merge(df, hist, on='Date', how='outer') if not df.empty else hist
                
                ticker_to_name[ticker] = company_name
            except Exception as e:
                st.warning(f"{company_name} のデータ取得中にエラーが発生しました: {e}")
        return df, ticker_to_name

    st.sidebar.write('### 株価の範囲指定')

    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください',
        0.0, 4000.0, (0.0, 500.0)
    )

    # ユーザーが追加したいティッカーシンボルを入力
    user_input = st.sidebar.text_input('ティッカーシンボルをカンマで区切って入力してください (例: AAPL, MSFT, GOOGL)', 'AAPL, MSFT, GOOGL')
    tickers_list = [ticker.strip() for ticker in user_input.split(',')]

    # ティッカーシンボルから会社名を取得する
    company_names = {
        'AAPL': 'Apple',
        'MSFT': 'Microsoft',
        'GOOGL': 'Google',
        'META': 'Facebook',
        'AMZN': 'Amazon',
        'NFLX': 'Netflix',
        'TSLA': 'Tesla',
        'TM': 'TOYOTA'
        # 必要に応じて他の会社も追加してください
    }
    
    # 入力されたティッカーシンボルに対応する会社名の辞書を作成
    tickers = {ticker: company_names.get(ticker, ticker) for ticker in tickers_list}

    df, ticker_to_name = get_data(start_date, end_date, tickers)
    
    if df.empty:
        st.error('データが取得できませんでした。')
    else:
        # Dateを選択肢から除外
        available_companies = [col for col in df.columns if col != 'Date']
        
        companies = st.multiselect(
            '表示する会社を選択してください',
            available_companies,
            # 初期選択はユーザーが入力した会社名
            list(tickers.values())  
        )
        
        if not companies:
            st.error('一社は選んでください！')
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
                    x=alt.X("Date:T", title="日付"),  
                    y=alt.Y("Stock Prices(USD):Q", stack=None,
                            scale=alt.Scale(domain=[ymin, ymax]),title="ヤフーファイナンス ドル"),
                    color='variable:N'
                )
            )
            st.altair_chart(chart, use_container_width=True)
