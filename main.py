import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing Stock Scanner", layout="wide")

st.title("📊 Pro Swing Stock Scanner - Live Strategy")
st.write("סורק מניות אוטומטי לאסטרטגיית סווינג (שעה אחרונה בסגירה).")

# רשימת המדדים המבוקשת
indices = {
    "S&P 500": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
    "Nasdaq 100": ["TSLA", "META", "NFLX", "AMD", "INTC"],
    "TA-125 / מקומי": ["TEVA.TA", "ESLT.TA", "POLI.TA", "LUMI.TA"]
}

selected_index = st.selectbox("בחר מדד לסריקה:", list(indices.keys()))

if st.button("הפעל סריקה כעת"):
    with st.spinner(f"סורק את מניות מדד {selected_index} לפי כללי הסגירה..."):
        tickers = indices[selected_index]
        results = []
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                if not hist.empty:
                    last_close = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change = ((last_close - prev_close) / prev_close) * 100
                    
                    # לדוגמה: איתות קניה מיד בסגירה אם התנאים מתאימים
                    signal = "קניה מיידית בסגירה" if change > 0 else "המתנה"
                    
                    results.append({
                        "סימול (Ticker)": ticker,
                        "מחיר סגירה אחרון": round(last_close, 2),
                        "שינוי יומי (%)": round(change, 2),
                        "איתות אסטרטגיה": signal
                    })
            except Exception as e:
                continue
                
        if results:
            df_results = pd.DataFrame(results)
            st.success("הסריקה הושלמה בהצלחה!")
            st.dataframe(df_results, use_container_width=True)
        else:
            st.warning("לא נמצאו נתונים להצגה.")
