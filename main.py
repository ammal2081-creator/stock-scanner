import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing Master V6 - Live Webhook & Scanner", layout="wide")

st.title("📊 Pro Swing - Real-Time TradingView Sync (S&P 500, Russell 2000, TA-125)")
st.write("לוח בקרה חי הקולט את כל האיתותים מכלל המדדים ישירות מהאסטרטגיה בטריידינגויו ומאמת אותם.")

if "alerts_log" not in st.session_state:
    st.session_state.alerts_log = []

# קליטת איתות חדש מטריידינגויו (למשל APD, TT וכו')
query_params = st.query_params
if "ticker" in query_params and "setup" in query_params:
    ticker = query_params.get("ticker").upper()
    setup = query_params.get("setup")
    price = query_params.get("price", "N/A")
    score = query_params.get("score", "4 / 4")
    
    # אימות אוטומטי לגרף השבועי (שיפוע 4 ממוצעים)
    weekly_status = "שלילי / מעורב 🔴"
    passed_filter = False
    try:
        df_weekly = yf.download(ticker, period="1y", interval="1wk", progress=False, auto_adjust=True)
        if df_weekly is not None and not df_weekly.empty:
            if isinstance(df_weekly.columns, pd.MultiIndex):
                df_weekly.columns = df_weekly.columns.get_level_values(0)
            if len(df_weekly) >= 10:
                w_close = df_weekly['Close'].dropna()
                w_ema10 = w_close.ewm(span=10, adjust=False).mean()
                w_ema21 = w_close.ewm(span=21, adjust=False).mean()
                w_sma50 = w_close.rolling(50).mean()
                w_sma200 = w_close.rolling(200).mean()
                
                s1 = w_ema10.iloc[-1] > w_ema10.iloc[-2]
                s2 = w_ema21.iloc[-1] > w_ema21.iloc[-2]
                s3 = w_sma50.iloc[-1] > w_sma50.iloc[-2] if not pd.isna(w_sma50.iloc[-1]) else True
                s4 = w_sma200.iloc[-1] > w_sma200.iloc[-2] if not pd.isna(w_sma200.iloc[-1]) else True
                
                if s1 and s2 and s3 and s4:
                    weekly_status = "חיובי מלא (כל הממוצעים בשיפוע) 🟢"
                    passed_filter = True
    except:
        weekly_status = "בבחינה"

    new_alert = {
        "סימול": ticker,
        "סטטוס סט-אפ (טריידינגויו)": setup,
        "מחיר כניסה ($)": price,
        "ציון אמינות": score,
        "גרף שבועי": weekly_status,
        "אישור סופי לסחר": "מאושר 🚀" if passed_filter else "במעקב",
        "זמן קבלה": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # מניעת כפילויות של אותו איתות פעיל
    if not any(d['סימול'] == ticker and d['סטטוס סט-אפ (טריידינגויו)'] == setup for d in st.session_state.alerts_log):
        st.session_state.alerts_log.append(new_alert)

st.subheader("📌 מניות וסט-אפים פעילים מכלל המדדים:")

if st.session_state.alerts_log:
    df_live = pd.DataFrame(st.session_state.alerts_log)
    st.dataframe(df_live, use_container_width=True)
else:
    st.info("האתר מוכן. ברגע שתגדיר את ה-Webhook בטריידינגויו עבור המדדים, כל מניה שתיתן איתות (כמו APD או TT) תופיע כאן מיד.")

st.markdown("---")
st.markdown("### 🔗 כתובת ה-Webhook להגדרה ב-TradingView:")
app_url = "https://stock-scanner-afawfrawzuj93pjjbne6o.streamlit.app"
st.code(f"{app_url}/?ticker={{ticker}}&setup={{strategy.market_position}}&price={{close}}&score=4", language="text")
