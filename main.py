import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing Master V6 - Independent Scanner", layout="wide")

st.title("📊 Pro Swing - Independent Strategy Scanner")
st.write("סורק עצמאי המריץ את כל תנאי האסטרטגיה (כולל גרף שבועי מחמיר, מחיר כניסה וציון אמינות) על כל המניות בבת אחת.")

# רשימת המניות לסריקה עצמאית
all_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", 
    "QQQ", "AMD", "NFLX", "INTC", "AVGO", "COST", "IWM", 
    "TEVA.TA", "ESLT.TA", "POLI.TA", "LUMI.TA"
]

if st.button("הפעל סריקה עצמאית מלאה לפי חוקי האסטרטגיה"):
    with st.spinner('מריץ סריקה וניתוח טכני ושבועי על כל המניות...'):
        results = []
        
        for ticker in all_tickers:
            try:
                # שליפת נתונים יומיים ושבועיים
                df_daily = yf.download(ticker, period="6mo", progress=False, auto_adjust=True)
                df_weekly = yf.download(ticker, period="1y", interval="1wk", progress=False, auto_adjust=True)
                
                if df_daily is not None and not df_daily.empty:
                    if isinstance(df_daily.columns, pd.MultiIndex):
                        df_daily.columns = df_daily.columns.get_level_values(0)
                    if isinstance(df_weekly.columns, pd.MultiIndex):
                        df_weekly.columns = df_weekly.columns.get_level_values(0)
                        
                    close_series = df_daily['Close'].dropna()
                    high_series = df_daily['High'].dropna()
                    low_series = df_daily['Low'].dropna()
                    
                    if len(close_series) > 50 and len(df_weekly) >= 10:
                        close = float(close_series.iloc[-1])
                        prev_close = float(close_series.iloc[-2])
                        high = float(high_series.iloc[-1])
                        low = float(low_series.iloc[-1])
                        
                        daily_change = ((close - prev_close) / prev_close) * 100
                        
                        # ממוצעים יומיים
                        sma50 = float(close_series.rolling(50).mean().iloc[-1])
                        sma200 = float(close_series.rolling(min(200, len(close_series))).mean().iloc[-1])
                        ema21 = float(close_series.ewm(span=21, adjust=False).mean().iloc[-1])
                        
                        # 1. תנאי גרף שבועי מחמיר: ארבעת הממוצעים בשיפוע חיובי מלא
                        w_close = df_weekly['Close'].dropna()
                        w_ema10 = w_close.ewm(span=10, adjust=False).mean()
                        w_ema21 = w_close.ewm(span=21, adjust=False).mean()
                        w_sma50 = w_close.rolling(50).mean()
                        w_sma200 = w_close.rolling(200).mean()
                        
                        s1 = w_ema10.iloc[-1] > w_ema10.iloc[-2]
                        s2 = w_ema21.iloc[-1] > w_ema21.iloc[-2]
                        s3 = w_sma50.iloc[-1] > w_sma50.iloc[-2] if not pd.isna(w_sma50.iloc[-1]) else True
                        s4 = w_sma200.iloc[-1] > w_sma200.iloc[-2] if not pd.isna(w_sma200.iloc[-1]) else True
                        
                        weekly_positive = s1 and s2 and s3 and s4
                        
                        # 2. חישוב מחיר כניסה אסטרטגי
                        resistance = float(high_series.iloc[-21:-1].max())
                        if close >= resistance * 0.98:
                            entry_price = resistance
                            setup_type = "פריצה (Breakout) 🚀"
                        else:
                            entry_price = ema21
                            setup_type = "פולבק ל-EMA21 📈"
                            
                        dist_from_entry = ((close - entry_price) / entry_price) * 100
                        
                        # 3. ציון אמינות (Score 1-4) בהתאם למודל
                        score = 0
                        if close > sma50: score += 1
                        if sma50 > sma200: score += 1
                        if close > ema21: score += 1
                        if weekly_positive: score += 1
                        
                        # סינון: הצגת מניות שעומדות בתנאי הבסיס של האסטרטגיה
                        if close > sma50 and weekly_positive:
                            results.append({
                                "סימול": ticker,
                                "מחיר נוכחי ($)": round(close, 2),
                                "סטטוס סט-אפ": setup_type,
                                "מחיר כניסה אסטרטגי ($)": round(entry_price, 2),
                                "מרחק ממחיר הכניסה (%)": round(dist_from_entry, 2),
                                "גרף שבועי (שיפוע ממוצעים)": "חיובי מלא 🟢",
                                "ציון אמינות": f"{score} / 4"
                            })
            except Exception as e:
                continue
                
        if results:
            final_df = pd.DataFrame(results)
            st.success("הסריקה העצמאית הושלמה בהצלחה!")
            st.dataframe(final_df, use_container_width=True)
        else:
            st.warning("לא נמצאו מניות העונות על מלוא קריטריוני האסטרטגיה ברגע זה.")
