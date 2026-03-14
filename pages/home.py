# pages/home.py
import streamlit as st, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import inject_css, topnav, sidebar_logo, page_header, init

inject_css(); topnav(); sidebar_logo(); init()

n  = st.session_state.n_total
nf = st.session_state.n_fake
nl = st.session_state.n_legit
fp = f"{round(nf/n*100)}%" if n else "—"

page_header("Dashboard", "Welcome to Fake Review Detector — your AI-powered tool to spot fake product reviews instantly.")

st.markdown('<div class="pw">', unsafe_allow_html=True)

# ── Stats strip ───────────────────────────────────────────
st.markdown(f"""
<div class="stats">
  <div class="stat">
    <div class="stat-lbl">Total Checked</div>
    <div class="stat-val sv-blue">{n}</div>
    <div class="stat-sub">reviews this session</div>
  </div>
  <div class="stat">
    <div class="stat-lbl">Fake Reviews Found</div>
    <div class="stat-val sv-red">{nf}</div>
    <div class="stat-sub">flagged as suspicious</div>
  </div>
  <div class="stat">
    <div class="stat-lbl">Legitimate Reviews</div>
    <div class="stat-val sv-green">{nl}</div>
    <div class="stat-sub">appear to be genuine</div>
  </div>
  <div class="stat">
    <div class="stat-lbl">Fake Rate</div>
    <div class="stat-val sv-amber">{fp}</div>
    <div class="stat-sub">of all reviews checked</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1D4ED8 0%,#1E3A8A 100%);
  border-radius:16px;padding:3rem 3.5rem;margin-bottom:1.8rem;
  display:grid;grid-template-columns:1fr auto;gap:2rem;align-items:center">

  <div>
    <div style="font-size:.78rem;font-weight:600;color:rgba(255,255,255,.6);
      text-transform:uppercase;letter-spacing:.08em;margin-bottom:.7rem">
      AI-Powered · Real-Time · Instant Results
    </div>
    <h1 style="font-family:'Inter',sans-serif;font-size:2.4rem;font-weight:800;
      color:#fff;line-height:1.15;letter-spacing:-.03em;margin:0 0 .9rem">
      Is This Review Real<br>or Fake?
    </h1>
    <p style="font-size:1rem;color:rgba(255,255,255,.75);line-height:1.75;max-width:480px;margin:0">
      Our AI checks any product review in under a second and tells you whether it looks
      genuine or suspicious — so you can shop smarter and trust the right reviews.
    </p>
  </div>

  <div style="text-align:center;padding:1.5rem 2rem;
    background:rgba(255,255,255,.08);border-radius:12px;
    border:1px solid rgba(255,255,255,.15);min-width:180px">
    <div style="font-size:3.5rem;margin-bottom:.5rem">🕵️</div>
    <div style="font-size:.85rem;color:rgba(255,255,255,.7);font-weight:500">
      AI Review Checker
    </div>
    <div style="font-size:.72rem;color:rgba(255,255,255,.4);margin-top:.25rem">
      Powered by Machine Learning
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── What you can do ───────────────────────────────────────
st.markdown("""
<div style="font-size:.75rem;font-weight:600;color:#64748B;
  text-transform:uppercase;letter-spacing:.08em;margin-bottom:1rem">
  WHAT YOU CAN DO
</div>
""", unsafe_allow_html=True)

cols = st.columns(3)
features = [
    ("🕵️", "Check a Single Review",
     "Paste any review text and get an instant result. See whether it's likely fake or real, how confident we are, and what signals we found.",
     "#EFF6FF", "#1D4ED8", "#BFDBFE"),
    ("📂", "Upload a File of Reviews",
     "Have a list of reviews? Upload a CSV or text file and we'll check them all at once. Download a full results report when done.",
     "#F0FDF4", "#16A34A", "#BBF7D0"),
    ("🌐", "Scan a Website's Reviews",
     "Paste a product URL and we'll automatically collect and check all its reviews — giving you a summary of how many look suspicious.",
     "#FFF7ED", "#D97706", "#FDE68A"),
]
for i, (ico, title, desc, bg, col, bdr) in enumerate(features):
    with cols[i]:
        st.markdown(f"""
<div style="background:{bg};border:1px solid {bdr};border-radius:12px;padding:1.4rem 1.5rem;height:100%">
  <div style="font-size:1.6rem;margin-bottom:.8rem">{ico}</div>
  <div style="font-size:.95rem;font-weight:600;color:#0F172A;margin-bottom:.5rem">{title}</div>
  <div style="font-size:.84rem;color:#64748B;line-height:1.7">{desc}</div>
</div>""", unsafe_allow_html=True)

# ── How it works ──────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:2rem 2.2rem">
  <div style="font-size:1.05rem;font-weight:700;color:#0F172A;margin-bottom:1.2rem">How It Works</div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1.2rem">
""", unsafe_allow_html=True)

steps = [
    ("1", "#EFF6FF", "#1D4ED8", "You Submit a Review", "Paste it, upload a file, or give us a product URL."),
    ("2", "#FFF7ED", "#D97706", "Our AI Reads It",     "We analyze the language, tone, and writing patterns."),
    ("3", "#F0FDF4", "#16A34A", "We Check the Signals","We look at 8 patterns that research shows separate real from fake reviews."),
    ("4", "#F5F3FF", "#7C3AED", "You Get a Result",    "Fake or Legitimate — with a confidence score and explanation."),
]
for num, bg, col, title, desc in steps:
    st.markdown(f"""
<div style="text-align:center">
  <div style="width:40px;height:40px;border-radius:10px;background:{bg};
    border:1.5px solid;border-color:{col}40;color:{col};
    font-size:1.1rem;font-weight:800;display:flex;align-items:center;
    justify-content:center;margin:0 auto .7rem">{num}</div>
  <div style="font-size:.85rem;font-weight:600;color:#0F172A;margin-bottom:.3rem">{title}</div>
  <div style="font-size:.78rem;color:#64748B;line-height:1.6">{desc}</div>
</div>""", unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

# ── Tip ───────────────────────────────────────────────────
st.markdown("""
<div class="tip-box" style="margin-top:1.2rem">
  <strong>💡 Tip:</strong> Use the <b>Upload &amp; Scan File</b> page if you want to check many reviews at once —
  you can download a full spreadsheet of results including which ones we think are fake.
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────
st.markdown("""
<div class="foot">
  <div class="foot-brand">🕵️ Fake Review Detector</div>
  <div style="font-size:.75rem;color:#64748B;font-weight:600">Made by Roll No: 23CS116</div>
  <div class="foot-copy">AI-powered · For informational use only · Results are model predictions, not guarantees</div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
