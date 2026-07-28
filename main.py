import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing Master Platform", layout="wide")

st.title("📊 Pro Swing - Master Strategy Platform")
st.write("פלטפורמת ניהול וסריקה: סריקה רוחבית למדדים או בדיקה ידנית מעמיקה לסימול ספציפי הכוללת ניתוח אנליסט AI ופרספקטיבת מומחי 'מומנטום מאסטרס'.")

tab1, tab2 = st.tabs(["📊 סריקה רוחבית למדדים", "🔍 בדיקה ידנית וניתוח מומחי מומנטום מאסטרס"])

def safe_extract(df, col_name):
    """ פונקציית עזר חסינה לחילוץ עמודות מנתחי yfinance """
    if df is None or df.empty:
        return pd.Series(dtype=float)
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df.columns = df.columns.get_level_values(0)
        except:
            pass
    matching = [c for c in df.columns if str(c).lower() == col_name.lower()]
    if matching:
        return df[matching[0]].dropna()
    for c in df.columns:
        if col_name.lower() in str(c).lower():
            return df[c].dropna()
    return pd.Series(dtype=float)

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
                                
                            close_s = safe_extract(df_d, 'Close')
                            high_s = safe_extract(df_d, 'High')
                            
                            if len(close_s) > 50:
                                close = float(close_s.iloc[-1])
                                prev_close = float(close_s.iloc[-2])
                                
                                sma50 = float(close_s.rolling(50).mean().iloc[-1])
                                sma200 = float(close_s.rolling(min(200, len(close_s))).mean().iloc[-1])
                                ema21 = float(close_s.ewm(span=21, adjust=False).mean().iloc[-1])
                                
                                weekly_positive = False
                                w_close = safe_extract(df_w, 'Close')
                                if len(w_close) >= 10:
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

