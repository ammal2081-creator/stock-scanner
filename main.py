import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing Live Scanner & Weekly Filter", layout="wide")

st.title("📊 Pro Swing - TradingView Sync + Weekly Filter")
st.write("לוח בקרה המקבל איתותים מטריידינגויו ומאמת אוטומטית שכל ממוצעי הגרף השבועי בשיפוע חיובי.")

if "alerts_log" not in st.session_state:
    st.session_state.alerts_log = []

# קליטת איתות חדש מטריידינגויו דרך ה-URL / Webhook
query_params = st.query_params
if "ticker" in query_params and "setup" in query_params:
    ticker = query_params.get("ticker").upper()
    setup = query_params.get("setup")
    price = query_params.get("price", "N/A")
    
    # בדיקה פייתונית אוטומטית לגרף השבועי (אימות שיפוע ארבעת הממוצעים)
    weekly_status = "שלילי / מעורב 🔴"
    passed_weekly_filter = False
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
                    passed_weekly_filter = True
    except:
        weekly_status = "שגיאה בבדיקה"

    new_alert = {
        "סימול": ticker,
        "סטטוס אסטרטגיה": setup,
        "מחיר כניסה ($)": price,
        "אימות גרף שבועי": weekly_status,
        "מאושר לסחר?": "כן 🚀" if passed_weekly_filter else "לא (נפסל בשבועי) ❌",
        "זמן קבלה": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # הוספה ללוג אם אינו קיים כפול אחרון
    if not any(d['סימול'] == ticker and d['סטטוס אסטרטגיה'] == setup for d in st.session_state.alerts_log):
        st.session_state.alerts_log.append(new_alert)

st.subheader("📌 איתותים פעילים (לאחר סינון ואימות שבועי):")

if st.session_state.alerts_log:
    df_live = pd.DataFrame(st.session_state.alerts_log)
    st.dataframe(df_live, use_container_width=True)
else:
    st.info("מחכה לקליטת איתותים מטריידינגויו...")

st.markdown("---")
st.markdown("### 🔗 כתובת ה-Webhook להגדרה ב-TradingView:")
app_url = "https://stock-scanner-afawfrawzuj93pjjbne6o.streamlit.app"
st.code(f"{app_url}/?ticker={{ticker}}&setup={{strategy.market_position}}&price={{close}}", language="text")
