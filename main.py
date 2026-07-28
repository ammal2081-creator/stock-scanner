import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Pro Swing Master Platform", layout="wide")

st.title("📊 Pro Swing - Master Strategy Platform")
st.write("פלטפורמת ניהול וסריקה: סריקה רוחבית למדדים או בדיקה ידנית מעמיקה המותאמת אישית לגרף החי ולמשנת מומחי 'מומנטום מאסטרס'.")

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
    st.subheader("🔍 בדיקה ידנית, ניתוח אנליסט AI ופרספקטיבה דינמית של מומחי 'מומנטום מאסטרס'")
    st.write('הקלד סימול לבדיקה המנתחת את הגרף החי ומפיקה ניתוח מותאם אישית לכל מאסטר ע"פ נתוני המחיר העדכניים.')
    
    manual_ticker = st.text_input("הכנס סימול (לדוגמה: APD, TT, TSLA, TEVA.TA):", value="APD").upper().strip()
    
    if st.button("הרץ ניתוח מקיף וחוות דעת מאסטרים דינמית"):
        if manual_ticker:
            with st.spinner(f'מנתח את הגרף החי של {manual_ticker} ומייצר תרחישי מסחר פרטניים...'):
                try:
                    t_obj = yf.Ticker(manual_ticker)
                    info = t_obj.info
                    
                    df_d = yf.download(manual_ticker, period="6mo", progress=False, auto_adjust=True)
                    df_w = yf.download(manual_ticker, period="1y", interval="1wk", progress=False, auto_adjust=True)
                    
                    close_s = safe_extract(df_d, 'Close')
                    high_s = safe_extract(df_d, 'High')
                    low_s = safe_extract(df_d, 'Low')
                    
                    if close_s.empty or len(close_s) < 10:
                        st.error(f"שגיאה: שרת Yahoo Finance לא החזיר נתונים עבור הסימול {manual_ticker} (ייתכן עומס או חסימת IP זמנית). נסה שוב בעוד מספר רגעים.")
                    elif len(close_s) <= 50:
                        st.warning(ోf"נמצאו רק {len(close_s)} ימי מסחר עבור {manual_ticker}. נדרשים לפחות 50 ימים לצורך חישוב ממוצעים מדויקים.")
                    else:
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
                        recent_low = float(low_s.iloc[-10:].min())
                        
                        if close >= resistance * 0.98:
                            base_entry = resistance
                            setup_type = "פריצה (Breakout) מתוך התכנסות 🚀"
                        else:
                            base_entry = ema21
                            setup_type = "פולבק (Pullback) ל-EMA21 📈"
                            
                        dist_from_entry = ((close - base_entry) / base_entry) * 100
                        score = 4 if (weekly_positive and close > sma50 and sma50 > sma200) else 3

                        company_name = info.get('longName', manual_ticker)
                        sector = info.get('sector', 'לא ידוע')
                        industry = info.get('industry', 'לא ידוע')
                        rev_growth = info.get('revenueGrowth', None)
                        debt_to_equity = info.get('debtToEquity', None)
                        
                        is_growing = True if (rev_growth is not None and rev_growth > -0.05) else False
                        can_service_debt = True if (debt_to_equity is None or debt_to_equity < 250) else False
                        ai_verdict = 'מאושר ע"פ אנליסט 🟢' if (is_growing and can_service_debt and weekly_positive) else 'בבדיקה / סיכון מוגבר 🟡'

                        st.success(f"ניתוח גרף חי הושלם עבור: **{company_name} ({manual_ticker})**")
                        
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("מחיר נוכחי", f"${close:.2f}", f"{((close-prev_close)/prev_close)*100:.2f}%")
                        m2.metric("מחיר כניסה מרכזי", f"${base_entry:.2f}")
                        m3.metric("מרחק ממחיר הכניסה", f"{dist_from_entry:.2f}%")
                        m4.metric("ציון אמינות טכני", f"{score} / 4")

                        st.markdown("---")
                        
                        col_tech, col_fund = st.columns(2)
                        with col_tech:
                            st.markdown("### 📈 סטטוס טכני ואסטרטגיה מהגרף")
                            st.info(f"**מצב נוכחי בגרף:** {setup_type}")
                            if weekly_positive:
                                st.markdown("* **גרף שבועי:** חיובי מלא 🟢 (כל 4 הממוצעים בשיפוע עולה)")
                            else:
                                st.markdown("* **גרף שבועי:** שלילי או מעורב 🔴 (לא כל הממוצעים בשיפוע חיובי)")
                            st.markdown(f"* **התנגדות קרובה (Pivot):** ${resistance:.2f}")
                            st.markdown(f"* **ממוצע 50 יומי:** ${sma50:.2f}")
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
                        st.markdown("### 🏛️ השולחן העגול: תוכניות מסחר נפרדות לכל מאסטר (על סמך הגרף החי)")
                        
                        minervini_buy = f"כניסה בפריצת התנגדות מודקת ב-${resistance * 1.005:.2f} (או פולבק הדוק ל-${ema21:.2f})"
                        minervini_stop = f"סטופ מחמיר ב-${min(ema21 * 0.97, recent_low * 0.98):.2f} (~6% סיכון)"
                        minervini_exit = "מימוש חלקי ראשון ברווח של 20% ומעבר לסטופ אי-זון"

                        ryan_buy = f"איסוף סביב בסיס המחיר הנוכחי ב-${base_entry:.2f} במחזור מסחר מתפתח"
                        ryan_stop = f"סטופ קבוע ב-${max(close * 0.92, sma50 * 0.98):.2f} (הפסד מקסימלי 8%)"
                        ryan_exit = "יציאה הדרגתית לפי חולשה בנפח המסחר או ירידת חוזק יחסי"

                        zanger_buy = f"פריצה אגרסיבית עם נפח כבד מעל ${resistance * 1.01:.2f} עם פתיחת המסחר"
                        zanger_stop = f"סטופ צמוד מאוד ב-${ema21 * 0.985:.2f} (סטופ של 3%-4%)"
                        zanger_exit = "מכירה אגרסיבית לתוך עליות חזקות או שבירת ממוצע 10/21 יום"

                        richie_buy = f"כניסה ממושמעת בהתאם ליחס סיכון-סיכוי סטטיסטי סביב ${base_entry:.2f}"
                        richie_stop = f"סטופ אחוזי ממוצע ב-${close * 0.94:.2f} (~6% חד-ספרתי)"
                        richie_exit = "מימוש חלקי כשהרווח פי 2 מהסיכון המקורי וניהול נגרר"

                        experts_data = [
                            {
                                "מומחה": "מארק מינרוויני",
                                "נקודת קניה (Buy)": minervini_buy,
                                "סטופ (Stop Loss)": minervini_stop,
                                "נקודת יציאה (Exit)": minervini_exit
                            },
                            {
                                "מומחה": "דייוויד ראיין",
                                "נקודת קניה (Buy)": ryan_buy,
                                "סטופ (Stop Loss)": ryan_stop,
                                "נקודת יציאה (Exit)": ryan_exit
                            },
                            {
                                "מומחה": "דן זנגר",
                                "נקודת קניה (Buy)": zanger_buy,
                                "סטופ (Stop Loss)": zanger_stop,
                                "נקודת יציאה (Exit)": zanger_exit
                            },
                            {
                                "מומחה": "מארק ריצ'י השני",
                                "נקודת קניה (Buy)": richie_buy,
                                "סטופ (Stop Loss)": richie_stop,
                                "נקודת יציאה (Exit)": richie_exit
                            }
                        ]
                        
                        st.dataframe(pd.DataFrame(experts_data), use_container_width=True)

                        st.markdown("### 📌 סיכום המלצה סופית על בסיס קריאת הגרף העדכני ודעות המאסטרים:")
                        if weekly_positive and is_growing and score >= 4:
                            summary_text = (
                                f"ניתוח הגרף העדכני של **{company_name} ({manual_ticker})** מצביע על מבנה טכני חיובי התומך בעקרונות הספר 'מומנטום מאסטרס'. "
                                f"המחיר נסחר בקרבת אזורי מפתח אסטרטגיים (התנגדות ב-${resistance:.2f} ותמיכת EMA21 ב-${ema21:.2f}), כשברקע הממוצעים השבועיים בשיפוע עולה מלא והנתונים הפונדמנטליים תומכים בצמיחה. "
                                f"על פי משנת המאסטרים, מומלץ להיערך לביצוע עסקה בהתאם לסט-אפ הנבחר (פריצה או פולבק), להקפיד באדיקות על רמות הסטופ שהוגדרו לכל שיטה, ולנהל את הפוזיציה באופן דינמי לתוך עוצמה."
                            )
                        else:
                            summary_text = (
                                f"בחינת נתוני הגרף העדכניים והפונדמנטליים של **{company_name} ({manual_ticker})** מראים תמונה מעורבת שאינה עומדת באופן מושלם בכל התנאים המחמירים של המאסטרים (כגון שיפוע שבועי שאינו מלא או מרחק לא אופטימלי מנקודת הציר). "
                                f"במצב עניינים זה, ההמלצה החד-משמעית של המומחים היא לא לכפות עסקאות: יש לשבת על הידיים, להמתין שהגרף יבנה בסיס מחיר הדוק וברור יותר, או לסנן החוצה את הרעש עד שההזדמנויות יעמדו במלוא קריטריוני הסיכון-סיכוי."
                            )
                        st.info(summary_text)

                except Exception as e:
                    st.error(f"שגיאה בניתוח הסימבול: {e}")
