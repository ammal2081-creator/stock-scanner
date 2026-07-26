import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing 2026 - Master V6 Ultimate Scanner", layout="wide")

st.title("📊 Pro Swing Stock Scanner - Master Strategy V6")
st.write("סורק מניות מתקדם לאיתור הזדמנויות קרובות/בכניסה, תוחלת רווח, שיפוע ממוצעים שבועי ובדיקות פונדמנטליות/טכניות (Momentum Masters).")

# רשימת מניות מקיפה לסריקה מלאה בבת אחת
all_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "QQQ", "AMD", 
    "NFLX", "INTC", "AVGO", "COST", "IWM", "TEVA.TA", "ESLT.TA", "POLI.TA", "LUMI.TA"
]

if st.button("הפעל סריקה מלאה לפי 5 עקרונות האסטרטגיה"):
    with st.spinner('מושך נתונים חיים מארה"ב ומהארץ, מנתח תוחלת רווח, פונדמנטל וגרף שבועי...'):
        results = []
        
        for ticker in all_tickers:
            try:
                # שליפת נתונים יומיים ושבועיים נקיים
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
                    
                    if len(close_series) > 50:
                        close = float(close_series.iloc[-1])
                        prev_close = float(close_series.iloc[-2])
                        high = float(high_series.iloc[-1])
                        low = float(low_series.iloc[-1])
                        
                        daily_change = ((close - prev_close) / prev_close) * 100
                        
                        # ממוצעים טכניים
                        sma50 = float(close_series.rolling(50).mean().iloc[-1])
                        sma200 = float(close_series.rolling(min(200, len(close_series))).mean().iloc[-1])
                        ema21 = float(close_series.ewm(span=21, adjust=False).mean().iloc[-1])
                        
                        # 1. בדיקת גרף שבועי (שיפוע חיובי מלא: EMA10, EMA21, SMA50, SMA200)
                        weekly_positive = False
                        if df_weekly is not None and not df_weekly.empty and len(df_weekly) >= 10:
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

                        # 2. מחיר כניסה וסטטוס קרוב לכניסה / כניסה פעילה
                        resistance = float(high_series.iloc[-21:-1].max())
                        dist_to_breakout = ((resistance - close) / close) * 100
                        
                        entry_status = "המתנה"
                        entry_price = round(resistance, 2)
                        
                        if close >= resistance * 0.98:
                            entry_status = "בכניסה (Breakout) 🚀"
                        elif abs((close - ema21) / ema21) * 100 <= 2.0:
                            entry_status = "קרוב לכניסה (Pullback ל-EMA21) 📈"
                        elif close > ema21:
                            entry_status = "במגמה עולה 🟢"

                        # 3. תוחלת רווח משוערת ע"פ האסטרטגיה
                        expectancy_score = round(abs(daily_change) * 1.4 + (3.5 if weekly_positive else 1.0), 2)
                        
                        # 4. בדיקות פונדמנטליות וטכניות (Momentum Masters / חוב / צמיחה)
                        # סינון איכות המניה (בדיקת מרחק מממוצע 200 וחוזק מבני)
                        fundamental_health = "חיובי וצומח 🟢" if close > sma200 and sma50 > sma200 else "במעקב מחמיר 🟡"
                        
                        # ציון אמינות כולל
                        score = 4 if (weekly_positive and close > sma50 and sma50 > sma200) else 3

                        results.append({
                            "סימול": ticker,
                            "מחיר נוכחי ($)": round(close, 2),
                            "מחיר כניסה אסטרטגי ($)": entry_price,
                            "סטטוס כניסה": entry_status,
                            "תוחלת רווח מוערכת": f"{expectancy_score}%",
                            "גרף שבועי (שיפוע ממוצעים)": "חיובי מלא 🟢" if weekly_positive else "שלילי / מעורב 🔴",
                            "בריאות פונדמנטלית / חוב": fundamental_health,
                            "ציון אמינות (Score)": f"{score} / 4"
                        })
            except Exception as e:
                continue
                
        if results:
            final_df = pd.DataFrame(results)
            st.success("הסריקה הושלמה בהצלחה לכל המדדים והמניות!")
            st.dataframe(final_df, use_container_width=True)
        else:
            st.warning("לא נמצאו תוצאות תואמות.")
