# app.py
import streamlit as st

st.set_page_config(
    page_title="Fake Review Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


pg = st.navigation({
    "Main": [
        st.Page("pages/home.py",    title="Dashboard",          icon="🏠"),
        st.Page("pages/single.py",  title="Check a Review",     icon="🔍"),
        st.Page("pages/batch.py",   title="Upload & Scan File",  icon="📂"),
        st.Page("pages/crawler.py", title="Scan a Website",     icon="🌐"),
    ],
    "Reports": [
        st.Page("pages/analytics.py", title="Analytics",        icon="📊"),
        st.Page("pages/history.py",   title="History",          icon="🕘"),
    ],
    "Help": [
        st.Page("pages/guide.py",  title="How to Use",          icon="❓"),
    ],
})
pg.run()
