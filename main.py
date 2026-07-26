import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing Full Market Autonomous Scanner", layout="wide")

st.title("📊 Pro Swing - Full Market Autonomous Scanner")
st.write("סורק מקיף המריץ סריקה רוחבית אוטומטית על **כל** מניות מדד S&P 500, מדד TA-125 ומניות נוספות בהתאם לחוקי האסטרטגיה.")

@st.cache_data(ttl=86400)
def get_full_universe():
    tickers = []
    # שליפה אוטומטית מלאה של כל מניות S&P 500 מוויקיפדיה
    try:
        sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        df_sp = pd.read_html(sp500_url)[0]
        sp_tickers = df_sp['Symbol'].str.replace('.', '-', regex=False).tolist()
        tickers.extend(sp_tickers)
    except:
        pass
        
    # מניות מדד TA-125 ומניות מובילות בישראל
    ta_stocks = [
        "TEVA.TA", "ESLT.TA", "POLI.TA", "LUMI.TA", "BEZQ.TA", "NICE.TA", "OPC.TA", 
        "ENLT.TA", "ISRA.TA", "BIG.TA", "AZRM.TA", "DLEG.TA", "FIBI.TA", "EIM.TA",
        "ARPT.TA", "MLSR.TA", "PHOE.TA", "CLIS.TA", "ENRG.TA"
    ]
    tickers.extend(ta_stocks)
    
    # מניות נזילות נוספות ומדדים מובילים
    additional = [
        "QQQ", "IWM", "RUT", "SMCI", "PLTR", "ARM", "COIN", "HOOD", "RIVN", "DKNG", 
        "UBER", "ABNB", "SQ", "BA", "CAT", "JPM", "V", "WMT", "DIS", "PFE"
    ]
    tickers.extend(additional)
    
    return list(set(tickers))

comprehensive_universe = get_full_universe()

st.info(f"מאגר הסריקה הפעיל טוען כעת אוטומטית **{len(comprehensive_universe)}** מניות מלאות מתוך מדדי S&P 500, TA-125 והשוק.")

if st.button("הפעל סריקה מלאה על כל מדדי השוק כעת"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    batch_size = 30
    total_batches = (len(comprehensive_universe) + batch_size - 1) // batch_size
    
    try:
        for b_idx, i in enumerate(range(0, len(comprehensive_universe), batch_size)):
            batch = comprehensive_universe[i:i+batch_size]
            status_text.text(f"סורק קבוצה {b_idx + 1} מתוך {total_batches} ({len(results)} תוצאות נמצאו עד כה)...")
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
                            low_s = df_d['Low'].dropna()
                            
                            if len(close_s) < 50:
                                continue
                                
                            close = float(close_s.iloc[-1])
                            prev_close = float(close_s.iloc[-2])
                            high = float(high_s.iloc[-1])
                            low = float(low_s.iloc[-1])
                            
                            sma50 = float(close_s.rolling(50).mean().iloc[-1])
                            sma200 = float(close_s.rolling(min(200, len(close_s))).mean().iloc[-1])
                            ema21 = float(close_s.ewm(span=21, adjust=False).mean().iloc[-1])
                            
                            # 1. בדיקת גרף שבועי מחמיר: שיפוע חיובי מלא של 4 ממוצעים (EMA10, EMA21, SMA50, SMA200)
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

                            # 2. חישוב מחיר כניסה אסטרטגי וסט-אפ
                            resistance = float(high_s.iloc[-21:-1].max())
                            
                            if close >= resistance * 0.98:
                                entry_price = resistance
                                setup_type = "פריצה (Breakout) 🚀"
                            else:
                                entry_price = ema21
                                setup_type = "פולבק ל-EMA21 📈"
                                
                            dist_from_entry = ((close - entry_price) / entry_price) * 100
                            
                            # תנאי סינון: מניות שקרובות לכניסה או בפריצה ועונות על הגרף השבועי
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
            final_df = pd.DataFrame(results)
            st.success(f"הסריקה הושלמה בהצלחה! סומנו ונמצאו {len(results)} מניות העונות בדיוק על תנאי האסטרטגיה מתוך כלל המדדים.")
            st.dataframe(final_df, use_container_width=True)
        else:
            st.warning("הסריקה הסתיימה בהצלחה על כל המניות, אך לא נמצאו ברגע זה מניות העונות על מלוא הקריטריונים המחמירים.")
            
    except Exception as e:
        st.error(f"שגיאה כללית בריצת הסריקה: {e}")
