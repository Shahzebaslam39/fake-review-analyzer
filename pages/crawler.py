# pages/crawler.py
import streamlit as st, sys, os, subprocess, json, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import (inject_css, topnav, sidebar_logo, page_header, footer, init,
                   load_models, classify, sentiment, badge, donut, track,
                   RED, GREEN, AMBER, BLUE, GRAY)

inject_css(); topnav(); sidebar_logo(); init()
model, vec = load_models()

page_header("Scan Website Reviews",
            "Check reviews from any website — auto-collect from Trustpilot, or paste / upload reviews manually.")
st.markdown('<div class="pw">', unsafe_allow_html=True)

def run_scan(revs):
    revs = [str(r).strip() for r in revs if str(r).strip() and len(str(r).strip()) > 5]
    if not revs:
        st.error("No review text found to scan.")
        return
    fk = lg = 0
    rows = []
    pb   = st.progress(0)
    ctr  = st.empty()
    for i, rv in enumerate(revs):
        lbl, cf      = classify(rv, model, vec)
        pol, sub, sl = sentiment(rv)
        is_f         = (lbl != "True") if lbl else True
        if is_f: fk += 1
        else:    lg += 1
        rows.append((rv, lbl if lbl else "False", cf, is_f, pol, sl))
        track(lbl if lbl else "False", rv, cf, pol, sl)
        pb.progress((i + 1) / len(revs))
        if i % 10 == 0:
            ctr.caption(f"Checked {i+1} of {len(revs)}  ·  {fk} fake  ·  {lg} legitimate")
    ctr.empty(); pb.empty()

    total = len(revs)
    fkp   = round(fk / total * 100)
    vc    = RED if fkp > 50 else (AMBER if fkp > 20 else GREEN)
    msg   = (f"Warning: {fkp}% of reviews look suspicious"
             if fkp > 30 else f"Most reviews appear genuine ({fkp}% flagged)")

    st.markdown(f"""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;
  padding:1.5rem 2rem;margin-bottom:1rem">
  <div style="font-size:1.1rem;font-weight:700;color:{vc};margin-bottom:.3rem">{msg}</div>
  <div style="font-size:.85rem;color:#64748B">Checked {total} reviews</div>
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
        cf_  = f'<div class="row-m">Confidence: {cf}%  · Tone: {sl}</div>' if cf else ""
        safe = rv.encode("ascii", "ignore").decode("ascii")[:260]
        st.markdown(f"""
<div class="row {cls}">
  <div class="row-n">#{i+1:02d}</div>
  <div><div class="row-t">{safe}</div>{cf_}</div>
  <div>{badge(lbl, cf)}</div>
</div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


tab1, tab2, tab3 = st.tabs([
    "Auto-Collect from Trustpilot URL",
    "Paste Reviews (any website)",
    "Upload Reviews File",
])

# ── TAB 1: Auto crawl ─────────────────────────────────────
with tab1:
    st.markdown("""
<div class="info-box">
  <strong>How to use:</strong> Paste a Trustpilot company URL and click <b>Start Scan</b>.
  Note: Trustpilot sometimes blocks automated collection.
  If it fails, use Tab 2 or Tab 3.
</div>
""", unsafe_allow_html=True)

    url_in = st.text_input("Trustpilot URL",
                           placeholder="https://www.trustpilot.com/review/amazon.com")
    go1 = st.button("Start Scan", key="go_crawl")

    if go1:
        if not url_in.strip():
            st.warning("Please enter a URL.")
        else:
            with st.spinner("Collecting reviews — this may take up to 30 seconds..."):
                try:
                    subprocess.call(f"python review_crawler.py {url_in}",
                                    shell=True, timeout=60)
                except Exception:
                    pass

            revs = []
            for path in ["reviews.json", "reviews1.csv"]:
                if os.path.exists(path) and os.path.getsize(path) > 10:
                    try:
                        if path.endswith(".json"):
                            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                                data = json.load(f)
                            revs = [r.get("body","").strip() for r in data
                                    if isinstance(r, dict) and len(r.get("body","").strip()) > 5]
                        else:
                            df_u = pd.read_csv(path, encoding="utf-8", errors="replace")
                            if "body" in df_u.columns:
                                revs = df_u["body"].dropna().astype(str).str.strip().tolist()
                                revs = [r for r in revs if len(r) > 5 and r != "nan"]
                        if revs:
                            break
                    except Exception:
                        continue

            if revs:
                run_scan(revs)
            else:
                st.error("Could not collect reviews from that URL. Trustpilot may have blocked the request.")
                st.markdown("""
<div class="tip-box">
  <strong>Use Tab 2 instead — it always works:</strong><br>
  1. Open the Trustpilot page in your browser<br>
  2. Select and copy all review texts<br>
  3. Click <b>Paste Reviews</b> tab above and paste them in
</div>
""", unsafe_allow_html=True)

# ── TAB 2: Paste reviews ──────────────────────────────────
with tab2:
    st.markdown("""
<div class="info-box">
  <strong>Works with any website — Amazon, Google, Trustpilot, or anywhere:</strong><br>
  1. Open the product page in your browser<br>
  2. Copy the review texts you want to check<br>
  3. Paste them below — one review per line — and click <b>Scan Pasted Reviews</b>
</div>
""", unsafe_allow_html=True)

    pasted = st.text_area("Paste reviews here (one per line)",
                          height=200,
                          placeholder="Paste reviews here, one per line:\n\nThis product is amazing!! Best thing I ever bought!!!\nReasonable quality for the price, packaging was good.")
    go2 = st.button("Scan Pasted Reviews", key="go_paste")

    if go2:
        if not pasted.strip():
            st.warning("Please paste at least one review.")
        else:
            revs = [l.strip() for l in pasted.splitlines() if l.strip() and len(l.strip()) > 5]
            if not revs:
                st.warning("No reviews found. Make sure each review is on its own line.")
            else:
                run_scan(revs)

# ── TAB 3: File upload ────────────────────────────────────
with tab3:
    st.markdown("""
<div class="info-box">
  <strong>How to use:</strong><br>
  Upload a <b>.TXT file</b> (one review per line) or a <b>.CSV file</b>
  (with a column of reviews named <b>body</b>, <b>review_text</b>, or <b>review</b>).
</div>
""", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload reviews file", type=["txt","csv"], key="crawler_upload")
    go3 = st.button("Scan Uploaded File", key="go_file", disabled=(uploaded is None))

    if go3 and uploaded:
        revs = []
        err  = None
        if uploaded.name.lower().endswith(".txt"):
            try:
                raw  = uploaded.read().decode("utf-8", errors="ignore")
                revs = [l.strip() for l in raw.splitlines() if l.strip() and len(l.strip()) > 5]
            except Exception as e:
                err = str(e)
        else:
            df_u = None
            for enc in ["utf-8","utf-8-sig","latin-1","cp1252"]:
                try:
                    uploaded.seek(0)
                    df_u = pd.read_csv(uploaded, encoding=enc, on_bad_lines="skip")
                    if not df_u.empty: break
                except Exception:
                    continue
            if df_u is not None and not df_u.empty:
                col = None
                for c in ["body","review_text","review","text","comment","content"]:
                    if c in df_u.columns: col = c; break
                if col is None:
                    oc = df_u.select_dtypes(include="object").columns.tolist()
                    if oc:
                        col = max(oc, key=lambda c: df_u[c].dropna().astype(str).str.len().mean())
                if col:
                    revs = df_u[col].dropna().astype(str).str.strip().tolist()
                    revs = [r for r in revs if len(r) > 5 and r.lower() != "nan"]
                else:
                    err = "Could not find a review text column. Rename it to **body** or **review_text**."
            else:
                err = "Could not read the file. Try saving it as UTF-8 CSV."
        if err:
            st.error(err)
        elif not revs:
            st.warning("No review text found in the file.")
        else:
            run_scan(revs)

footer()
st.markdown('</div>', unsafe_allow_html=True)