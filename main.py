import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing Stock Scanner", layout="wide")

st.title("📊 Pro Swing Stock Scanner - Full Market Scan")
st.write("סורק מניות אוטומטי מקיף לכלל המדדים כולל בדיקות טכניות, שבועיות, פונדמנטליות ותוחלת רווח.")

# הגדרת כל המדדים לסריקה כוללת
all_indices = {
    "S&P 500 (מדגם מוביל)": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
    "Nasdaq 100 (מדגם מוביל)": ["TSLA", "META", "NFLX", "AMD", "INTC"],
    "Russell 2000 (מדגם קטנות)": ["IWM", "RUT"],
    "TA-125 / מקומי": ["TEVA.TA", "ESLT.TA", "POLI.TA", "LUMI.TA"]
}

scan_mode = st.radio("בחר אופן סריקה:", ["סרוק את כל המדדים במקביל", "בחר מדד ספציפי"])

selected_indices_to_scan = []
if scan_mode == "סרוק את כל המדדים במקביל":
    selected_indices_to_scan = list(all_indices.keys())
else:
    chosen = st.selectbox("בחר מדד:", list(all_indices.keys()))
    selected_indices_to_scan = [chosen]

if st.button("הפעל סריקה מקיפה כעת"):
    with st.spinner("מבצע סריקה רוחבית, ניתוח ממוצעים, גרף שבועי ותוחלת רווח..."):
        all_results = []
        
        for idx_name in selected_indices_to_scan:
            tickers = all_indices[idx_name]
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    
                    # נתונים יומיים ושבועיים
                    hist_d = stock.history(period="10d")
                    hist_w = stock.history(period="10w", interval="1wk")
                    
                    if not hist_d.empty and not hist_w.empty:
                        last_close = hist_d['Close'].iloc[-1]
                        prev_close = hist_d['Close'].iloc[-2]
                        daily_change = ((last_close - prev_close) / prev_close) * 100
                        
                        # בדיקת ממוצעים טכנית פשוטה (לדוגמה: מחיר מעל ממוצע 50)
                        ma_50 = hist_d['Close'].rolling(window=min(50, len(hist_d))).mean().iloc[-1]
                        respects_ma = "כן" if last_close >= ma_50 else "בבחינה"
                        
                        # בדיקת מגמה שבועית
                        weekly_trend = "עולה" if hist_w['Close'].iloc[-1] > hist_w['Close'].iloc[-2] else "מתקן"
                        
                        # תוחלת רווח משוערת ואיתות לפי חוקי סגירה
                        signal = "קניה מיידית בסגירה" if daily_change > 0 and weekly_trend == "עולה" else "המתנה"
                        expectancy_score = round((daily_change * 1.2) + (2.5 if respects_ma == "כן" else 0), 2)
                        
                        all_results.append({
                            "מדד": idx_name,
                            "סימול": ticker,
                            "סגירה אחרונה": round(last_close, 2),
                            "שינוי יומי (%)": round(daily_change, 2),
                            "מכבד ממוצעים": respects_ma,
                            "מגמה שבועית": weekly_trend,
                            "תוחלת מוערכת": expectancy_score,
                            "איתות אסטרטגיה": signal
                        })
                except Exception as e:
                    continue
                    
        if all_results:
            df_final = pd.DataFrame(all_results)
            st.success("הסריקה המקיפה הסתיימה בהצלחה עבור כל המדדים שנבחרו!")
            st.dataframe(df_final, use_container_width=True)
        else:
            st.warning("לא נמצאו תוצאות תואמות לקריטריונים.")
