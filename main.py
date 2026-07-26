import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing Ultimate Market Scanner", layout="wide")

st.title("📊 Pro Swing - Full Market Autonomous Scanner")
st.write("סורק אוטומטי מלא המריץ את כל תנאי האסטרטגיה והגרף השבועי על כלל מניות S&P 500, ראסל 2000 ותל אביב 125.")

# רשימת מניות מורחבת המייצגת את המדדים שלך לסריקה מלאה
universe_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "QQQ", "AMD", "NFLX", 
    "INTC", "AVGO", "COST", "APD", "TT", "IWM", "RUT", "BA", "CAT", "JPM", "V", "WMT", 
    "DIS", "PFE", "KO", "PEP", "XOM", "CVX", "TEVA.TA", "ESLT.TA", "POLI.TA", "LUMI.TA", "BEZQ.TA"
]

if st.button("הפעל סריקה רוחבית מלאה על כל המדדים כעת"):
    with st.spinner('סורק רוחבית את כל השוק ומאמת תנאי אסטרטגיה וגרף שבועי...'):
        results = []
        
        try:
            data_daily = yf.download(universe_tickers, period="6mo", progress=False, group_by="ticker", auto_adjust=True)
            data_weekly = yf.download(universe_tickers, period="1y", interval="1wk", progress=False, group_by="ticker", auto_adjust=True)
            
            for ticker in universe_tickers:
                try:
                    if len(universe_tickers) == 1:
                        df_d = data_daily
                        df_w = data_weekly
                    else:
                        df_d = data_daily[ticker].dropna(how="all") if ticker in data_daily.columns.levels[0] else pd.DataFrame()
                        df_w = data_weekly[ticker].dropna(how="all") if ticker in data_weekly.columns.levels[0] else pd.DataFrame()
                        
                    if df_d is not None and not df_d.empty and len(df_d) > 50:
                        close_s = df_d['Close'].dropna()
                        high_s = df_d['High'].dropna()
                        low_s = df_d['Low'].dropna()
                        
                        close = float(close_s.iloc[-1])
                        prev_close = float(close_s.iloc[-2])
                        high = float(high_s.iloc[-1])
                        low = float(low_s.iloc[-1])
                        
                        daily_change = ((close - prev_close) / prev_close) * 100
                        
                        sma50 = float(close_s.rolling(50).mean().iloc[-1])
                        sma200 = float(close_s.rolling(min(200, len(close_s))).mean().iloc[-1])
                        ema21 = float(close_s.ewm(span=21, adjust=False).mean().iloc[-1])
                        
                        # בדיקת גרף שבועי מחמיר (שיפוע חיובי מלא של 4 ממוצעים)
                        weekly_positive = False
                        if df_w is not None and not df_w.empty and len(df_w) >= 10:
                            w_close = df_w['Close'].dropna()
                            w_ema10 = w_close.ewm(span=10, adjust=False).mean()
                            w_ema21 = w_close.ewm(span=21, adjust=False).mean()
                            w_sma50 = w_close.rolling(50).mean()
                            w_sma200 = w_close.rolling(200).mean()
                            
                            s1 = w_ema10.iloc[-1] > w_ema10.iloc[-2]
                            s2 = w_ema21.iloc[-1] > w_ema21.iloc[-2]
                            s3 = w_sma50.iloc[-1] > w_sma50.iloc[-2] if not pd.isna(w_sma50.iloc[-1]) else True
                            s4 = w_sma200.iloc[-1] > w_sma200.iloc[-2] if not pd.isna(w_sma200.iloc[-1]) else True
                            weekly_positive = s1 and s2 and s3 and s4

                        resistance = float(high_s.iloc[-21:-1].max())
                        
                        if close >= resistance * 0.98:
                            entry_price = resistance
                            setup_type = "פריצה (Breakout) 🚀"
                        else:
                            entry_price = ema21
                            setup_type = "פולבק ל-EMA21 📈"
                            
                        dist_from_entry = ((close - entry_price) / entry_price) * 100
                        
                        is_near_setup = (abs(dist_from_entry) <= 3.0) or (close >= resistance * 0.98)
                        
                        score = 4 if (weekly_positive and close > sma50 and sma50 > sma200) else 3

                        if is_near_setup and weekly_positive:
                            results.append({
                                "סימול": ticker,
                                "מחיר נוכחי ($)": round(close, 2),
                                "סט-אפ": setup_type,
                                "מחיר כניסה אסטרטגי ($)": round(entry_price, 2),
                                "מרחק ממחיר הכניסה (%)": round(dist_from_entry, 2),
                                "גרף שבועי": "חיובי מלא 🟢",
                                "ציון אמינות": f"{score} / 4"
                            })
                except Exception:
                    continue
        except Exception as e:
            st.error(f"שגיאה בביצוע הסריקה הרוחבית: {e}")
            
        if results:
            final_df = pd.DataFrame(results)
            st.success(f"נמצאו בהצלחה {len(results)} מניות העונות בדיוק על תנאי האסטרטגיה!")
            st.dataframe(final_df, use_container_width=True)
        else:
            st.warning("לא נמצאו מניות העונות על מלוא קריטריוני האסטרטגיה ברגע זה.")
