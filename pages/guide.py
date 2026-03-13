# pages/guide.py
import streamlit as st, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import inject_css, topnav, sidebar_logo, page_header, init, BLUE, RED, GREEN, AMBER

inject_css(); topnav(); sidebar_logo(); init()

page_header("How to Use", "Everything you need to know to get the most out of Fake Review Detector.")

st.markdown('<div class="pw">', unsafe_allow_html=True)

# ── Quick start ───────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#1D4ED8,#1E3A8A);border-radius:14px;
  padding:2rem 2.2rem;margin-bottom:1.8rem">
  <div style="font-size:1.1rem;font-weight:700;color:#fff;margin-bottom:.6rem">Quick Start</div>
  <div style="font-size:.9rem;color:rgba(255,255,255,.8);line-height:1.75">
    The fastest way to start: click <b style="color:#fff">Check a Review</b> in the left menu,
    paste any review you found online, and click <b style="color:#fff">Check This Review</b>.
    You'll get your result in under a second.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Three ways ────────────────────────────────────────────
st.markdown("""
<div style="font-size:.75rem;font-weight:600;color:#64748B;
  text-transform:uppercase;letter-spacing:.08em;margin-bottom:1rem">
  3 WAYS TO USE THIS TOOL
</div>
""", unsafe_allow_html=True)

ways = [
    ("🔍", "Check a Single Review", BLUE, "#EFF6FF", "#BFDBFE",
     [
         ("Go to <b>Check a Review</b> in the left menu.", ""),
         ("Copy any review from Amazon, Google, Trustpilot, or anywhere.", ""),
         ("Paste it into the text box.", ""),
         ("Click <b>Check This Review</b>.", ""),
         ("Read your result — Fake or Legitimate — with a confidence score.", ""),
     ]),
    ("📂", "Check Many Reviews at Once", GREEN, "#F0FDF4", "#BBF7D0",
     [
         ("Go to <b>Upload &amp; Scan File</b> in the left menu.", ""),
         ("Prepare a CSV file (spreadsheet) with one column of reviews, OR a plain text file with one review per line.", ""),
         ("Click <b>Choose your file</b> and select your file.", ""),
         ("Choose how many reviews to check and click <b>Run Scan</b>.", ""),
         ("When done, download your results as a spreadsheet.", ""),
     ]),
    ("🌐", "Check a Product's Reviews from a Website", AMBER, "#FFFBEB", "#FDE68A",
     [
         ("Go to <b>Scan a Website</b> in the left menu.", ""),
         ("Visit <b>Trustpilot.com</b> and find a product or company.", ""),
         ("Copy the URL from your browser's address bar.", ""),
         ("Paste the URL into the box and click <b>Start Scan</b>.", ""),
         ("We'll collect all the reviews automatically and show you which look suspicious.", ""),
     ]),
]

for ico, title, col, bg, bdr, steps in ways:
    st.markdown(f"""
<div style="background:{bg};border:1px solid {bdr};border-radius:12px;
  padding:1.5rem 1.8rem;margin-bottom:1rem">
  <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:1rem">
    <div style="font-size:1.4rem">{ico}</div>
    <div style="font-size:1rem;font-weight:700;color:#0F172A">{title}</div>
  </div>
  <ol style="margin:0;padding-left:1.2rem;display:flex;flex-direction:column;gap:.5rem">
    {''.join(f'<li style="font-size:.875rem;color:#374151;line-height:1.65">{s}</li>' for s,_ in steps)}
  </ol>
</div>""", unsafe_allow_html=True)

# ── Understanding results ─────────────────────────────────
st.markdown("""
<div style="font-size:.75rem;font-weight:600;color:#64748B;
  text-transform:uppercase;letter-spacing:.08em;margin:1.5rem 0 1rem">
  UNDERSTANDING YOUR RESULTS
</div>
""", unsafe_allow_html=True)