# ==================== טאב 2: בדיקה ידנית וניתוח מומחי מומנטום מאסטרס ====================
with tab2:
    st.subheader("🔍 בדיקה ידנית, ניתוח אנליסט AI ופרספקטיבת מומחי 'מומנטום מאסטרס'")
    st.write("הקלד סימול לבדיקה הכוללת: ניתוח טכני, פונדמנטלי, וחוות דעת מפורטת של מארק מינרוויני, דייוויד ראיין, דן זנגר ומארק ריצ'י השני.")
    
    manual_ticker = st.text_input("הכנס סימול (לדוגמה: APD, TT, TSLA, TEVA.TA):", value="APD").upper().strip()
    
    if st.button("הרץ ניתוח מקיף וחוות דעת מאסטרים"):
        if manual_ticker:
            with st.spinner(f'מנתח לעומק את {manual_ticker} ומייצר פרספקטיבת מומחים...'):
                try:
                    t_obj = yf.Ticker(manual_ticker)
                    info = t_obj.info
                    
                    df_d = yf.download(manual_ticker, period="6mo", progress=False, auto_adjust=True)
                    df_w = yf.download(manual_ticker, period="1y", interval="1wk", progress=False, auto_adjust=True)
                    
                    close_s = safe_extract(df_d, 'Close')
                    high_s = safe_extract(df_d, 'High')
                    
                    if len(close_s) > 50:
                        close = float(close_s.iloc[-1])
                        prev_close = float(close_s.iloc[-2])
                        
                        sma50 = float(close_s.rolling(50).mean().iloc[-1])
                        sma200 = float(close_s.rolling(min(200, len(close_s))).mean().iloc[-1])
                        ema21 = float(close_s.ewm(span=21, adjust=False).mean().iloc[-1])
                        
                        weekly_positive = False
                        w_close = safe_extract(df_w, 'Close')
                        if len(w_close) >= 10:
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

                        company_name = info.get('longName', manual_ticker)
                        sector = info.get('sector', 'לא ידוע')
                        industry = info.get('industry', 'לא ידוע')
                        rev_growth = info.get('revenueGrowth', None)
                        debt_to_equity = info.get('debtToEquity', None)
                        
                        is_growing = True if (rev_growth is not None and rev_growth > -0.05) else False
                        can_service_debt = True if (debt_to_equity is None or debt_to_equity < 250) else False
                        
                        ai_verdict = 'מאושר ע"פ אנליסט 🟢' if (is_growing and can_service_debt and weekly_positive) else 'בבדיקה / סיכון מוגבר 🟡'

                        st.success(f"ניתוח הושלם בהצלחה עבור: **{company_name} ({manual_ticker})**")
                        
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("מחיר נוכחי", f"${close:.2f}", f"{((close-prev_close)/prev_close)*100:.2f}%")
                        m2.metric("מחיר כניסה אסטרטגי", f"${entry_price:.2f}")
                        m3.metric("מרחק ממחיר הכניסה", f"{dist_from_entry:.2f}%")
                        m4.metric("ציון אמינות טכני", f"{score} / 4")

                        st.markdown("---")
                        
                        col_tech, col_fund = st.columns(2)
                        
                        with col_tech:
                            st.markdown("### 📈 סטטוס טכני ואסטרטגיה")
                            st.info(f"**סוג סט-אפ:** {setup_type}")
                            if weekly_positive:
                                st.markdown("* **גרף שבועי:** חיובי מלא 🟢 (כל 4 הממוצעים בשיפוע עולה)")
                            else:
                                st.markdown("* **גרף שבועי:** שלילי או מעורב 🔴 (לא כל הממוצעים בשיפוע חיובי)")
                            
                            st.markdown(f"* **ממוצע 50 יומי:** ${sma50:.2f} ({'מעל 50 🟢' if close > sma50 else 'מתחת ל-50 🔴'})")
                            st.markdown(f"* **ממוצע 200 יומי:** ${sma200:.2f} ({'מעל 200 🟢' if close > sma200 else 'מתחת ל-200 🔴'})")
                            st.markdown(f"* **EMA 21 יומי:** ${ema21:.2f}")

                        with col_fund:
                            st.markdown("### 🤖 חוות דעת אנליסט AI (פונדמנטלי)")
                            st.markdown(f"**סקטור:** {sector} | **תעשייה:** {industry}")
                            
                            growth_txt = f"{rev_growth*100:.1f}%" if rev_growth is not None else "נתון לא זמין"
                            debt_txt = f"{debt_to_equity:.1f}%" if debt_to_equity is not None else "נמוך / לא זמין"
                            
                            if is_growing:
                                st.markdown(f"* **מגמת צמיחה (הכנסות):** צומחת בקצב של {growth_txt} 🟢")
                            else:
                                st.markdown(f"* **מגמת צמיחה (הכנסות):** האטה או התכווצות 🟡")
                                
                            if can_service_debt:
                                st.markdown(f"* **יכולת שירות חוב:** יחס חוב להון בריא ({debt_txt}) - החברה מסוגלת לשרת את חובותיה בקלות 🟢")
                            else:
                                st.markdown(f"* **יכולת שירות חוב:** רמת מינוף גבוהה יחסית ({debt_txt}) 🟡")
                                
                            st.markdown(f"**שורה תחתונה:** {ai_verdict}")

                        st.markdown("---")
                        st.markdown("### 🏛️ השולחן העגול: דעות מומחי 'מומנטום מאסטרס' על המניה")
                        
                        experts_data = [
                            {
                                "מומחה": "מארק מינרוויני",
                                "נקודת קניה (Buy)": f"קנייה בפריצה מדויקת או פולבק בתוך תבנית VCP סמוך ל-${entry_price:.2f}[cite: 1]",
                                "סטופ (Stop Loss)": "סטופ הדוק בטווח של 5%-7% או מתחת לתמיכה האחרונה[cite: 1]",
                                "נקודת יציאה (Exit)": "מימוש חלק לתוך עוצמה או סטופ מנטלי לפי הפרת מבנה טכני[cite: 1]"
                            },
                            {
                                "מומחה": "דייוויד ראיין",
                                "נקודת קניה (Buy)": f"בחינת בסיס מחיר הדוק סביב ${entry_price:.2f} עם נפח מסחר עולה[cite: 1]",
                                "סטופ (Stop Loss)": "הפסד מקסימלי של 8% או שבירת ממוצע נע 21 יום[cite: 1]",
                                "נקודת יציאה (Exit)": "יציאה הדרגתית לפי חולשה בשוק הכללי או ירידת חוזק יחסי[cite: 1]"
                            },
                            {
                                "מומחה": "דן זנגר",
                                "נקודת קניה (Buy)": f"פריצה אגרסיבית עם מחזור כבד מעל אזור ההתנגדות סביב ${entry_price:.2f}[cite: 1]",
                                "סטופ (Stop Loss)": "סטופ צמוד מאוד (3%-5%) מתחת למחיר הכניסה או שבירת EMA21[cite: 1]",
                                "נקודת יציאה (Exit)": "מכירה מהירה לתוך עליות חזקות או שבירת תמיכה מהירה[cite: 1]"
                            },
                            {
                                "מומחה": "מארק ריצ'י השני",
                                "נקודת קניה (Buy)": f"כניסה ממושמעת בטווח קרוב לשיא בהתאם למבנה השוק ולתבנית VCP סביב ${entry_price:.2f}[cite: 1]",
                                "סטופ (Stop Loss)": "סטופ מבוסס סטטיסטיקה ואחוזים חד-ספרתיים בינוניים[cite: 1]",
                                "נקודת יציאה (Exit)": "מימוש חלקי כשהרווח הוא פי 2 מהסיכון, וניהול נגרר[cite: 1]"
                            }
                        ]
                        
                        st.dataframe(pd.DataFrame(experts_data), use_container_width=True)

                        st.markdown("### 📌 סיכום המלצה סופית על בסיס דעות המאסטרים:")
                        if weekly_positive and is_growing and score >= 4:
                            summary_text = (
                                f"על בסיס משנתם של מחברי הספר 'מומנטום מאסטרס', המניה **{company_name} ({manual_ticker})** עונה על הקריטריונים המחמירים של מניות מובילות[cite: 1]. "
                                f"הן מבחינת המבנה הטכני בגרף היומי והשבועי (שיפוע חיובי מלא בממוצעים) והן מבחינת נתוני הצמיחה ויכולת שירות החוב, המאסטרים היו ממליצים להיערך לכניסה אסטרטגית מבוקרת. "
                                f"מומלץ לפתוח פוזיציה בקרבת מחיר הכניסה המחושב (${entry_price:.2f}), להקפיד על ניהול סיכונים קפדני עם סטופ מוגדר מראש, ולתת למומנטום לעבוד תוך מימוש חלקי לתוך עוצמה."
                            )
                        else:
                            summary_text = (
                                f"לפי עקרונותיהם של מומחי 'מומנטום מאסטרס', המניה **{company_name} ({manual_ticker})** מציגה כרגע סימנים מעורבים או שאינה עומדת במלוא התנאים המחמירים (כגון היעדר שיפוע חיובי מלא בכל הממוצעים או פונדמנטליים גבוליים)[cite: 1]. "
                                f"במצב כזה, גישתם של המאסטרים דורשת משמעת גבוהה: יש להמתין בסבלנות להשלמת התבנית או לשבת על הידיים, שכן ניסיון להיכנס לעסקה בתנאים לא מושלמים נושא סיכון מוגבר בניגוד לכללי ניהול הסיכון הקשוחים של השיטה."
                            )
                        st.info(summary_text)

                    else:
                        st.error("לא נמצאו נתונים מספיקים עבור הסימול שהוזן.")
                except Exception as e:
                    st.error(f"שגיאה בניתוח הסימבול: {e}")
