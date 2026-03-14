# pages/batch.py
import streamlit as st, sys, os, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import (inject_css, topnav, sidebar_logo, page_header, init,
                   load_models, classify, sentiment, _signals, risk,
                   badge, donut, conf_hist, scatter, make_wc, track,
                   BLUE, RED, GREEN, AMBER, GRAY)

inject_css(); topnav(); sidebar_logo(); init()
model, vec = load_models()

page_header("Upload & Scan File",
            "Upload a spreadsheet or text file of reviews — we'll check every single one.")

st.markdown('<div class="pw">', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
  <strong>How to use this page:</strong><br>
  1. Upload a <b>.CSV file</b> (with a column of reviews) or a <b>.TXT file</b> (one review per line).<br>
  2. Choose how many reviews to check and what to show.<br>
  3. Click <b>Run Scan</b> — results appear with charts and a download link.
</div>
""", unsafe_allow_html=True)

ca, cb, cc = st.columns([2.5, 1, 1])
with ca:
    uploaded = st.file_uploader("Choose your file", type=["csv","txt"],
                                 help="CSV: must have a column of review text. TXT: one review per line.")
with cb:
    lim  = st.selectbox("Reviews to check", [50, 100, 250, 500, 1000, "All"], index=1)
with cc:
    filt = st.selectbox("Show results", ["All", "Fake only", "Legit only"])

run = st.button("🔍 Run Scan", disabled=uploaded is None)

if run and uploaded:
    batch = []
    if uploaded.name.lower().endswith(".txt"):
        raw   = uploaded.read().decode("utf-8", errors="ignore")
        batch = [l.strip() for l in raw.splitlines() if l.strip()]
    else:
        try:    df_raw = pd.read_csv(uploaded, encoding="utf-8",   errors="replace")
        except: df_raw = pd.read_csv(uploaded, encoding="latin-1")
        col = None
        for c in ["review_text","body","review","text","comment","content","description","Review"]:
            if c in df_raw.columns: col = c; break
        if col is None:
            sc = df_raw.select_dtypes(include="object").columns.tolist()
            if sc: col = max(sc, key=lambda c: df_raw[c].dropna().astype(str).str.len().mean())
        if col:
            batch = df_raw[col].dropna().astype(str).tolist()
        else:
            st.error("We couldn't find a column of review text in your file. Rename the review column to **review_text** and try again.")

    if batch:
        if lim != "All": batch = batch[:int(lim)]
        total = len(batch)

        st.markdown(f"""
<div style="display:flex;align-items:center;gap:.75rem;padding:.8rem 1rem;
  background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;margin:.8rem 0">
  <div style="width:8px;height:8px;border-radius:50%;background:{BLUE};
    animation:pulse 1.3s infinite"></div>
  <div style="font-size:.875rem;font-weight:600;color:{BLUE}">
    Scanning {total} reviews — please wait…
  </div>
</div>
<style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}</style>
""", unsafe_allow_html=True)

        pb  = st.progress(0)
        ctr = st.empty()
        results = []; fk = lg = 0
        ft = []; lt = []

        for i, rv in enumerate(batch):
            lbl, cf      = classify(str(rv), model, vec)
            pol, sub, sl = sentiment(str(rv))
            sig          = _signals(str(rv))
            rs           = risk(sig, lbl, cf)
            is_f         = lbl != "True"
            results.append({"#": i+1, "review": rv,
                "verdict": "Fake" if is_f else "Legitimate",
                "confidence_%": cf, "polarity": pol,
                "subjectivity": sub, "sentiment": sl,
                "risk_score": rs, "preview": rv[:38]+"…"})
            if is_f: fk += 1; ft.append(rv)
            else:    lg += 1; lt.append(rv)
            pb.progress((i+1)/total)
            if i % 8 == 0: ctr.caption(f"Checked {i+1} of {total}  ·  {fk} fake  ·  {lg} legitimate")
            if i < 150: track(lbl, rv, cf, pol, sl)
        ctr.empty()

        fkp = round(fk/total*100); lgp = 100 - fkp
        df_res = pd.DataFrame(results)

        # ── Summary banner ──
        bg   = "#FEE2E2" if fkp > 50 else ("#FFF7ED" if fkp > 20 else "#DCFCE7")
        col  = RED if fkp > 50 else (AMBER if fkp > 20 else GREEN)
        msg  = (f"⚠️ <b>{fkp}% of reviews appear fake</b> — this product has a high proportion of suspicious reviews."
                if fkp > 30 else
                f"✅ <b>Most reviews look legitimate</b> — only {fkp}% showed suspicious patterns.")

        st.markdown(f"""
