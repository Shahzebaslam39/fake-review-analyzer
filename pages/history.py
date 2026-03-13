# pages/history.py
import streamlit as st, sys, os, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import inject_css, topnav, sidebar_logo, page_header, init, RED, GREEN, AMBER, GRAY

inject_css(); topnav(); sidebar_logo(); init()

page_header("History", "Every review checked this session, with timestamps and results.")

st.markdown('<div class="pw">', unsafe_allow_html=True)

hist = st.session_state.history

if not hist:
    st.markdown("""
<div style="text-align:center;padding:4rem 2rem">
  <div style="font-size:3rem;margin-bottom:1rem">🕘</div>
  <div style="font-size:1.1rem;font-weight:600;color:#0F172A;margin-bottom:.4rem">No history yet</div>
  <div style="font-size:.875rem;color:#64748B">Your checked reviews will appear here.</div>
</div>""", unsafe_allow_html=True)
else:
    ca, cb = st.columns([5, 1])
    with ca:
        csv_out = pd.DataFrame(hist).to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download History as Spreadsheet",
            data=csv_out, file_name="review_check_history.csv", mime="text/csv")
    with cb:
        if st.button("🗑 Clear", help="Remove all history from this session"):
            for k in ["history","n_total","n_fake","n_legit"]:
                st.session_state[k] = [] if k == "history" else 0
            st.rerun()

    # ── Table ──
    st.markdown("""
<div style="background:#fff;border:1px solid #E2E8F0;border-radius:12px;overflow:hidden;margin-top:.8rem">
  <div style="display:grid;grid-template-columns:80px 1fr 100px 90px 80px;gap:.6rem;
    padding:.7rem 1.1rem;background:#F8FAFC;border-bottom:1px solid #E2E8F0;
    font-size:.72rem;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:.06em">
    <span>Time</span><span>Review</span><span>Result</span><span>Tone</span><span>Confidence</span>
  </div>
""", unsafe_allow_html=True)

    for e in reversed(hist[-200:]):
        vc   = GREEN if e["verdict"] == "Legitimate" else RED
        pol  = e.get("polarity", 0)
        sc   = GREEN if pol > .15 else (RED if pol < -.10 else AMBER)
        cf_s = f"{e['conf']}%" if e["conf"] else "—"
        bg   = "#DCFCE7" if e["verdict"] == "Legitimate" else "#FEF2F2"
        bdr  = "#BBF7D0" if e["verdict"] == "Legitimate" else "#FECACA"
        st.markdown(f"""
<div style="display:grid;grid-template-columns:80px 1fr 100px 90px 80px;gap:.6rem;
  align-items:center;padding:.65rem 1.1rem;border-bottom:1px solid #F1F5F9;
  transition:background .15s" onmouseover="this.style.background='#F8FAFC'"
  onmouseout="this.style.background='#fff'">
  <span style="font-size:.75rem;color:#94A3B8">{e['time']}</span>
  <span style="font-size:.84rem;color:#0F172A;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{e['text']}</span>
  <span style="font-size:.78rem;font-weight:600;color:{vc}">{e['verdict']}</span>
  <span style="font-size:.78rem;color:{sc}">{e.get('sentiment','—')}</span>
  <span style="font-size:.78rem;color:#64748B">{cf_s}</span>
</div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div class="foot">
  <div class="foot-brand">🔍 Fake Review Detector</div>
  <div style="font-size:.75rem;color:#64748B;font-weight:600">Made by Roll No: 23CS116</div>
  <div class="foot-copy">History is only saved for this browser session and is not stored anywhere.</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