results_info = [
    ("✅ Legitimate", GREEN, "#DCFCE7", "#BBF7D0",
     "This review did not show strong signs of being fake. It appears to be written by a real customer based on its language, tone, and writing patterns."),
    ("⚠️ Fake", RED, "#FEE2E2", "#FECACA",
     "This review showed patterns our AI associates with fake reviews — such as exaggerated language, too many exclamation marks, repetitive wording, or unusual writing style."),
    ("🎯 Confidence Score", BLUE, "#EFF6FF", "#BFDBFE",
     "This shows how certain our AI is about its verdict — from 50% (uncertain) to 100% (very confident). Higher is more reliable."),
    ("📊 Suspicion Level", AMBER, "#FFFBEB", "#FDE68A",
     "A 0–100 risk score combining the AI verdict with 8 language patterns. Low = likely genuine. Medium = questionable. High = strong signs of being fake."),
]

cols = st.columns(2)
for i, (title, col, bg, bdr, desc) in enumerate(results_info):
    with cols[i % 2]:
        st.markdown(f"""
<div style="background:{bg};border:1px solid {bdr};border-radius:10px;
  padding:1.1rem 1.3rem;margin-bottom:.8rem">
  <div style="font-size:.9rem;font-weight:700;color:{col};margin-bottom:.4rem">{title}</div>
  <div style="font-size:.83rem;color:#374151;line-height:1.65">{desc}</div>
</div>""", unsafe_allow_html=True)

# ── What signals we look for ──────────────────────────────
st.markdown("""
<div style="font-size:.75rem;font-weight:600;color:#64748B;
  text-transform:uppercase;letter-spacing:.08em;margin:1.5rem 0 1rem">
  WHAT OUR AI LOOKS FOR
</div>
<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;
  padding:1.5rem 1.8rem;margin-bottom:1rem">
  <p style="font-size:.875rem;color:#374151;margin-bottom:1rem;line-height:1.75">
    Our AI checks 8 patterns that research has shown are more common in fake reviews than real ones:
  </p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:.7rem">
""", unsafe_allow_html=True)

signals = [
    ("💬", "Too Many Emotional Words", "Fake reviews often overuse words like \"amazing\", \"incredible\", \"perfect\", \"horrible\" to manipulate your emotions."),
    ("!", "Excessive Exclamation Marks", "Real customers use occasional exclamation marks. Fake reviews often use many in a row to create fake excitement."),
    ("🔤", "Lots of ALL CAPS Words", "Overusing capital letters is a sign of urgency injection — a technique used to make fake reviews feel more impactful."),
    ("👤", "Heavy Use of I / Me / My", "Fake reviewers overuse first-person words to fake personal experience. Real customers tend to focus on the product."),
    ("📝", "Repetitive Wording", "Fake reviews often repeat the same words or phrases, because they're written quickly to fill space rather than from real experience."),
    ("🎨", "Word Variety", "Genuine reviews use a wide variety of words naturally. Fake reviews often have low word variety because they're formulaic."),
    ("😊", "Tone Analysis", "We measure how positive, negative, or neutral the review sounds — and whether that matches what a real customer experience would look like."),
    ("⚖️", "How Opinionated It Sounds", "We measure subjectivity — very high subjectivity combined with extreme positivity or negativity can signal a fake review."),
]

for ico, title, desc in signals:
    st.markdown(f"""
<div style="background:#fff;border:1px solid #E2E8F0;border-radius:8px;padding:.85rem 1rem">
  <div style="font-size:.85rem;font-weight:600;color:#0F172A;margin-bottom:.25rem">{ico} {title}</div>
  <div style="font-size:.78rem;color:#64748B;line-height:1.6">{desc}</div>
</div>""", unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

# ── Important note ────────────────────────────────────────
st.markdown("""
<div class="tip-box" style="margin-top:.5rem">
  <strong>⚠️ Important:</strong> Fake Review Detector is an AI tool — not a guarantee.
  A "Fake" result means the review <em>shows patterns</em> associated with fake reviews,
  but it could still be real. A "Legitimate" result means we didn't detect strong fake signals,
  but the review could still be inauthentic. Always use your own judgment alongside our results.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="foot">
  <div class="foot-brand">🔍 Fake Review Detector</div>
  <div style="font-size:.75rem;color:#64748B;font-weight:600">Made by Roll No: 23CS116</div>
  <div class="foot-copy">AI-powered · For informational use only · Results are predictions, not guarantees</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
