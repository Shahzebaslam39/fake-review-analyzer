# pages/single.py
import streamlit as st, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import (inject_css, topnav, sidebar_logo, page_header, init,
                   load_models, classify, sentiment, _signals, risk,
                   badge, sbar, gauge, track,
                   BLUE, RED, GREEN, AMBER, GRAY, SLATE)

inject_css(); topnav(); sidebar_logo(); init()
model, vec = load_models()

page_header("Check a Review", "Paste any product review below. We'll tell you whether it looks real or fake.")

st.markdown('<div class="pw">', unsafe_allow_html=True)

# ── Instructions ─────────────────────────────────────────
st.markdown("""
<div class="info-box">
  <strong>How to use this page:</strong>
  Copy any product review — from Amazon, Google, Trustpilot, or anywhere else — paste it into the box below,
  and click <b>Check This Review</b>. Results appear instantly.
</div>
""", unsafe_allow_html=True)

review = st.text_area(
    "Review Text",
    height=160,
    placeholder="Paste the review here — for example:\n\n\"This product is absolutely amazing!!! Best purchase I ever made. Totally changed my life, highly recommend to everyone!!!\"",
    key="single_rev"
)

go = st.button("🔍 Check This Review", key="go_single")

if go:
    if not review.strip():
        st.warning("Please paste a review into the box above before clicking Check.")
    else:
        with st.spinner("Analyzing review…"):
            time.sleep(.25)
            lbl, cf      = classify(review, model, vec)
            pol, sub, sl = sentiment(review)
            sig          = _signals(review)
            rs           = risk(sig, lbl, cf)

        if lbl:
            track(lbl, review, cf, pol, sl)
            cls   = "ok" if lbl == "True" else "bad"
            cf_row = f'<div class="row-m">We are {cf}% confident in this result.</div>' if cf else ""

            # ── Main verdict ──
            st.markdown("<br>", unsafe_allow_html=True)
            is_fake = lbl != "True"
            verdict_bg  = "#FEE2E2" if is_fake else "#DCFCE7"
            verdict_bdr = "#FECACA" if is_fake else "#BBF7D0"
            verdict_col = RED if is_fake else GREEN
            verdict_ico = "⚠️" if is_fake else "✅"
            verdict_ttl = "This review looks FAKE" if is_fake else "This review looks LEGITIMATE"
            verdict_msg = (
                "Our AI detected patterns commonly found in fake reviews — "
                "such as exaggerated language, unusual writing style, or suspicious emotional cues. "
                "Treat this review with extra caution."
            ) if is_fake else (
                "Our AI did not detect strong signs of deception in this review. "
                "It appears to be written by a genuine customer, based on its language and tone."
            )

            st.markdown(f"""
<div style="background:{verdict_bg};border:1.5px solid {verdict_bdr};border-radius:14px;
  padding:1.6rem 2rem;margin-bottom:1.5rem;display:grid;
  grid-template-columns:auto 1fr auto;gap:1.2rem;align-items:center">
  <div style="font-size:2.5rem">{verdict_ico}</div>
  <div>
    <div style="font-size:1.15rem;font-weight:700;color:{verdict_col};margin-bottom:.3rem">{verdict_ttl}</div>
    <div style="font-size:.875rem;color:#374151;line-height:1.65">{verdict_msg}</div>
  </div>
  <div>{badge(lbl, cf)}</div>
</div>
""", unsafe_allow_html=True)

            if cf:
                st.progress(int(cf))
                st.caption(f"Confidence: {cf}%")

            st.markdown("<br>", unsafe_allow_html=True)
            col_l, col_r = st.columns([1.5, 1])

            with col_l:
                # ── Signals ──
                st.markdown("""
<div class="card">
  <div class="card-hd">
    <div class="card-ic">📋</div>
    <div>
      <div class="card-ht">What We Found</div>
      <div class="card-hs">Patterns our AI looks for to spot fake reviews</div>
    </div>
  </div>
""", unsafe_allow_html=True)

                pol_col = GREEN if pol > .15 else (RED if pol < -.10 else AMBER)
                pol_pct = (pol + 1) / 2 * 100
                tone_lbl = "Positive tone" if pol > .15 else ("Negative tone" if pol < -.10 else "Neutral tone")

                bars = ""
                bars += sbar("Overall Tone",          pol_pct,               100,  pol_col, tone_lbl)
                bars += sbar("How Subjective It Sounds", sub * 100,          100,  BLUE,   f"{int(sub*100)}% opinionated")
                bars += sbar("Emotional Word Usage",   sig["emo_%"],          30,   AMBER,  f"{sig['emo_%']}%")
                bars += sbar("Use of 'I / Me / My'",  sig["fp_%"],           25,   BLUE,   f"{sig['fp_%']}%")
                bars += sbar("Exclamation Marks",      min(sig["excl_mk"],10),10,   RED,    str(sig["excl_mk"]))
                bars += sbar("ALL CAPS Usage",         sig["caps_%"],         18,   RED,    f"{sig['caps_%']}%")
                bars += sbar("Word Variety",           sig["ttr"] * 100,      100,  GREEN,  f"{int(sig['ttr']*100)}% varied")
                bars += sbar("Repeated Words",         100 - sig["ttr"]*100,  100,  AMBER,  "Low" if sig["ttr"] > .6 else "High")
                st.markdown(bars + "</div>", unsafe_allow_html=True)

                st.markdown("""
<div class="tip-box">
  <strong>What do these signals mean?</strong><br>
  Fake reviews often use <b>too many emotional words</b> ("amazing", "incredible", "horrible"),
  <b>excessive exclamation marks</b>, and <b>repeat the same words</b> more than a real customer would.
  They also tend to use <b>"I", "me", "my"</b> very frequently to fake personal experience.
</div>
""", unsafe_allow_html=True)

            with col_r:
                # ── Risk gauge ──
                st.markdown("""
<div class="card">
  <div class="card-hd">
    <div class="card-ic">🎯</div>
    <div>
      <div class="card-ht">Suspicion Level</div>
      <div class="card-hs">Combined risk rating from AI + pattern analysis</div>
    </div>
  </div>
""", unsafe_allow_html=True)
                st.plotly_chart(gauge(rs), use_container_width=True,
                                config={"displayModeBar": False}, theme=None)

                # ── Quick stats ──
                mini = [
                    ("Word Count",    sig["word_count"],          BLUE),
                    ("! Marks",       sig["excl_mk"],             RED),
                    ("Tone",          sl,                         pol_col),
                    ("Confidence",    f"{cf}%" if cf else "—",    GREEN),
                ]
                st.markdown('<div style="display:grid;grid-template-columns:1fr 1fr;gap:.6rem;margin-top:.5rem">', unsafe_allow_html=True)
                for lbl_m, val_m, col_m in mini:
                    st.markdown(f"""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:.7rem .9rem">
  <div style="font-size:.7rem;font-weight:500;color:#64748B;margin-bottom:.2rem">{lbl_m}</div>
  <div style="font-size:1.1rem;font-weight:700;color:{col_m}">{val_m}</div>
</div>""", unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)

            # ── Reviewed text ──
            st.markdown(f"""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;
  padding:1.1rem 1.3rem;margin-top:1rem">
  <div style="font-size:.72rem;font-weight:600;color:#64748B;
    text-transform:uppercase;letter-spacing:.06em;margin-bottom:.4rem">Review Analyzed</div>
  <div style="font-size:.875rem;color:#374151;line-height:1.7">{review}</div>
</div>
""", unsafe_allow_html=True)
            

st.markdown("""
<div class="foot">
  <div class="foot-brand">🕵️ Fake Review Detector</div>
  <div style="font-size:.75rem;color:#64748B;font-weight:600">Made by Roll No: 23CS116</div>
  <div class="foot-copy">Results are AI predictions — not guarantees. Use as a guide alongside your own judgment.</div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
