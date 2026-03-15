# utils.py — Fake Review Detector AI — backend (never shown to user)
import io, re, base64, pickle
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from wordcloud import WordCloud
from datetime import datetime
import nltk

nltk.download("stopwords", quiet=True)
SW = set(stopwords.words("english"))

# ── Brand Colours ──────────────────────────────────────────
BLUE   = "#1D4ED8"   # primary blue
BLIGHT = "#2563EB"   # hover blue
BDARK  = "#1E3A8A"   # dark blue
RED    = "#DC2626"   # danger / fake
GREEN  = "#16A34A"   # success / legit
AMBER  = "#D97706"   # warning / medium
SLATE  = "#0F172A"   # dark text
GRAY   = "#64748B"   # muted text
LGRAY  = "#F1F5F9"   # light bg
BORDER = "#E2E8F0"   # border
WHITE  = "#FFFFFF"

# ── Model Loader ───────────────────────────────────────────
@st.cache_resource
def load_models():
    m = pickle.load(open("Models/best_model.pkl",       "rb"))
    v = pickle.load(open("Models/count_vectorizer.pkl", "rb"))
    return m, v

# ── Classification ─────────────────────────────────────────
def _preprocess(text):
    corrected = str(TextBlob(text).correct())
    cleaned   = re.sub(r"[^a-zA-Z]", " ", corrected)
    ps        = PorterStemmer()
    return " ".join(ps.stem(t) for t in cleaned.lower().split() if t not in SW)

def classify(text, model, vec):
    if not text.strip(): return None, None
    v    = vec.transform([_preprocess(text)]).toarray()
    pred = model.predict(v)[0]
    try:    conf = round(float(max(model.predict_proba(v)[0])) * 100, 1)
    except: conf = None
    return str(pred), conf

# ── Sentiment ──────────────────────────────────────────────
def sentiment(text):
    b   = TextBlob(text)
    pol = round(b.sentiment.polarity,     3)
    sub = round(b.sentiment.subjectivity, 3)
    lbl = "Positive" if pol > .15 else ("Negative" if pol < -.10 else "Neutral")
    return pol, sub, lbl

# ── Deception Signals (internal only) ─────────────────────
def _signals(text):
    words  = text.split()
    n_w    = max(len(words), 1)
    n_c    = max(len(text),  1)
    emo    = {"amazing","perfect","incredible","best","worst","terrible","awful",
              "fantastic","great","excellent","horrible","love","hate","absolutely",
              "totally","completely","highly","very","extremely","outstanding","superb"}
    fp     = {"i","me","my","mine","myself","we","our","us","ours"}
    excl_w = {"but","except","without","although","however","though","unless","instead","rather"}
    return {
        "emo_%":     round(sum(1 for w in words if w.lower() in emo)   / n_w * 100, 1),
        "fp_%":      round(sum(1 for w in words if w.lower() in fp)    / n_w * 100, 1),
        "excl_w":    sum(1 for w in words if w.lower() in excl_w),
        "excl_mk":   text.count("!"),
        "caps_%":    round(sum(1 for c in text if c.isupper()) / n_c * 100, 1),
        "ttr":       round(len(set(w.lower() for w in words)) / n_w, 3),
        "word_count":n_w,
        "char_count":n_c,
    }

def risk(sig, label, conf):
    s = 0
    if label != "True":        s += 42
    if conf:                   s += int((100 - conf) * 0.12)
    if sig["excl_mk"]  > 2:   s += 8
    if sig["caps_%"]   > 7:   s += 8
    if sig["fp_%"]     > 18:  s += 7
    if sig["emo_%"]    > 12:  s += 7
    if sig["ttr"]      < 0.5: s += 6
    if sig["excl_w"]   < 2:   s += 6
    return min(s, 100)

# ── Session state ──────────────────────────────────────────
def init():
    for k, v in [("n_total",0),("n_fake",0),("n_legit",0),("history",[])]:
        if k not in st.session_state: st.session_state[k] = v

