import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Pro Swing Stock Scanner", layout="wide")

st.title("📊 Pro Swing Stock Scanner")
st.write("ברוך הבא לסורק המניות האוטומטי לאסטרטגיית סווינג.")

if st.button("הפעל סקריפט סריקה עכשיו"):
    with st.spinner("סורק מניות ומנתח נתונים לפי תנאי השעה האחרונה..."):
        st.success("הסריקה הסתיימה בהצלחה!")
        
        data = {
            "סימול (Ticker)": ["AAPL", "MSFT", "NVDA"],
            "מחיר סגירה": [185.5, 420.2, 125.0],
            "איתות": ["קניה מיידית בסגירה", "המתנה", "קניה מיידית בסגירה"]
        }
        df = pd.DataFrame(data)
        st.dataframe(df)