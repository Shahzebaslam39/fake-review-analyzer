# pages/crawler.py
import streamlit as st, sys, os, subprocess, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import (inject_css, topnav, sidebar_logo, page_header, init,
                   load_models, classify, sentiment, badge, donut, track,
                   RED, GREEN, AMBER, BLUE, GRAY)

inject_css(); topnav(); sidebar_logo(); init()
model, vec = load_models()

page_header("Scan a Website's Reviews",
            "Give us a Trustpilot product URL and we'll automatically collect and check all its reviews.")

st.markdown('<div class="pw">', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
  <strong>How to use this page:</strong><br>
  1. Go to <b>Trustpilot.com</b> and find the product or company you want to check.<br>
  2. Copy the URL from your browser address bar.<br>
  3. Paste it below and click <b>Start Scan</b>. We'll collect and check all the reviews for you.
</div>
""", unsafe_allow_html=True)

url_in = st.text_input("Product or Company URL",
    placeholder="https://www.trustpilot.com/review/example.com")
go = st.button("🌐 Start Scan")

if go:
    if not url_in.strip():
        st.warning("Please enter a URL before scanning.")
    else:
        with st.spinner("Collecting reviews from the website — this may take a moment…"):
            subprocess.call(f"python review_crawler.py {url_in}", shell=True)
        try:
            df_u = pd.read_csv("reviews1.csv")
            revs = df_u["body"].dropna().astype(str).tolist()
            if not revs:
                st.error("We couldn't collect any reviews from that URL. Make sure it's a valid Trustpilot product page.")
            else:
                fk = lg = 0; rows = []
                pb = st.progress(0)
                for i, rv in enumerate(revs):
                    lbl, cf      = classify(rv, model, vec)
                    pol, sub, sl = sentiment(rv)
                    is_f = lbl != "True"
                    if is_f: fk += 1
                    else:    lg += 1
                    rows.append((rv, lbl, cf, is_f, pol, sl))
                    track(lbl, rv, cf, pol, sl)
                    pb.progress((i+1)/len(revs))

                total = len(revs)
                fkp   = round(fk/total*100)
                verdict_col = RED if fkp > 50 else (AMBER if fkp > 20 else GREEN)
                verdict_msg = (f"⚠️ {fkp}% of reviews look suspicious" if fkp > 30
                               else f"✅ Most reviews appear genuine ({fkp}% flagged)")

                st.markdown(f"""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;
  padding:1.5rem 2rem;margin-bottom:1.2rem">
  <div style="font-size:1.1rem;font-weight:700;color:{verdict_col};margin-bottom:.4rem">
    {verdict_msg}
  </div>
  <div style="font-size:.85rem;color:#64748B">
    We checked {total} reviews from this page.
  </div>
</div>
""", unsafe_allow_html=True)
                st.progress(fkp, text=f"Fake rate: {fkp}%")

                c1, _ = st.columns([1, 2])
                with c1:
                    st.caption("Fake vs Legitimate")
                    st.plotly_chart(donut(fk, lg), use_container_width=True,
                                    config={"displayModeBar": False}, theme=None)

                st.markdown('<div class="rows">', unsafe_allow_html=True)
                for i, (rv, lbl, cf, is_f, pol, sl) in enumerate(rows):
                    cls  = "ok" if not is_f else "bad"
                    cf_  = f'<div class="row-m">Confidence: {cf}%  ·  Tone: {sl}</div>' if cf else ""
                    st.markdown(f"""
<div class="row {cls}">
  <div class="row-n">#{i+1:02d}</div>
  <div><div class="row-t">{rv}</div>{cf_}</div>
  <div>{badge(lbl, cf)}</div>
</div>""", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.rerun()
        except FileNotFoundError:
            st.error("Something went wrong collecting the reviews. Please check the URL and try again.")

st.markdown("""
<div class="foot">
  <div class="foot-brand">🔍 Fake Review Detector</div>
  <div style="font-size:.75rem;color:#64748B;font-weight:600">Made by Roll No: 23CS116</div>
  <div class="foot-copy">Results are AI predictions — use as a guide alongside your own judgment.</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
