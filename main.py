import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing Master Scanner & Manual Check", layout="wide")

st.title("📊 Pro Swing - Master Strategy Platform")
st.write("פלטפורמת ניהול וסריקה: סריקה רוחבית לכלל המדדים או בדיקה ידנית ממוקדת לסימול ספציפי.")

# חלוקה ללשוניות (טאבים) נוחות
tab1, tab2 = st.tabs(["📊 סריקה רוחבית למדדים", "🔍 בדיקה ידנית לסימבול ספציפי"])

# ==================== טאב 1: סריקה רוחבית למדדים ====================
with tab1:
    st.subheader("סריקה אוטומטית מלאה למניות S&P 500, Russell 2000 ותל אביב 125")
    
    @st.cache_data(ttl=86400)
    def get_comprehensive_universe():
        sp500_core = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH", "JNJ", 
            "XOM", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP", "KO", "BAC", 
            "AVGO", "COST", "MCD", "TMO", "CSCO", "ACN", "WMT", "LIN", "ABT", "DHR", "NFLX", 
            "PDD", "AMD", "QCOM", "TXN", "AMGN", "IBM", "HON", "SBUX", "GE", "LMT", "INTC",
            "ISRG", "CAT", "DIS", "BKNG", "NOW", "PFE", "AMAT", "GILD", "MDLZ", "ADI", "ADP",
            "LRCX", "VRTX", "TJX", "CB", "PANW", "SNPS", "C", "MO", "REGN", "CI", "BX", "BSX",
            "DUK", "SLB", "SO", "EQIX", "SHW", "ITW", "ZTS", "WM", "CL", "T", "ETN", "CDNS",
            "MU", "MMC", "PNC", "ICE", "USB", "CSX", "EOG", "NOC", "BDX", "FCX", "ORCL", "CRM",
            "APD", "TT", "BA", "WFC", "AXP", "GS", "MS", "RTX", "DE", "PLD", "SPG"
        ]
        russell_small_caps = [
            "IWM", "RUT", "RRC", "AA", "AAL", "AAON", "ABCB", "ABG", "ABM", "ACIW", 
            "ACLS", "ADC", "ADTN", "AEIS", "AGCO", "AGI", "AHCO", "AIN", "AKR", "ALRM",
            "SMCI", "PLTR", "ARM", "COIN", "HOOD", "RIVN", "DKNG", "UBER", "ABNB", "SQ",
            "ROKU", "PINS", "SNAP", "TWLO", "MDB", "NET", "DDOG", "ZS", "CRWD", "PATH"
        ]
        ta_125 = [
            "TEVA.TA", "ESLT.TA", "POLI.TA", "LUMI.TA", "BEZQ.TA", "NICE.TA", "OPC.TA", 
            "ENLT.TA", "ISRA.TA", "BIG.TA", "AZRM.TA", "DLEG.TA", "FIBI.TA", "EIM.TA",
            "ARPT.TA", "MLSR.TA", "PHOE.TA", "CLIS.TA", "ENRG.TA", "ORL.TA", "BLSR.TA"
        ]
        return list(set(sp500_core + russell_small_caps + ta_125))

    comprehensive_universe = get_comprehensive_universe()
    st.info(f"מאגר הסריקה מוגדר ל-{len(comprehensive_universe)} מניות מרכזיות.")

    if st.button("הפעל סריקה מלאה על כל השוק"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        batch_size = 30
        total_batches = (len(comprehensive_universe) + batch_size - 1) // batch_size
        
        try:
            for b_idx, i in enumerate(range(0, len(comprehensive_universe), batch_size)):
                batch = comprehensive_universe[i:i+batch_size]
                status_text.text(f"סורק קבוצה {b_idx + 1} מתוך {total_batches}...")
                progress_bar.progress((b_idx + 1) / total_batches)
                
                try:
                    data_daily = yf.download(batch, period="6mo", progress=False, group_by="ticker", auto_adjust=True)
                    data_weekly = yf.download(batch, period="1y", interval="1wk", progress=False, group_by="ticker", auto_adjust=True)
                    
                    for ticker in batch:
                        try:
                            if len(batch) == 1:
                                df_d = data_daily
                                df_w = data_weekly
                            else:
                                df_d = data_daily[ticker].dropna(how="all") if ticker in data_daily.columns.levels[0] else pd.DataFrame()
                                df_w = data_weekly[ticker].dropna(how="all") if ticker in data_weekly.columns.levels[0] else pd.DataFrame()
                                
                            if df_d is not None and not df_d.empty and len(df_d) > 50:
                                close_s = df_d['Close'].dropna()
                                high_s = df_d['High'].dropna()
                                
                                close = float(close_s.iloc[-1])
                                prev_close = float(close_s.iloc[-2])
                                
                                sma50 = float(close_s.rolling(50).mean().iloc[-1])
                                sma200 = float(close_s.rolling(min(200, len(close_s))).mean().iloc[-1])
                                ema21 = float(close_s.ewm(span=21, adjust=False).mean().iloc[-1])
                                
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
                                is_near_setup = (abs(dist_from_entry) <= 3.5) or (close >= resistance * 0.98)
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
                except Exception:
                    continue
                    
            progress_bar.empty()
            status_text.empty()
            
            if results:
                st.success(f"הסריקה הושלמה! נמצאו {len(results)} מניות תואמות.")
                st.dataframe(pd.DataFrame(results), use_container_width=True)
            else:
                st.warning("לא נמצאו מניות העונות על מלוא הקריטריונים ברגע זה.")
        except Exception as e:
            st.error(f"שגיאה: {e}")

# ==================== טאב 2: בדיקה ידנית לסימבול ספציפי ====================
with tab2:
    st.subheader("בדיקה והרצת אסטרטגיה ידנית לסימול בודד")
    st.write("הקלד סימול מניה (לדוגמה: `APD`, `TT`, `TSLA`, `TEVA.TA`) ובדוק את מצבה המדויק מול כללי האסטרטגיה.")
    
    manual_ticker = st.text_input("הכנס סימול לבדיקה:", value="APD").upper().strip()
    
    if st.button("הרץ בדיקה לסימבול"):
        if manual_ticker:
            with st.spinner(f'מנתח לעומק את {manual_ticker}...'):
                try:
                    df_d = yf.download(manual_ticker, period="6mo", progress=False, auto_adjust=True)
                    df_w = yf.download(manual_ticker, period="1y", interval="1wk", progress=False, auto_adjust=True)
                    
                    if isinstance(df_d.columns, pd.MultiIndex):
                        df_d.columns = df_d.columns.get_level_values(0)
                    if isinstance(df_w.columns, pd.MultiIndex):
                        df_w.columns = df_w.columns.get_level_values(0)
                        
                    if df_d is not None and not df_d.empty and len(df_d) > 50:
                        close_s = df_d['Close'].dropna()
                        high_s = df_d['High'].dropna()
                        
                        close = float(close_s.iloc[-1])
                        prev_close = float(close_s.iloc[-2])
                        
                        sma50 = float(close_s.rolling(50).mean().iloc[-1])
                        sma200 = float(close_s.rolling(min(200, len(close_s))).mean().iloc[-1])
                        ema21 = float(close_s.ewm(span=21, adjust=False).mean().iloc[-1])
                        
                        # בדיקת שבועי
                        weekly_positive = False
                        w_status_details = []
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
                        score = 4 if (weekly_positive and close > sma50 and sma50 > sma200) else 3

                        st.success(תוצאות ניתוח עבור: **{manual_ticker}**)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("מחיר נוכחי", f"${close:.2f}", f"{((close-prev_close)/prev_close)*100:.2f}%")
                        col2.metric("מחיר כניסה אסטרטגי", f"${entry_price:.2f}")
                        col3.metric("מרחק ממחיר הכניסה", f"{dist_from_entry:.2f}%")
                        
                        st.markdown("### 📋 נתוני האסטרטגיה המלאים:")
                        st.json({
                            "סימול": manual_ticker,
                            "סטטוס סט-אפ": setup_type,
                            "ציון אמינות (Conviction Score)": f"{score} / 4",
                            "גרף שבועי (שיפוע 4 ממוצעים)": "חיובי מלא 🟢" if weekly_positive else "שלילי / מעורב 🔴",
                            "ממוצע 50 יומי": round(sma50, 2),
                            "ממוצע 200 יומי": round(sma200, 2),
                            "EMA 21": round(ema21, 2)
                        })
                    else:
                        st.error("לא נמצאו נתונים מספיקים עבור הסימול שהוזן.")
                except Exception as e:
                    st.error(f"שגיאה בשליפת הנתונים: {e}")
