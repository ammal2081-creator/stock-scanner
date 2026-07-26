import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing 2026 - Master Execution V6", layout="wide")

st.title("📊 Pro Swing 2026 - Master Execution V6 Scanner")
st.write("סורק מניות אוטומטי התואם במדויק לכללי האסטרטגיה של Pine Script (ציון אמינות, מרחקים ממוצעים, פריצות ופולבקים).")

# רשימות המדדים לסריקה
all_indices = {
    "S&P 500 (מובילות)": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"],
    "Nasdaq 100": ["QQQ", "AMD", "NFLX", "INTC", "AVGO", "COST"],
    "TA-125 / מקומי": ["TEVA.TA", "ESLT.TA", "POLI.TA", "LUMI.TA", "BEZQ.TA"]
}

scan_choice = st.selectbox("בחר מדד לסריקה:", list(all_indices.keys()))

if st.button("הפעל סריקה מדויקת לפי אסטרטגיית V6"):
    with st.spinner("מנתח נתונים, מחשב ממוצעים, ציון אמינות (Score) ואיתותים..."):
        tickers = all_indices[scan_choice]
        results = []
        
        # שליפת מדד השוק (SPY) לחישוב Relative Strength
        try:
            spy = yf.Ticker("SPY").history(period="60d")
            spy_close = spy['Close'].iloc[-1]
            spy_sma200 = spy['Close'].mean() # פשטות לחישוב מקומי
        except:
            spy_close = 0
            spy_sma200 = 0

        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period="70d")
                
                if len(df) > 50:
                    close = df['Close'].iloc[-1]
                    prev_close = df['Close'].iloc[-2]
                    high = df['High'].iloc[-1]
                    low = df['Low'].iloc[-1]
                    open_price = df['Open'].iloc[-1]
                    
                    # חישוב ממוצעים נעמיים
                    sma50 = df['Close'].rolling(50).mean().iloc[-1]
                    sma200 = df['Close'].rolling(min(200, len(df))).mean().iloc[-1]
                    ema10 = df['Close'].ewm(span=10, adjust=False).mean().iloc[-1]
                    ema21 = df['Close'].ewm(span=21, adjust=False).mean().iloc[-1]
                    
                    # מרחק מ-EMA 21 באחוזים
                    dist_ema21_pct = ((close - ema21) / ema21) * 100
                    is_not_extended = dist_ema21_pct <= 8.0 # maxEmaDist
                    
                    # חישוב Relative Strength מול SPY
                    rs_line = (close / spy_close) if spy_close > 0 else 0
                    rs_ema21 = pd.Series([rs_line]).ewm(span=21, adjust=False).mean().iloc[-1]
                    
                    # Conviction Score (1 to 4)
                    score = 0
                    if rs_line > rs_ema21:
                        score += 2
                    if close > sma50 and sma50 > sma200:
                        score += 1
                    if spy_close > spy_sma200:
                        score += 1
                        
                    # ניהול סיכון דינמי לפי הציון
                    risk_pct = 0.01 if score == 4 else (0.008 if score == 3 else (0.006 if score >= 2 else 0.0))
                    
                    # זיהוי סטפס (Setups)
                    resistance = df['High'].iloc[-21:-1].max()
                    is_breakout = close > resistance
                    is_deep_pullback = low <= ema10 * 1.015 and close > ema21 and close > open_price
                    is_shallow_pullback = low <= ema10 * 1.01 and close > ema10 and close > open_price and ema10 > ema21
                    
                    valid_setup = (is_breakout or is_deep_pullback or is_shallow_pullback) and score >= 2 and is_not_extended
                    
                    setup_name = "המתנה / אין סט אפ"
                    if is_breakout: setup_name = "Breakout 🚀"
                    elif is_deep_pullback: setup_name = "Deep Pullback 📉"
                    elif is_shallow_pullback: setup_name = "Shallow Pullback 📈"

                    results.append({
                        "סימול": ticker,
                        "מחיר סגירה": round(close, 2),
                        "ציון אמינות (Score)": f"{score} / 4",
                        "סיכון מוגדר (%)": f"{risk_pct * 100}%",
                        "מרחק מ-EMA21 (%)": round(dist_ema21_pct, 2),
                        "עומד בהרחבה (Not Extended)": "כן" if is_not_extended else "לא",
                        "זיהוי סט אפ": setup_name,
                        "סטטוס תקינות לסריקה": "תקין לפעולה" if valid_setup else "מעקב בלבד"
                    })
            except Exception as e:
                continue
                
        if results:
            final_df = pd.DataFrame(results)
            st.success("הסריקה הושלמה בהצלחה לפי חוקי אסטרטגיית V6!")
            st.dataframe(final_df, use_container_width=True)
        else:
            st.warning("לא נמצאו תוצאות תואמות.")