def track(label, text, conf, pol, slbl):
    st.session_state.n_total += 1
    if label == "True": st.session_state.n_legit += 1
    else:               st.session_state.n_fake  += 1
    st.session_state.history.append({
        "time":      datetime.now().strftime("%H:%M:%S"),
        "text":      text[:65] + ("…" if len(text) > 65 else ""),
        "verdict":   "Legitimate" if label == "True" else "Fake",
        "conf":      conf,
        "sentiment": slbl,
        "polarity":  pol,
    })

# ── Word cloud ─────────────────────────────────────────────
def make_wc(texts, fake=True):
    combined = " ".join(texts)
    if not combined.strip(): return None
    wc = WordCloud(
        width=680, height=220,
        background_color=WHITE,
        colormap="Reds" if fake else "Blues",
        max_words=60, prefer_horizontal=.85, stopwords=SW,
    ).generate(combined)
    fig, ax = plt.subplots(figsize=(6.8, 2.2), facecolor=WHITE)
    ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
    fig.tight_layout(pad=0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig); buf.seek(0)
    return base64.b64encode(buf.read()).decode()

# ── Plotly helpers ─────────────────────────────────────────
_bg = "rgba(0,0,0,0)"

def donut(fake, legit):
    fig = go.Figure(go.Pie(
        labels=["Fake", "Legitimate"], values=[fake, legit], hole=.65,
        marker=dict(colors=[RED, GREEN], line=dict(color=WHITE, width=3)),
        textinfo="none",
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=_bg, plot_bgcolor=_bg, showlegend=True,
        height=220, margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(font=dict(family="Inter, sans-serif", size=11, color=GRAY), bgcolor=_bg),
        annotations=[dict(text=f"<b>{fake+legit}</b>", x=.5, y=.5,
                          font=dict(size=24, family="Inter, sans-serif", color=SLATE),
                          showarrow=False)],
    )
    return fig

def conf_hist(confs):
    fig = go.Figure(go.Histogram(
        x=confs, nbinsx=18,
        marker=dict(color=BLUE, opacity=.8, line=dict(color=WHITE, width=1)),
        hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=_bg, plot_bgcolor="#F8FAFC",
        xaxis=dict(title=dict(text="Confidence %", font=dict(size=11)), color=GRAY,
                   gridcolor=BORDER),
        yaxis=dict(title=dict(text="Reviews", font=dict(size=11)), color=GRAY,
                   gridcolor=BORDER),
        margin=dict(t=8, b=38, l=42, r=8), height=200, bargap=.06,
    )
    return fig

def scatter(df):
    colors = df["verdict"].map({"Fake": RED, "Legitimate": GREEN})
    fig = go.Figure(go.Scatter(
        x=df["polarity"], y=df["subjectivity"], mode="markers",
        marker=dict(color=colors, size=7, opacity=.75,
                    line=dict(color=WHITE, width=1)),
        text=df.get("preview", df["review"].str[:38]),
        hovertemplate="<b>%{text}</b><br>Polarity: %{x:.2f}  Subjectivity: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=_bg, plot_bgcolor="#F8FAFC",
        xaxis=dict(title=dict(text="Tone (Negative → Positive)", font=dict(size=11)),
                   range=[-1.1,1.1], gridcolor=BORDER, zeroline=True,
                   zerolinecolor=BORDER, color=GRAY),
        yaxis=dict(title=dict(text="Subjectivity", font=dict(size=11)),
                   range=[-.05,1.05], gridcolor=BORDER, color=GRAY),
        margin=dict(t=8, b=38, l=48, r=8), height=240,
    )
    return fig

def gauge(score):
    score = max(0, min(100, int(score)))
    col = GREEN if score < 40 else (AMBER if score < 70 else RED)
    lbl = "Low Risk" if score < 40 else ("Medium Risk" if score < 70 else "High Risk")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        gauge=dict(
            axis=dict(range=[0, 100]),
            bar=dict(color=col, thickness=.25),
            bgcolor=LGRAY,
            bordercolor=BORDER,
            borderwidth=1,
            steps=[
                dict(range=[0,  40], color="#DCFCE7"),
                dict(range=[40, 70], color="#FEF3C7"),
                dict(range=[70,100], color="#FEE2E2"),
            ],
            threshold=dict(
                line=dict(color=col, width=2),
                thickness=.7,
                value=score
            ),
        ),
        number=dict(font=dict(size=28, color=col)),
        title=dict(text=f"<b>{lbl}</b>", font=dict(size=12, color=GRAY)),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        height=185,
        margin=dict(t=30, b=8, l=20, r=20)
    )
    return fig

def bar_chart(labels, values, colors):
    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker=dict(color=colors, line=dict(color=WHITE, width=1)),
        hovertemplate="%{x}: %{y}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=_bg, plot_bgcolor="#F8FAFC",
        xaxis=dict(gridcolor=BORDER, color=GRAY),
        yaxis=dict(title=dict(text="Count", font=dict(size=11)),
                   gridcolor=BORDER, color=GRAY),
        margin=dict(t=8, b=28, l=40, r=8), height=200, showlegend=False,
    )
    return fig

# ── Shared CSS ─────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --blue:   #1D4ED8;
  --blight: #2563EB;
  --bdark:  #1E3A8A;
  --red:    #DC2626;
  --green:  #16A34A;
  --amber:  #D97706;
  --slate:  #0F172A;
  --gray:   #64748B;
  --lgray:  #F1F5F9;
  --border: #E2E8F0;
  --white:  #FFFFFF;
}

