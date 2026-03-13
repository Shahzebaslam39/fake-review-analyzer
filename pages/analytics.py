# pages/analytics.py
import streamlit as st, sys, os, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import (inject_css, topnav, sidebar_logo, page_header, init,
                   donut, conf_hist, scatter, bar_chart, BLUE, RED, GREEN, AMBER, GRAY)

inject_css(); topnav(); sidebar_logo(); init()

page_header("Analytics", "A summary of all reviews checked this session.")

st.markdown('<div class="pw">', unsafe_allow_html=True)

hist = st.session_state.history

if not hist:
    st.markdown("""
<div style="text-align:center;padding:4rem 2rem">
  <div style="font-size:3rem;margin-bottom:1rem">📊</div>
  <div style="font-size:1.1rem;font-weight:600;color:#0F172A;margin-bottom:.4rem">No data yet</div>
  <div style="font-size:.875rem;color:#64748B">
    Start checking reviews — your results will appear here automatically.
  </div>
</div>""", unsafe_allow_html=True)
else:
    df    = pd.DataFrame(hist)
    total = len(df)
    fakes = len(df[df["verdict"] == "Fake"])
    legit = total - fakes
    avg_c = round(df["conf"].dropna().mean(), 1)

    st.markdown(f"""
<div class="stats">
  <div class="stat"><div class="stat-lbl">Total Checked</div>
    <div class="stat-val sv-blue">{total}</div>
    <div class="stat-sub">reviews this session</div></div>
  <div class="stat"><div class="stat-lbl">Fake Found</div>
    <div class="stat-val sv-red">{fakes}</div>
    <div class="stat-sub">{round(fakes/total*100)}% of total</div></div>
  <div class="stat"><div class="stat-lbl">Legitimate</div>
    <div class="stat-val sv-green">{legit}</div>
    <div class="stat-sub">{round(legit/total*100)}% of total</div></div>
  <div class="stat"><div class="stat-lbl">Avg. Confidence</div>
    <div class="stat-val sv-blue">{avg_c}%</div>
    <div class="stat-sub">how sure our AI was</div></div>
</div>
""", unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.caption("Fake vs Legitimate — all reviews checked")
        st.plotly_chart(donut(fakes, legit), use_container_width=True,
                        config={"displayModeBar": False}, theme=None)
    with r2:
        sc    = df["sentiment"].value_counts()
        labs  = list(sc.index); vals = list(sc.values)
        cols  = {"Positive": GREEN, "Negative": RED, "Neutral": AMBER}
        colors= [cols.get(l, BLUE) for l in labs]
        st.caption("Tone distribution — how reviews sounded overall")
        st.plotly_chart(bar_chart(labs, vals, colors), use_container_width=True,
                        config={"displayModeBar": False}, theme=None)

    confs = df["conf"].dropna().tolist()
    if confs:
        r3, r4 = st.columns(2)
        with r3:
            st.caption("Confidence scores — how certain our AI was per review")
            st.plotly_chart(conf_hist(confs), use_container_width=True,
                            config={"displayModeBar": False}, theme=None)
        with r4:
            if "polarity" in df.columns:
                df["review"]  = df["text"]
                df["subjectivity"] = df.get("subjectivity", 0.5)
                df["preview"] = df["text"].str[:40]
                st.caption("Tone vs subjectivity — where reviews cluster")
                st.plotly_chart(scatter(df), use_container_width=True,
                                config={"displayModeBar": False}, theme=None)

st.markdown("""
<div class="foot">
  <div class="foot-brand">🔍 Fake Review Detector</div>
  <div style="font-size:.75rem;color:#64748B;font-weight:600">Made by Roll No: 23CS116</div>
  <div class="foot-copy">Session data is not saved after you close the browser.</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
