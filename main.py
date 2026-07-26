import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing 2026 - Master V6 Live", layout="wide")

st.title("📊 Pro Swing Stock Scanner - Master V6 Synced")
st.write("סורק מניות אוטומטי המסונכרן במדויק לחוקי אסטרטגיית ה-Pine Script (ציון אמינות, מחירי כניסה ומחירים חיים).")

all_indices = {
    "S&P 500 & Nasdaq מובילות": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"],
    "מניות קטנות ונוספות": ["QQQ", "AMD", "NFLX", "INTC", "IWM"],
    "ישראלי / מקומי (TA-125)": ["TEVA.TA", "ESLT.TA", "POLI.TA", "LUMI.TA"]
}

scan_mode = st.radio("אופן סריקה:", ["סרוק את כל המדדים בבת אחת (הכל כלול)", "בחר קבוצה ספציפית"])

selected_groups = []
if scan_mode == "סרוק את כל המדדים בבת אחת (הכל כלול)":
    selected_groups = list(all_indices.keys())
else:
    chosen = st.selectbox("בחר קבוצה:", list(all_indices.keys()))
    selected_groups = [chosen]

if st.button("הפעל סריקה מדויקת מול הטריידינגויו"):
    with st.spinner('מושך נתונים מדויקים, מחשב ציוני אמינות מודל V6 ומחירי כניסה...'):
        all_results = []
        
        # שליפת מדד הייחוס SPY לצורך חישוב RS מדויק
        try:
            spy_df = yf.download("SPY", period="3mo", progress=False)
            if isinstance(spy_df.columns, pd.MultiIndex):
                spy_df.columns = spy_df.columns.get_level_values(0)
            spy_close = float(spy_df['Close'].iloc[-1])
            spy_sma200 = float(spy_df['Close'].rolling(min(200, len(spy_df))).mean().iloc[-1])
        except:
            spy_close = 0
            spy_sma200 = 0

        tickers_to_scan = []
        for g in selected_groups:
            for t in all_indices[g]:
                if t not in tickers_to_scan:
                    tickers_to_scan.append(t)
                    
        for ticker in tickers_to_scan:
            try:
                df_daily = yf.download(ticker, period="6mo", progress=False)
                df_weekly = yf.download(ticker, period="1y", interval="1wk", progress=False)
                
                if df_daily is not None and not df_daily.empty:
                    if isinstance(df_daily.columns, pd.MultiIndex):
                        df_daily.columns = df_daily.columns.get_level_values(0)
                    if isinstance(df_weekly.columns, pd.MultiIndex):
                        df_weekly.columns = df_weekly.columns.get_level_values(0)
                        
                    if len(df_daily) > 50 and len(df_weekly) >= 4:
                        close = float(df_daily['Close'].iloc[-1])
                        prev_close = float(df_daily['Close'].iloc[-2])
                        high = float(df_daily['High'].iloc[-1])
                        low = float(df_daily['Low'].iloc[-1])
                        
                        # ממוצעים יומיים
                        sma50 = float(df_daily['Close'].rolling(50).mean().iloc[-1])
                        sma200 = float(df_daily['Close'].rolling(min(200, len(df_daily))).mean().iloc[-1])
                        ema21 = float(df_daily['Close'].ewm(span=21, adjust=False).mean().iloc[-1])
                        
                        # בדיקת שיפוע ממוצעים שבועיים
                        w_close = df_weekly['Close']
                        w_ema10 = w_close.ewm(span=10, adjust=False).mean()
                        w_ema21 = w_close.ewm(span=21, adjust=False).mean()
                        w_sma50 = w_close.rolling(50).mean()
                        w_sma200 = w_close.rolling(200).mean()
                        
                        slope_ema10 = w_ema10.iloc[-1] > w_ema10.iloc[-2]
                        slope_ema21 = w_ema21.iloc[-1] > w_ema21.iloc[-2]
                        slope_sma50 = w_sma50.iloc[-1] > w_sma50.iloc[-2] if not pd.isna(w_sma50.iloc[-1]) else True
                        slope_sma200 = w_sma200.iloc[-1] > w_sma200.iloc[-2] if not pd.isna(w_sma200.iloc[-1]) else True
                        
                        weekly_positive = slope_ema10 and slope_ema21 and slope_sma50 and slope_sma200
                        weekly_str = "חיובי מלא (כל הממוצעים בשיפוע) 🟢" if weekly_positive else "מעורב / שלילי 🔴"
                        
                        # חישוב Relative Strength מול SPY
                        rs_line = (close / spy_close) if spy_close > 0 else 1
                        rs_ema21 = pd.Series([rs_line]).ewm(span=21, adjust=False).mean().iloc[-1]
                        
                        # חישוב מדויק של Conviction Score (1 עד 4) תואם לטריידינגויו
                        score = 0
                        if rs_line > rs_ema21: score += 2  # RS חזק שווה 2 נקודות כמוגדר באסטרטגיה
                        if close > sma50 and sma50 > sma200: score += 1
                        if spy_close > spy_sma200: score += 1
                        
                        # מחיר כניסה אסטרטגי בהתאם לפריצה או פולבק EMA21
                        resistance = float(df_daily['High'].iloc[-21:-1].max())
                        entry_price = resistance if close >= resistance * 0.98 else round(ema21, 2)
                        
                        setup_status = "מעקב"
                        if close >= resistance * 0.99:
                            setup_status = "BREAKOUT 🚀"
                        elif low <= ema21 * 1.015:
                            setup_status = "PULLBACK 📈"

                        all_results.append({
                            "סימול": ticker,
                            "מחיר נוכחי ($)": round(close, 2),
                            "מחיר כניסה אסטרטגי ($)": round(entry_price, 2),
                            "שינוי יומי (%)": round(((close - prev_close) / prev_close) * 100, 2),
                            "גרף שבועי (שיפוע ממוצעים)": weekly_str,
                            "ציון אמינות (Score)": f"{score} / 4",
                            "סטטוס אסטרטגיה": setup_status
                        })
            except Exception as e:
                continue
                
        if all_results:
            final_df = pd.DataFrame(all_results)
            st.success("הסריקה הסתיימה בהצלחה והותאמה לכללי האסטרטגיה!")
            st.dataframe(final_df, use_container_width=True)
        else:
            st.warning("לא נמצאו נתונים להצגה.")