/* ── RESET ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp {
  background: #FFFFFF !important;
  color: #0F172A !important;
  font-family: 'Inter', sans-serif !important;
}
.block-container { padding: 0 0 4rem !important; max-width: 100% !important; }
#MainMenu, footer, header, .stDeployButton { display: none !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
  background: var(--bdark) !important;
  border-right: none !important;
}
section[data-testid="stSidebar"] * { color: #CBD5E1 !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stSidebarNav"] a {
  font-size: .875rem !important; border-radius: 6px !important;
  color: #94A3B8 !important; font-weight: 400 !important;
  padding: .5rem .75rem !important; margin: .1rem 0 !important;
}
[data-testid="stSidebarNav"] a:hover { background: rgba(255,255,255,.08) !important; color: #fff !important; }
[data-testid="stSidebarNav"] a[aria-current="page"] {
  background: rgba(255,255,255,.12) !important;
  color: #fff !important; font-weight: 600 !important;
  border-left: 3px solid #60A5FA !important;
}
[data-testid="stSidebarNavSeparatorHeader"] {
  color: #475569 !important; font-size: .68rem !important; letter-spacing: .1em !important;
}
::-webkit-scrollbar { width: 4px; background: var(--lgray); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

/* ── TOP NAV BAR ── */
.topnav {
  background: var(--blue);
  padding: 0 2.5rem;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0,0,0,.15);
}
.topnav-brand {
  display: flex; align-items: center; gap: .75rem;
}
.topnav-logo {
  width: 34px; height: 34px; border-radius: 8px;
  background: rgba(255,255,255,.15);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; flex-shrink: 0;
}
.topnav-name {
  font-size: 1.05rem; font-weight: 700; color: #fff; letter-spacing: -.01em;
}
.topnav-tagline {
  font-size: .72rem; color: rgba(255,255,255,.6); margin-top: .05rem;
}
.topnav-pills { display: flex; align-items: center; gap: .6rem; }
.pill {
  font-size: .72rem; font-weight: 500;
  padding: .3rem .85rem; border-radius: 20px;
  border: 1px solid rgba(255,255,255,.25);
  color: rgba(255,255,255,.85);
  background: rgba(255,255,255,.08);
}
.pill-live {
  background: rgba(22,163,74,.2); border-color: rgba(22,163,74,.4); color: #86EFAC;
}
.pill-live::before { content: "● "; animation: blink 2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* ── PAGE WRAPPER ── */
.pw { padding: 0 2.5rem; max-width: 1400px; margin: 0 auto; }

/* ── PAGE HEADER INSIDE CONTENT ── */
.pg-hd {
  padding: 2rem 0 1.5rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
}
.pg-hd-title {
  font-size: 1.75rem; font-weight: 700; color: var(--slate); letter-spacing: -.02em;
}
.pg-hd-sub { font-size: .875rem; color: var(--gray); margin-top: .3rem; }

/* ── STATS STRIP ── */
.stats { display: grid; grid-template-columns: repeat(4,1fr); gap: 1rem; margin-bottom: 1.8rem; }
.stat {
  background: var(--white); border: 1px solid var(--border);
  border-radius: 12px; padding: 1.2rem 1.4rem;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
  transition: box-shadow .2s;
}
.stat:hover { box-shadow: 0 4px 12px rgba(0,0,0,.1); }
.stat-lbl { font-size: .75rem; font-weight: 500; color: var(--gray); text-transform: uppercase; letter-spacing: .06em; margin-bottom: .5rem; }
.stat-val { font-size: 2rem; font-weight: 700; letter-spacing: -.02em; line-height: 1; }
.stat-sub { font-size: .75rem; color: var(--gray); margin-top: .3rem; }
.sv-blue  { color: var(--blue); }
.sv-red   { color: var(--red); }
.sv-green { color: var(--green); }
.sv-amber { color: var(--amber); }

/* ── CARD ── */
.card {
  background: var(--white); border: 1px solid var(--border);
  border-radius: 12px; padding: 1.6rem 1.8rem; margin-bottom: 1.2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.card-hd { display: flex; align-items: center; gap: .85rem; margin-bottom: 1.2rem; }
.card-ic {
  width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
  background: #EFF6FF; border: 1px solid #BFDBFE;
  display: flex; align-items: center; justify-content: center; font-size: 1rem;
}
.card-ht { font-size: 1rem; font-weight: 600; color: var(--slate); }
.card-hs { font-size: .8rem; color: var(--gray); margin-top: .12rem; }

/* ── TWO LANE (simple / detailed) ── */
.lanes { display: grid; grid-template-columns: 1fr 1fr; gap: .9rem; margin-bottom: 1.3rem; }
.lane { border-radius: 10px; padding: .9rem 1.1rem; }
.lane-s { background: #EFF6FF; border: 1px solid #BFDBFE; }
.lane-d { background: #F8FAFC; border: 1px solid var(--border); }
.lane-tag { font-size: .68rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; margin-bottom: .35rem; }
.lane-s .lane-tag { color: var(--blue); }
.lane-d .lane-tag { color: var(--gray); }
.lane-body { font-size: .875rem; color: var(--slate); line-height: 1.7; }

/* ── INPUTS ── */
.stTextArea textarea, .stTextInput > div > div > input {
  background: var(--white) !important; border: 1.5px solid var(--border) !important;
  border-radius: 8px !important; color: var(--slate) !important;
  font-family: 'Inter', sans-serif !important; font-size: .875rem !important;
  transition: border-color .2s, box-shadow .2s !important;
}
.stTextArea textarea:focus, .stTextInput > div > div > input:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px rgba(29,78,216,.1) !important;
}
label[data-testid="stWidgetLabel"] p {
  color: var(--slate) !important; font-family: 'Inter', sans-serif !important;
  font-size: .78rem !important; font-weight: 600 !important; letter-spacing: .02em !important;
}

/* ── BUTTON ── */
.stButton > button {
  background: var(--blue) !important; color: var(--white) !important;
  border: none !important; border-radius: 8px !important;
  font-family: 'Inter', sans-serif !important; font-size: .875rem !important;
  font-weight: 600 !important; padding: .6rem 1.8rem !important;
  box-shadow: 0 1px 3px rgba(0,0,0,.15) !important;
  transition: all .18s !important;
}
.stButton > button:hover {
  background: var(--blight) !important;
  box-shadow: 0 4px 12px rgba(29,78,216,.3) !important;
  transform: translateY(-1px) !important;
}
.stButton > button:disabled {
  background: var(--border) !important; color: var(--gray) !important;
  box-shadow: none !important; transform: none !important;
}

/* ── VERDICT BADGES ── */
.badge {
  display: inline-flex; align-items: center; gap: .35rem;
  border-radius: 20px; padding: .3rem .9rem;
  font-size: .8rem; font-weight: 600; white-space: nowrap;
}
.badge-ok  { background: #DCFCE7; color: #15803D; border: 1px solid #BBF7D0; }
.badge-bad { background: #FEE2E2; color: #B91C1C; border: 1px solid #FECACA; }

/* ── RESULT ROWS ── */
.rows { display: flex; flex-direction: column; gap: .5rem; }
.row {
  display: grid; grid-template-columns: 36px 1fr auto;
  gap: .8rem; align-items: center;
  background: var(--white); border: 1px solid var(--border);
  border-radius: 10px; padding: .85rem 1.1rem;
  box-shadow: 0 1px 2px rgba(0,0,0,.04);
  transition: box-shadow .18s, border-color .18s;
}
.row:hover { box-shadow: 0 3px 10px rgba(0,0,0,.08); border-color: #CBD5E1; }
.row.ok  { border-left: 4px solid var(--green); }
.row.bad { border-left: 4px solid var(--red); }
.row-n { font-size: .72rem; color: var(--gray); font-weight: 500; text-align: center; }
.row-t { font-size: .875rem; line-height: 1.55; color: var(--slate); }
.row-m { font-size: .75rem; color: var(--gray); margin-top: .15rem; }

/* ── SUMMARY PAIR ── */
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1.1rem 0; }
.pcell { border-radius: 10px; padding: 1.1rem 1.3rem; }
.pcell.bad { background: #FEE2E2; border: 1px solid #FECACA; }
.pcell.ok  { background: #DCFCE7; border: 1px solid #BBF7D0; }
.pn { font-size: 2rem; font-weight: 700; line-height: 1; }
.pcell.bad .pn { color: var(--red); }
.pcell.ok  .pn { color: var(--green); }
.pl { font-size: .75rem; color: var(--gray); margin-top: .28rem; font-weight: 500; }

/* ── SIGNAL BARS ── */
.sbar { display: flex; align-items: center; gap: .75rem; padding: .55rem .9rem; background: var(--lgray); border-radius: 8px; margin: .3rem 0; }
.sbar-lbl { font-size: .78rem; font-weight: 500; color: var(--slate); min-width: 160px; }
.sbar-track { flex: 1; background: var(--border); border-radius: 99px; height: 6px; overflow: hidden; }
.sbar-fill  { height: 100%; border-radius: 99px; transition: width .4s ease; }
.sbar-val   { font-size: .78rem; font-weight: 600; min-width: 52px; text-align: right; }

/* ── PROGRESS ── */
.stProgress > div > div {
  background: var(--blue) !important; border-radius: 99px !important;
}
.stProgress > div { background: var(--border) !important; border-radius: 99px !important; height: 6px !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] > div {
  background: #F8FAFC !important; border: 1.5px dashed var(--border) !important;
  border-radius: 10px !important; transition: border-color .2s !important;
}
[data-testid="stFileUploader"] > div:hover { border-color: var(--blue) !important; background: #EFF6FF !important; }
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] span { color: var(--gray) !important; font-size: .8rem !important; }

/* ── SELECT ── */
.stSelectbox > div > div {
  background: var(--white) !important; border: 1.5px solid var(--border) !important;
  color: var(--slate) !important; border-radius: 8px !important;
  font-family: 'Inter', sans-serif !important;
}

/* ── DOWNLOAD ── */
.stDownloadButton > button {
  background: transparent !important; color: var(--blue) !important;
  border: 1.5px solid #BFDBFE !important; font-weight: 500 !important;
}
.stDownloadButton > button:hover {
  background: #EFF6FF !important; border-color: var(--blue) !important;
  transform: translateY(-1px) !important;
}

/* ── INFO BOX ── */
.info-box {
  background: #EFF6FF; border: 1px solid #BFDBFE; border-left: 3px solid var(--blue);
  border-radius: 8px; padding: .85rem 1.1rem; margin: .8rem 0;
  font-size: .84rem; color: #1E3A8A; line-height: 1.65;
}
.tip-box {
  background: #FFFBEB; border: 1px solid #FDE68A; border-left: 3px solid var(--amber);
  border-radius: 8px; padding: .85rem 1.1rem; margin: .8rem 0;
  font-size: .84rem; color: #78350F; line-height: 1.65;
}

/* ── CAPTION ── */
.stCaption, [data-testid="stCaptionContainer"] p {
  color: var(--gray) !important; font-size: .75rem !important;
}
.stSpinner > div { border-top-color: var(--blue) !important; }
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── FOOTER ── */
.foot {
  background: var(--lgray); border-top: 1px solid var(--border);
  padding: 1.5rem 2.5rem; margin-top: 3rem;
  display: flex; justify-content: space-between; align-items: center;
}
.foot-brand { font-size: .9rem; font-weight: 700; color: var(--blue); }
.foot-copy  { font-size: .75rem; color: var(--gray); }
button[data-testid="collapsedControl"] {
  background: #1D4ED8 !important;
  border-radius: 0 8px 8px 0 !important;
  width: 28px !important;
  height: 56px !important;
  border: none !important;
  box-shadow: 2px 0 8px rgba(0,0,0,.15) !important;
}
button[data-testid="collapsedControl"]:hover {
  background: #2563EB !important;
}
button[data-testid="collapsedControl"] svg {
  color: white !important;
  fill: white !important;
}
[data-testid="stSidebarCollapseButton"] {
  display: none !important;
}
</style>
"""

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)

# ── Top navigation bar ──────────────────────────────────────
def topnav():
    n  = st.session_state.get("n_total", 0)
    nf = st.session_state.get("n_fake",  0)
    st.markdown(f"""
<div class="topnav">
  <div class="topnav-brand">
    <div class="topnav-logo">🔍</div>
    <div>
      <div class="topnav-name">Fake Review Detector</div>
      <div class="topnav-tagline">AI-Powered Review Authentication</div>
    </div>
  </div>
  <div class="topnav-pills">
    <span class="pill">Reviews Scanned: <b style="color:#fff">{n}</b></span>
    <span class="pill">Fake Found: <b style="color:#FCA5A5">{nf}</b></span>
    <span class="pill pill-live">AI Active</span>
    <span class="pill" style="border-color:rgba(255,255,255,.4);color:#fff;font-weight:600">Roll No: 23CS116</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar logo ────────────────────────────────────────────
def sidebar_logo():
    st.sidebar.markdown("""
<div style="padding:1.3rem .8rem 1.2rem;margin-bottom:.2rem;border-bottom:1px solid rgba(255,255,255,.08)">
  <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:.4rem">
    <div style="width:30px;height:30px;border-radius:7px;background:rgba(255,255,255,.12);
      display:flex;align-items:center;justify-content:center;font-size:.95rem">🔍</div>
    <div style="font-size:.95rem;font-weight:700;color:#fff;letter-spacing:-.01em">Fake Review Detector</div>
  </div>
  <div style="font-size:.7rem;color:#475569;padding-left:2.4rem">AI-Powered Review Checker</div>
  <div style="font-size:.68rem;color:#334155;padding-left:2.4rem;margin-top:.25rem;font-weight:600;letter-spacing:.03em">Roll No: 23CS116</div>
</div>""", unsafe_allow_html=True)

# ── Page section header ─────────────────────────────────────
def page_header(title: str, subtitle: str = ""):
    sub = f'<div class="pg-hd-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
<div class="pw">
  <div class="pg-hd">
    <div class="pg-hd-title">{title}</div>
    {sub}
  </div>
</div>""", unsafe_allow_html=True)

# ── Verdict badge HTML ──────────────────────────────────────
def badge(label, conf=None):
    c   = f" · {conf}% confident" if conf else ""
    cls = "ok" if label == "True" else "bad"
    ico = "✓" if label == "True" else "✗"
    txt = "Legitimate" if label == "True" else "Fake"
    return f'<span class="badge badge-{cls}">{ico} {txt}{c}</span>'

# ── Signal bar HTML ─────────────────────────────────────────
def sbar(label, val, max_val, color, disp=None):
    pct  = min(int(val / max(max_val, .001) * 100), 100)
    show = disp if disp is not None else str(val)
    return f"""
<div class="sbar">
  <span class="sbar-lbl">{label}</span>
  <div class="sbar-track">
    <div class="sbar-fill" style="width:{pct}%;background:{color}"></div>
  </div>
  <span class="sbar-val" style="color:{color}">{show}</span>
</div>"""
def footer():
    st.markdown("""
<div class="foot">
  <div class="foot-brand">Review Analyzer</div>
  <div style="font-size:.75rem;color:#64748B;font-weight:600">Made by Roll No: 23CS116</div>
  <div class="foot-copy">AI predictions only — use as a guide alongside your own judgment.</div>
</div>
""", unsafe_allow_html=True)