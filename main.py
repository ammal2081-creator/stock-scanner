import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing 2026 - Master V6", layout="wide")

st.title("📊 Pro Swing Stock Scanner - Master V6 Live")
st.write("סורק מניות אוטומטי הכולל מחירים חיים, בדיקת גרף שבועי, ציון אמינות וניהול סיכונים מלא.")

all_indices = {
    "S&P 500 & Nasdaq מובילות": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"],
    "ישראלי / מקומי (TA-125)": ["TEVA.TA", "ESLT.TA", "POLI.TA", "LUMI.TA"]
}

selected_group = st.selectbox("בחר קבוצת מדדים לסריקה:", list(all_indices.keys()))

if st.button("הפעל סריקה מדויקת עם גרף שבועי ומחירים חיים"):
    with st.spinner("שולף שערים מארה"ב ומהארץ, מנתח גרף שבועי ומחשב ציוני V6..."):
        tickers = all_indices[selected_group]
        results = []
        
        for ticker in tickers:
            try:
                # שליפת נתונים יומיים
                df_daily = yf.download(ticker, period="3mo", progress=False)
                # שליפת נתונים שבועיים לצורך בדיקת גרף שבועי
                df_weekly = yf.download(ticker, period="6mo", interval="1wk", progress=False)
                
                if df_daily is not None and not df_daily.empty:
                    if isinstance(df_daily.columns, pd.MultiIndex):
                        df_daily.columns = df_daily.columns.get_level_values(0)
                    if isinstance(df_weekly.columns, pd.MultiIndex):
                        df_weekly.columns = df_weekly.columns.get_level_values(0)
                        
                    if len(df_daily) > 30:
                        close = float(df_daily['Close'].iloc[-1])
                        prev_close = float(df_daily['Close'].iloc[-2])
                        high = float(df_daily['High'].iloc[-1])
                        low = float(df_daily['Low'].iloc[-1])
                        
                        # ממוצעים טכניים
                        sma50 = float(df_daily['Close'].rolling(50).mean().iloc[-1])
                        sma200 = float(df_daily['Close'].rolling(min(200, len(df_daily))).mean().iloc[-1])
                        ema21 = float(df_daily['Close'].ewm(span=21, adjust=False).mean().iloc[-1])
                        
                        dist_ema21 = ((close - ema21) / ema21) * 100
                        
                        # בדיקת גרף שבועי חיובי (האם הנר השבועי האחרון סגור מעל השבוע הקודם)
                        weekly_trend = "שלילי"
                        if df_weekly is not None and len(df_weekly) >= 2:
                            w_close_curr = float(df_weekly['Close'].iloc[-1])
                            w_close_prev = float(df_weekly['Close'].iloc[-2])
                            if w_close_curr > w_close_prev:
                                weekly_trend = "חיובי (עולה) 🟢"
                                
                        # חישוב ציון אמינות (Score 1 עד 4)
                        score = 0
                        if close > sma50: score += 1
                        if sma50 > sma200: score += 1
                        if close > ema21: score += 1
                        if weekly_trend.startswith("חיובי"): score += 1
                        
                        risk_pct = f"{score * 0.25}%" if score > 0 else "0%"
                        
                        # זיהוי סט-אפ
                        resistance = float(df_daily['High'].iloc[-21:-1].max())
                        is_breakout = close >= resistance * 0.99
                        
                        setup_status = "מעקב"
                        if is_breakout:
                            setup_status = "BREAKOUT 🚀"
                        elif close > ema21:
                            setup_status = "PULLBACK / TREND 📈"

                        results.append({
                            "סימול": ticker,
                            "מחיר סגירה ($/אגק)": round(close, 2),
                            "שינוי יומי (%)": round(((close - prev_close) / prev_close) * 100, 2),
                            "גרף שבועי": weekly_trend,
                            "ציון אמינות (Score)": f"{score} / 4",
                            "סיכון מוגדר": risk_pct,
                            "סטטוס אסטרטגיה": setup_status
                        })
            except Exception as e:
                continue
                
        if results:
            final_df = pd.DataFrame(results)
            st.success("הסריקה הושלמה בהצלחה!")
            st.dataframe(final_df, use_container_width=True)
        else:
            st.warning("לא נמצאו תוצאות. נסה שוב.")