<div style="background:{bg};border:1px solid;border-color:{col}40;border-radius:12px;
  padding:1.2rem 1.6rem;margin-bottom:1.2rem">
  <div style="font-size:1rem;color:{col};">{msg}</div>
  <div style="font-size:.8rem;color:#64748B;margin-top:.3rem">
    Scanned {total} reviews  ·  {fk} fake  ·  {lg} legitimate
  </div>
</div>
""", unsafe_allow_html=True)
        st.progress(fkp, text=f"Fake rate: {fkp}%")

        # ── Charts ──
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.caption("Fake vs Legitimate breakdown")
            st.plotly_chart(donut(fk, lg), use_container_width=True,
                            config={"displayModeBar": False}, theme=None)
        with c2:
            confs = [r["confidence_%"] for r in results if r["confidence_%"]]
            if confs:
                st.caption("How confident we were across all results")
                st.plotly_chart(conf_hist(confs), use_container_width=True,
                                config={"displayModeBar": False}, theme=None)
        with c3:
            st.caption("Tone analysis — how positive/subjective each review was")
            st.plotly_chart(scatter(df_res), use_container_width=True,
                            config={"displayModeBar": False}, theme=None)

        # ── Word clouds ──
        st.markdown("<br>", unsafe_allow_html=True)
        wc1, wc2 = st.columns(2)
        with wc1:
            st.caption("⚠ Most common words in FAKE reviews")
            if ft:
                img = make_wc(ft, fake=True)
                if img: st.markdown(
                    f'<img src="data:image/png;base64,{img}" style="width:100%;border-radius:10px;'
                    f'border:1px solid #FECACA">', unsafe_allow_html=True)
            else: st.info("No fake reviews to show.")
        with wc2:
            st.caption("✓ Most common words in LEGITIMATE reviews")
            if lt:
                img = make_wc(lt, fake=False)
                if img: st.markdown(
                    f'<img src="data:image/png;base64,{img}" style="width:100%;border-radius:10px;'
                    f'border:1px solid #BFDBFE">', unsafe_allow_html=True)
            else: st.info("No legitimate reviews to show.")

        # ── Download ──
        st.markdown("<br>", unsafe_allow_html=True)
        csv_out = df_res.drop(columns=["preview"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Full Results Spreadsheet",
            data=csv_out, file_name="fake_review_scan_results.csv", mime="text/csv",
            help="Download a spreadsheet with every review and whether it was flagged as fake."
        )

        # ── Filtered rows ──
        st.markdown("<br>", unsafe_allow_html=True)
        display = results
        if filt == "Fake only":  display = [r for r in results if r["verdict"] == "Fake"]
        elif filt == "Legit only": display = [r for r in results if r["verdict"] == "Legitimate"]
        shown = min(len(display), 200)
        if shown < len(display):
            st.caption(f"Showing {shown} of {len(display)} results. Download the spreadsheet above for the full list.")

        st.markdown('<div class="rows">', unsafe_allow_html=True)
        for r in display[:shown]:
            lbl_r = "True" if r["verdict"] == "Legitimate" else "False"
            cls   = "ok" if lbl_r == "True" else "bad"
            prev  = r["review"][:260] + ("…" if len(r["review"]) > 260 else "")
            cf_   = f'<div class="row-m">Confidence: {r["confidence_%"]}%  ·  Tone: {r["sentiment"]}  ·  Risk score: {r["risk_score"]}/100</div>' if r["confidence_%"] else ""
            st.markdown(f"""
<div class="row {cls}">
  <div class="row-n">#{r['#']:03d}</div>
  <div><div class="row-t">{prev}</div>{cf_}</div>
  <div>{badge(lbl_r, r['confidence_%'])}</div>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
       

st.markdown("""
<div class="foot">
  <div class="foot-brand">🕵️ Fake Review Detector</div>
  <div style="font-size:.75rem;color:#64748B;font-weight:600">Made by Roll No: 23CS116</div>
  <div class="foot-copy">Results are AI predictions — use as a guide alongside your own judgment.</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
