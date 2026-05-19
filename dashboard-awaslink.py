import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import Counter
import re

try:
    from wordcloud import WordCloud
    HAS_WORDCLOUD = True
except ImportError:
    HAS_WORDCLOUD = False

# ─── Stopwords & preprocessing (sesuai notebook) ────────────────────────────
STOPWORDS_ID = {
    'yang','dan','di','ini','itu','ke','dari','untuk','dengan',
    'adalah','atau','pada','juga','tidak','dalam','akan','ada',
    'saya','anda','kamu','kami','kita','dia','ia','mereka',
    'satu','dua','tiga','sudah','bisa','dapat','telah','lebih',
    'seperti','kalau','jika','maka','namun','tetapi','karena',
    'hingga','sampai','setelah','sebelum','serta',
    'bahwa','oleh','semua','hanya','orang','ingin','tahu',
    'hari','waktu','mungkin','beberapa','apakah','memiliki',
    'tentang','terima','kasih','sini','apa',
    'perusahaan','bisnis','informasi','email','situs','web',
    'the','a','an','is','in','on','at','to','of','and','or',
    'be','has','have','was','were','are','not','it','this',
    'that','with','for','as','by','from','but','so','if',
    'we','you','your','our','they','their','all','can','will',
    'just','about','only','also','more','here','there',
    'pls','msg','ok','ya','yg','ny','dg','sy','utk','jd',
    'jg','tp','lg','sdh','blm','bln','thn',
}

URL_PATTERN = (
    r'https?://[^\s]+|www\.[^\s]+|'
    r'[a-zA-Z0-9.-]+\.(?:com|net|org|id|co\.id|my\.id|ac\.id|go\.id|info|biz)\b'
)

def preprocess_for_wordfreq(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'https?://\S+|www\.\S+|\S+\.(?:com|net|org|id|co\.id)\S*', ' ', text)
    text = re.sub(r'\b(?:com|net|org|id|co|my|biz|web|info)\b', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_top_words(series_text, top_n=20):
    all_words = []
    for text in series_text:
        processed = preprocess_for_wordfreq(text)
        words = [w for w in processed.split() if len(w) > 2 and w not in STOPWORDS_ID]
        all_words.extend(words)
    return Counter(all_words).most_common(top_n)

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AwasLink Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ─── Color Palette (sesuai notebook: biru untuk Ham, merah untuk Spam) ───────
COLOR_SPAM   = "#FF0000"   # Bright red  (sesuai notebook)
COLOR_HAM    = "#069AF3"   # Bright blue (sesuai notebook)
COLOR_ACCENT = "#F57C00"
COLOR_BG     = "#F0F4F8"

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.main { background-color: #F5F7FA; }

.cover-banner {
    background: linear-gradient(135deg, #0D2B6B 0%, #1565C0 60%, #42A5F5 100%);
    padding: 40px;
    border-radius: 24px;
    margin-bottom: 28px;
    color: white;
    box-shadow: 0 8px 32px rgba(21,101,192,0.25);
    position: relative;
    overflow: hidden;
}

.cover-banner::before {
    content: "🛡️";
    position: absolute;
    right: 40px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 100px;
    opacity: 0.12;
}

.cover-banner h1 {
    font-size: 36px;
    font-weight: 800;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}

.cover-banner p {
    font-size: 16px;
    opacity: 0.85;
    margin-bottom: 18px;
    max-width: 560px;
}

.badge-row { display: flex; gap: 10px; flex-wrap: wrap; }

.badge {
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.28);
    padding: 7px 16px;
    border-radius: 50px;
    font-size: 13px;
    font-weight: 600;
    backdrop-filter: blur(4px);
}

/* Metric Cards */
.metric-card {
    background: white;
    padding: 24px 20px;
    border-radius: 20px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
    text-align: center;
    transition: all 0.25s ease;
    border-top: 4px solid #1565C0;
    height: 100%;
}
.metric-card.spam { border-top-color: #FF0000; }
.metric-card.ham  { border-top-color: #069AF3; }
.metric-card.warn { border-top-color: #F57C00; }
.metric-card.ok   { border-top-color: #2E7D32; }

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.metric-card .icon  { font-size: 28px; margin-bottom: 8px; }
.metric-card .value { font-size: 30px; font-weight: 800; color: #0D2B6B; margin-bottom: 4px; font-family: 'JetBrains Mono', monospace; }
.metric-card .label { font-size: 13px; color: #666; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.metric-card .sub   { font-size: 12px; color: #999; margin-top: 4px; }

/* Section Titles */
.section-title {
    font-size: 22px;
    font-weight: 800;
    color: #0D2B6B;
    margin-top: 20px;
    margin-bottom: 4px;
    letter-spacing: -0.3px;
}
.section-desc {
    font-size: 14px;
    color: #555;
    margin-bottom: 16px;
    font-weight: 400;
    line-height: 1.6;
}

/* Insight Box */
.insight-box {
    background: linear-gradient(135deg, #E3F2FD, #EDE7F6);
    padding: 18px 22px;
    border-radius: 16px;
    border-left: 5px solid #1565C0;
    margin-top: 14px;
    margin-bottom: 8px;
    font-size: 14px;
    line-height: 1.7;
    color: #1a1a2e;
}
.insight-box b { color: #0D2B6B; }

/* Warning Box */
.warn-box {
    background: #FFF8E1;
    padding: 14px 20px;
    border-radius: 14px;
    border-left: 5px solid #F57C00;
    margin-bottom: 14px;
    font-size: 13px;
    color: #5D4037;
}

/* Tag pills for features */
.pill-spam { background:#FFE5E5; color:#C62828; padding:4px 12px; border-radius:50px; font-size:12px; font-weight:700; display:inline-block; margin:3px; }
.pill-ham  { background:#E3F2FD; color:#1565C0; padding:4px 12px; border-radius:50px; font-size:12px; font-weight:700; display:inline-block; margin:3px; }

/* Q-box */
.q-box {
    background: white;
    border: 1.5px solid #E3EBF9;
    border-radius: 18px;
    padding: 20px 24px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.q-box .q-num { font-size: 11px; font-weight: 700; color: #42A5F5; text-transform: uppercase; letter-spacing: 1px; }
.q-box .q-text { font-size: 15px; font-weight: 600; color: #1a1a2e; margin-top: 5px; }

/* Divider */
.divider { height: 1px; background: linear-gradient(90deg, #E3EBF9, transparent); margin: 28px 0; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D2B6B, #1565C0);
}
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stRadio label { color: white !important; }
</style>
""", unsafe_allow_html=True)


# ─── Load Data ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("combined_dataset_features.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ File 'combined_dataset_features.csv' tidak ditemukan. Pastikan file berada di direktori yang sama.")
    st.stop()

# ─── Fitur yang digunakan (sesuai notebook) ──────────────────────────────────
FITUR_INDIKATOR = [
    "kata_mendesak",
    "kata_hadiah",
    "kata_sensitif",
    "nama_brand",
    "angka_telepon",
    "ada_url",
    "simbol",
]

FITUR_NUMERIK = [
    "panjang_pesan",
    "jumlah_angka",
    "rasio_huruf_kapital",
    "jumlah_tanda_seru",
    "jumlah_kata",
    "jumlah_huruf_kapital",
]

LABEL_DISPLAY = {
    "kata_mendesak":      "Kata Mendesak\n(urgent/segera/deadline)",
    "kata_hadiah":        "Kata Hadiah\n(gratis/menang/bonus)",
    "kata_sensitif":      "Kata Sensitif\n(OTP/PIN/rekening)",
    "nama_brand":         "Nama Brand\n(BCA/Shopee/GoPay)",
    "angka_telepon":      "Nomor Telepon\n(+62/08xx)",
    "ada_url":            "Mengandung URL",
    "simbol":             "Simbol/Emoji\n(★/✓/☎)",
    "panjang_pesan":      "Panjang Pesan",
    "jumlah_angka":       "Jumlah Angka",
    "rasio_huruf_kapital":"Rasio Huruf Kapital",
    "jumlah_tanda_seru":  "Jumlah Tanda Seru (!)",
    "jumlah_kata":        "Jumlah Kata",
}

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ AwasLink")
    st.markdown("---")
    st.markdown("### 📂 Filter Data")
    label_filter = st.radio(
        "Tampilkan:",
        ["Semua Data", "Spam / Phishing", "Ham (Normal)"],
        index=0
    )
    st.markdown("---")
    st.markdown("### 📌 Pertanyaan Bisnis")
    st.markdown("""
    1. Distribusi Spam vs Ham  
    2. Kata Dominan Phishing  
    3. Fitur Numerik  
    4. Indikator Phishing  
    """)
    st.markdown("---")
    st.caption("Dashboard AwasLink | Capstone Project Data Scientist")

# ─── Filter ──────────────────────────────────────────────────────────────────
if label_filter == "Spam / Phishing":
    filtered_df = df[df["label"] == 1].copy()
elif label_filter == "Ham (Normal)":
    filtered_df = df[df["label"] == 0].copy()
else:
    filtered_df = df.copy()

spam_df = filtered_df[filtered_df["label"] == 1]
ham_df  = filtered_df[filtered_df["label"] == 0]

# ─── Statistik dasar ─────────────────────────────────────────────────────────
total_pesan   = len(filtered_df)
total_spam    = len(spam_df)
total_ham     = len(ham_df)
pct_spam      = (total_spam / total_pesan * 100) if total_pesan > 0 else 0
pct_ham       = (total_ham  / total_pesan * 100) if total_pesan > 0 else 0
missing_vals  = filtered_df.isnull().sum().sum()

# Rasio imbalance (sesuai notebook: ham:spam ≈ 1.5:1)
rasio_str = f"{total_ham}:{total_spam}" if total_spam > 0 else "N/A"
rasio_val  = round(total_ham / total_spam, 2) if total_spam > 0 else 0

# ═══════════════════════════════════════════════════════════════════════════
#  COVER BANNER
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="cover-banner">
    <h1>🛡️ AwasLink Dashboard</h1>
    <p>Analisis deteksi pesan <b>Spam & Phishing</b> berbasis pola teks, fitur numerik, dan indikator linguistik pada dataset pesan Indonesia.</p>
    <div class="badge-row">
        <span class="badge">📨 {total_pesan:,} Pesan</span>
        <span class="badge">📂 {label_filter}</span>
        <span class="badge">⚠️ Rasio Ham:Spam ≈ {rasio_val:.1f}:1</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Pertanyaan Bisnis (Konteks) ─────────────────────────────────────────────
with st.expander("📋 Lihat 4 Pertanyaan Bisnis yang Dijawab Dashboard Ini", expanded=False):
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        st.markdown("""
        <div class="q-box">
            <div class="q-num">Pertanyaan 1</div>
            <div class="q-text">Bagaimana distribusi jumlah dan persentase pesan phishing vs normal, dan apakah ada ketidakseimbangan data?</div>
        </div>
        <div class="q-box">
            <div class="q-num">Pertanyaan 2</div>
            <div class="q-text">Kata-kata apa yang paling dominan pada pesan phishing dibandingkan pesan normal?</div>
        </div>
        """, unsafe_allow_html=True)
    with col_q2:
        st.markdown("""
        <div class="q-box">
            <div class="q-num">Pertanyaan 3</div>
            <div class="q-text">Bagaimana karakteristik fitur numerik (panjang pesan, jumlah angka, rasio huruf kapital) pada pesan phishing vs normal?</div>
        </div>
        <div class="q-box">
            <div class="q-num">Pertanyaan 4</div>
            <div class="q-text">Seberapa sering indikator phishing seperti kata mendesak, OTP, URL, nomor telepon muncul pada pesan spam vs ham?</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 1 — OVERVIEW / PERTANYAAN 1
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 Overview — Distribusi Pesan (Pertanyaan 1)</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">Dataset terdiri dari pesan Ham (normal) dan Spam/Phishing yang dikumpulkan dari berbagai sumber SMS, email, dan URL Indonesia. Ham sedikit lebih banyak dari Spam dengan rasio sekitar 1.5:1 — tergolong <b>Cukup Seimbang</b>.</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="icon">📨</div>
        <div class="value">{total_pesan:,}</div>
        <div class="label">Total Pesan</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card spam">
        <div class="icon">🚨</div>
        <div class="value">{total_spam:,}</div>
        <div class="label">Spam / Phishing</div>
        <div class="sub">{pct_spam:.1f}% dari total</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card ham">
        <div class="icon">✅</div>
        <div class="value">{total_ham:,}</div>
        <div class="label">Ham (Normal)</div>
        <div class="sub">{pct_ham:.1f}% dari total</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card warn">
        <div class="icon">⚖️</div>
        <div class="value">{rasio_val:.1f}:1</div>
        <div class="label">Rasio Ham : Spam</div>
        <div class="sub">Cukup Seimbang</div>
    </div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""<div class="metric-card ok">
        <div class="icon">🔍</div>
        <div class="value">{missing_vals}</div>
        <div class="label">Missing Values</div>
        <div class="sub">Total pada dataset</div>
    </div>""", unsafe_allow_html=True)

# Visualisasi distribusi Q1
st.markdown("<br>", unsafe_allow_html=True)
fig1, axes1 = plt.subplots(1, 2, figsize=(14, 5))
fig1.patch.set_facecolor('#F5F7FA')

# Bar chart distribusi
categories  = ['Ham (Normal)', 'Spam / Phishing']
counts      = [total_ham, total_spam]
bar_colors  = [COLOR_HAM, COLOR_SPAM]
bars = axes1[0].bar(categories, counts, color=bar_colors, width=0.5, edgecolor='white', linewidth=2)
for bar, count in zip(bars, counts):
    axes1[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.01,
                  f'{count:,}', ha='center', va='bottom', fontsize=12, fontweight='bold')
axes1[0].set_title('Jumlah Pesan per Kategori', fontsize=13, fontweight='bold', pad=12)
axes1[0].set_ylabel('Jumlah Pesan')
axes1[0].spines[['top','right']].set_visible(False)
axes1[0].set_facecolor('#F5F7FA')
axes1[0].grid(axis='y', linestyle='--', alpha=0.4)

# Pie chart
pie_vals   = [v for v in [total_ham, total_spam] if v > 0]
pie_labels = [l for l, v in zip(['Ham (Normal)', 'Spam / Phishing'], [total_ham, total_spam]) if v > 0]
pie_colors = [c for c, v in zip([COLOR_HAM, COLOR_SPAM], [total_ham, total_spam]) if v > 0]
wedges, texts, autotexts = axes1[1].pie(
    pie_vals, labels=pie_labels, autopct='%1.1f%%',
    colors=pie_colors, startangle=90,
    textprops={'fontsize': 11},
    wedgeprops={'edgecolor': 'white', 'linewidth': 3}
)
for at in autotexts:
    at.set_fontweight('bold')
    at.set_fontsize(12)
axes1[1].set_title('Persentase Distribusi Label', fontsize=13, fontweight='bold', pad=12)
axes1[1].set_facecolor('#F5F7FA')

plt.suptitle('Pertanyaan 1: Distribusi Pesan Phishing dan Normal',
             fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout()
st.pyplot(fig1)

st.markdown("""
<div class="insight-box">
<b>💡 Insight — Pertanyaan 1:</b><br>
Dataset memiliki jumlah pesan <b>Ham (normal) yang sedikit lebih banyak</b> dari pesan Spam/Phishing dengan <b>rasio sekitar 1.5:1</b>.
Ketidakseimbangan ini tergolong <b>ringan</b>, sehingga model masih bisa dilatih tanpa penanganan imbalance khusus.
Namun, evaluasi menggunakan <b>precision, recall, dan F1-score</b> tetap penting agar model tidak condong ke kelas Ham semata.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 2 — KATA DOMINAN / PERTANYAAN 2
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔤 Kata Dominan — Phishing vs Normal (Pertanyaan 2)</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">Pesan phishing menggunakan kata-kata yang bersifat <b>ajakan, promosi, dan urgensi</b>. Pesan normal cenderung menggunakan kata-kata percakapan sehari-hari yang netral.</div>', unsafe_allow_html=True)

# ── Hitung top kata langsung dari CSV ───────────────────────────────────────
@st.cache_data
def compute_top_words(df, top_n=20):
    ham_texts  = df[df["label"] == 0]["text"] if "text" in df.columns else pd.Series([], dtype=str)
    spam_texts = df[df["label"] == 1]["text"] if "text" in df.columns else pd.Series([], dtype=str)
    top_ham  = get_top_words(ham_texts,  top_n=top_n)
    top_spam = get_top_words(spam_texts, top_n=top_n)
    return top_ham, top_spam

with st.spinner("Menghitung frekuensi kata dari dataset..."):
    top_ham_words, top_spam_words = compute_top_words(filtered_df, top_n=20)

ham_df_w  = pd.DataFrame(top_ham_words[:15],  columns=['Kata', 'Frekuensi'])
spam_df_w = pd.DataFrame(top_spam_words[:15], columns=['Kata', 'Frekuensi'])

# ── Word Cloud (ganti pills) ─────────────────────────────────────────────────
if HAS_WORDCLOUD and not ham_df_w.empty and not spam_df_w.empty:
    def red_color_func(*args, **kwargs):
        return "hsl(0, 100%, 35%)"

    def blue_color_func(*args, **kwargs):
        return "hsl(207, 97%, 49%)"

    # Build frequency dicts dari hasil hitung nyata
    freq_ham  = {row["Kata"]: row["Frekuensi"] for _, row in ham_df_w.iterrows()}
    freq_spam = {row["Kata"]: row["Frekuensi"] for _, row in spam_df_w.iterrows()}

    wc_ham = WordCloud(
        width=700, height=340, background_color='white',
        color_func=blue_color_func, max_words=50,
        collocations=False, random_state=42
    ).generate_from_frequencies(freq_ham)

    wc_spam = WordCloud(
        width=700, height=340, background_color='white',
        color_func=red_color_func, max_words=50,
        collocations=False, random_state=42
    ).generate_from_frequencies(freq_spam)

    fig_wc, axes_wc = plt.subplots(1, 2, figsize=(16, 5))
    fig_wc.patch.set_facecolor('#F5F7FA')

    for ax, wc, title, color in zip(
        axes_wc,
        [wc_ham, wc_spam],
        ['Word Cloud — Pesan Ham (Normal)', 'Word Cloud — Pesan Spam / Phishing'],
        [COLOR_HAM, COLOR_SPAM]
    ):
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(title, fontsize=13, fontweight='bold', pad=12, color=color)
        ax.set_facecolor('#F5F7FA')

    plt.suptitle('Pertanyaan 2: Pola Kata — Pesan Normal vs Spam / Phishing',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig_wc)
else:
    st.info("Install `wordcloud` untuk menampilkan Word Cloud: `pip install wordcloud`")

# ── Bar chart top kata (dihitung dari CSV) ───────────────────────────────────
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))
fig2.patch.set_facecolor('#F5F7FA')

spam_kritis = {'otp','verifikasi','klik','hadiah','gratis','rekening','menang'}

# Panel kiri: Ham
if not ham_df_w.empty:
    bars_h = axes2[0].barh(ham_df_w['Kata'][::-1], ham_df_w['Frekuensi'][::-1],
                            color=COLOR_HAM, alpha=0.85)
    x_max_h = ham_df_w['Frekuensi'].max()
    for bar in bars_h:
        axes2[0].text(bar.get_width() + x_max_h * 0.01,
                      bar.get_y() + bar.get_height() / 2,
                      f'{int(bar.get_width()):,}', va='center', fontsize=9, color='#333')
axes2[0].set_title('Top 15 Kata — Ham (Pesan Normal)', fontsize=12, fontweight='bold')
axes2[0].set_xlabel('Frekuensi Kemunculan')
axes2[0].spines[['top', 'right']].set_visible(False)
axes2[0].set_facecolor('#F5F7FA')

# Panel kanan: Spam (kata kritis lebih gelap)
if not spam_df_w.empty:
    bar_colors_s = [('#B20000' if w in spam_kritis else COLOR_SPAM)
                    for w in spam_df_w['Kata'][::-1]]
    bars_s = axes2[1].barh(spam_df_w['Kata'][::-1], spam_df_w['Frekuensi'][::-1],
                            color=bar_colors_s, alpha=0.85)
    x_max_s = spam_df_w['Frekuensi'].max()
    for bar in bars_s:
        axes2[1].text(bar.get_width() + x_max_s * 0.01,
                      bar.get_y() + bar.get_height() / 2,
                      f'{int(bar.get_width()):,}', va='center', fontsize=9, color='#333')
axes2[1].set_title('Top 15 Kata — Spam / Phishing\n(merah tua = kata kritis)', fontsize=12, fontweight='bold')
axes2[1].set_xlabel('Frekuensi Kemunculan')
axes2[1].spines[['top', 'right']].set_visible(False)
axes2[1].set_facecolor('#F5F7FA')

plt.suptitle('Pertanyaan 2: Pola Kata Dominan pada Pesan Normal vs Phishing',
             fontsize=14, fontweight='bold')
plt.tight_layout()
st.pyplot(fig2)

st.markdown("""
<div class="insight-box">
<b>💡 Insight — Pertanyaan 2:</b><br>
Pesan phishing memiliki kata-kata promosi dan urgensi yang sangat dominan seperti <b>"gratis"</b>, <b>"uang"</b>, <b>"klik"</b>, <b>"menang"</b>, dan <b>"sekarang"</b>.
Kata-kata ini digunakan untuk menarik perhatian dan mengarahkan korban ke tindakan tertentu.
Kata kritis (merah tua) seperti <b>"OTP"</b>, <b>"verifikasi"</b>, dan <b>"rekening"</b> secara langsung mengindikasikan upaya pencurian data finansial.
Sementara pesan normal menggunakan vocabulary percakapan sehari-hari yang netral dan bervariasi.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 3 — FITUR NUMERIK / PERTANYAAN 3
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📏 Karakteristik Fitur Numerik (Pertanyaan 3)</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">Pesan phishing memiliki <b>jumlah angka lebih banyak</b>, <b>rasio huruf kapital lebih tinggi</b>, dan <b>panjang pesan yang lebih bervariasi</b>. Fitur-fitur ini memberikan sinyal kuat untuk klasifikasi.</div>', unsafe_allow_html=True)

# Tabel perbandingan fitur numerik
fitur_num_available = [f for f in FITUR_NUMERIK if f in filtered_df.columns]

rows_num = []
for fitur in fitur_num_available:
    label_display = LABEL_DISPLAY.get(fitur, fitur)
    avg_spam = round(spam_df[fitur].mean(), 3) if not spam_df.empty else 0
    avg_ham  = round(ham_df[fitur].mean(),  3) if not ham_df.empty  else 0
    diff_pct = round(((avg_spam - avg_ham) / avg_ham * 100), 1) if avg_ham != 0 else 0
    rows_num.append({
        "Fitur": label_display.replace('\n', ' '),
        "Rata-rata Spam": avg_spam,
        "Rata-rata Ham":  avg_ham,
        "Spam lebih tinggi (%)": diff_pct
    })

df_num = pd.DataFrame(rows_num)
st.dataframe(
    df_num.style.background_gradient(subset=["Rata-rata Spam"], cmap="Reds")
               .background_gradient(subset=["Rata-rata Ham"],  cmap="Blues")
               .format({"Spam lebih tinggi (%)": "{:+.1f}%"}),
    use_container_width=True,
    hide_index=True
)

# Visualisasi 3 fitur utama
fitur_vis = [(f, LABEL_DISPLAY.get(f, f)) for f in ["panjang_pesan","jumlah_angka","rasio_huruf_kapital"]
             if f in filtered_df.columns]

if fitur_vis and not spam_df.empty and not ham_df.empty:
    fig3, axes3 = plt.subplots(1, 3, figsize=(16, 5))
    fig3.patch.set_facecolor('#F5F7FA')

    for idx, (fitur, judul) in enumerate(fitur_vis):
        ax = axes3[idx]
        # Batasi outlier untuk visualisasi lebih jelas
        q95 = filtered_df[fitur].quantile(0.95)
        spam_p = spam_df[spam_df[fitur] <= q95][fitur]
        ham_p  = ham_df[ham_df[fitur]   <= q95][fitur]

        if not ham_p.empty:
            ax.hist(ham_p,  bins=35, alpha=0.7, color=COLOR_HAM,  label='Ham (Normal)')
        if not spam_p.empty:
            ax.hist(spam_p, bins=35, alpha=0.7, color=COLOR_SPAM, label='Spam/Phishing')

        ax.set_title(judul.replace('\n', ' '), fontsize=12, fontweight='bold')
        ax.set_xlabel(judul.replace('\n', ' '))
        ax.set_ylabel('Frekuensi')
        ax.legend(fontsize=9)
        ax.spines[['top','right']].set_visible(False)
        ax.set_facecolor('#F5F7FA')
        ax.grid(axis='y', linestyle='--', alpha=0.35)

    plt.suptitle('Pertanyaan 3: Distribusi Fitur Numerik — Spam vs Ham',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig3)

# Rata-rata per kelas — bar chart
if fitur_vis and not spam_df.empty and not ham_df.empty:
    fig3b, axes3b = plt.subplots(1, 3, figsize=(16, 4))
    fig3b.patch.set_facecolor('#F5F7FA')

    for idx, (fitur, judul) in enumerate(fitur_vis):
        ax = axes3b[idx]
        means = [ham_df[fitur].mean(), spam_df[fitur].mean()]
        bars  = ax.bar(['Ham', 'Spam'], means, color=[COLOR_HAM, COLOR_SPAM],
                       width=0.5, edgecolor='white', linewidth=2)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + max(means)*0.02,
                    f'{bar.get_height():.2f}',
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
        ax.set_title(f'Rata-rata {judul.replace(chr(10), " ")}', fontsize=12, fontweight='bold')
        ax.set_ylabel('Nilai Rata-rata')
        ax.spines[['top','right']].set_visible(False)
        ax.set_facecolor('#F5F7FA')
        ax.grid(axis='y', linestyle='--', alpha=0.35)

    plt.suptitle('Perbandingan Rata-rata Fitur Numerik per Kelas',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig3b)

st.markdown("""
<div class="insight-box">
<b>💡 Insight — Pertanyaan 3:</b><br>
Pesan phishing memiliki <b>jumlah angka lebih banyak</b> (nominal uang, nomor rekening, kode OTP),
<b>rasio huruf kapital lebih tinggi</b> (memberi kesan mendesak dan menarik perhatian),
dan panjang pesan yang lebih bervariasi. Ketiga fitur ini <b>dapat dimanfaatkan langsung</b> sebagai fitur klasifikasi dalam model ML.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 4 — INDIKATOR PHISHING / PERTANYAAN 4
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">⚠️ Kemunculan Indikator Phishing (Pertanyaan 4)</div>', unsafe_allow_html=True)
st.markdown('<div class="section-desc">Persentase pesan yang mengandung masing-masing indikator phishing. Indikator seperti <b>kata sensitif</b> (OTP, PIN, rekening), <b>kata mendesak</b>, dan <b>URL</b> muncul jauh lebih dominan pada pesan spam dibandingkan pesan normal.</div>', unsafe_allow_html=True)

fitur_ind_available = [f for f in FITUR_INDIKATOR if f in filtered_df.columns]

if fitur_ind_available and not spam_df.empty and not ham_df.empty:
    ham_pct  = [(ham_df[f].mean()  * 100) if f in ham_df.columns  else 0 for f in fitur_ind_available]
    spam_pct = [(spam_df[f].mean() * 100) if f in spam_df.columns else 0 for f in fitur_ind_available]
    x_labels = [LABEL_DISPLAY.get(f, f) for f in fitur_ind_available]

    x = np.arange(len(fitur_ind_available))
    width = 0.35

    fig4, ax4 = plt.subplots(figsize=(14, 6))
    fig4.patch.set_facecolor('#F5F7FA')
    ax4.set_facecolor('#F5F7FA')

    bars_h_4 = ax4.bar(x - width/2, ham_pct,  width, label='Ham (Normal)',      color=COLOR_HAM,  alpha=0.9, edgecolor='white')
    bars_s_4 = ax4.bar(x + width/2, spam_pct, width, label='Spam / Phishing',   color=COLOR_SPAM, alpha=0.9, edgecolor='white')

    for bars, col in [(bars_h_4, COLOR_HAM), (bars_s_4, COLOR_SPAM)]:
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax4.text(bar.get_x() + bar.get_width()/2,
                         h + 0.8, f'{h:.0f}%',
                         ha='center', va='bottom', fontsize=9,
                         fontweight='bold', color=col)

    ax4.set_xticks(x)
    ax4.set_xticklabels(x_labels, fontsize=10)
    ax4.set_ylabel('Persentase Pesan yang Mengandung Indikator (%)')
    ax4.set_ylim(0, max(spam_pct + ham_pct) * 1.22 if spam_pct or ham_pct else 100)
    ax4.legend(fontsize=11)
    ax4.spines[['top','right']].set_visible(False)
    ax4.yaxis.grid(True, linestyle='--', alpha=0.4)
    ax4.set_title('Pertanyaan 4: Persentase Kemunculan Indikator Phishing pada Spam vs Ham',
                  fontsize=13, fontweight='bold', pad=14)

    plt.tight_layout()
    st.pyplot(fig4)

    # Tabel indikator
    rows_ind = []
    for fitur, hp, sp in zip(fitur_ind_available, ham_pct, spam_pct):
        rows_ind.append({
            "Indikator": LABEL_DISPLAY.get(fitur, fitur).replace('\n', ' '),
            "Ham (%)":   round(hp, 1),
            "Spam (%)":  round(sp, 1),
            "Selisih (Spam - Ham) %": round(sp - hp, 1)
        })
    df_ind = pd.DataFrame(rows_ind).sort_values("Selisih (Spam - Ham) %", ascending=False)
    st.dataframe(
        df_ind.style.background_gradient(subset=["Selisih (Spam - Ham) %"], cmap="OrRd"),
        use_container_width=True, hide_index=True
    )

st.markdown("""
<div class="insight-box">
<b>💡 Insight — Pertanyaan 4:</b><br>
<b>Kata sensitif</b> (OTP/PIN/password/rekening), <b>kata mendesak</b> (segera/urgent/berakhir),
<b>URL</b>, dan <b>nomor telepon</b> muncul secara signifikan lebih sering pada pesan phishing.
Indikator-indikator ini merupakan <b>sinyal kuat deteksi phishing</b> dan sangat disarankan
dijadikan fitur prioritas dalam model klasifikasi.
<br><br>
<b>Catatan:</b> Domain <code>.id</code> saja tidak cukup kuat sebagai indikator utama spam
karena banyak pesan ham Indonesia juga menggunakan domain tersebut.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 5 — KESIMPULAN & REKOMENDASI
# ═══════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🎯 Kesimpulan & Rekomendasi Action Item</div>', unsafe_allow_html=True)

col_k1, col_k2 = st.columns(2)
with col_k1:
    st.markdown("""
    <div class="q-box">
        <div class="q-num">Kesimpulan 1 — Distribusi Data</div>
        <div class="q-text">Ham lebih banyak dari Spam dengan rasio ~1.5:1. Cukup seimbang — masih aman untuk training tanpa resampling, namun evaluasi dengan F1-score tetap diperlukan.</div>
    </div>
    <div class="q-box">
        <div class="q-num">Kesimpulan 2 — Pola Kata</div>
        <div class="q-text">Pesan phishing menggunakan kata promosi & urgensi ("gratis", "uang", "klik", "OTP"). Pola ini sangat berbeda dari pesan normal yang menggunakan vocabulary netral sehari-hari.</div>
    </div>
    """, unsafe_allow_html=True)
with col_k2:
    st.markdown("""
    <div class="q-box">
        <div class="q-num">Kesimpulan 3 — Fitur Numerik</div>
        <div class="q-text">Spam memiliki jumlah angka lebih banyak, rasio huruf kapital lebih tinggi, dan panjang pesan lebih bervariasi. Ketiga fitur ini signifikan untuk klasifikasi.</div>
    </div>
    <div class="q-box">
        <div class="q-num">Kesimpulan 4 — Indikator Phishing</div>
        <div class="q-text">Kata sensitif, kata mendesak, URL, dan nomor telepon adalah indikator terkuat phishing. Domain ".id" tidak cukup kuat berdiri sendiri sebagai indikator spam.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 🚀 Rekomendasi Action Item")
st.success("""
1. **Gabungkan TF-IDF + Fitur Manual** — Kombinasi fitur TF-IDF (pola kata) dengan fitur manual (panjang pesan, jumlah angka, rasio huruf kapital, URL, nomor telepon, kata sensitif) memberi informasi paling lengkap untuk model klasifikasi.

2. **Prioritaskan Fitur Indikator Tinggi** — Kata sensitif (OTP/PIN/rekening), kata mendesak, dan keberadaan URL adalah indikator dengan perbedaan Spam vs Ham terbesar — gunakan sebagai fitur utama.

3. **Evaluasi dengan F1-score & Recall** — Meski imbalance ringan, gunakan metrik ini agar model tidak bias ke kelas Ham. Recall untuk kelas Spam lebih penting agar phishing tidak lolos.

4. **Jangan andalkan domain '.id' sebagai sinyal utama** — Banyak pesan normal Indonesia juga menggunakan domain tersebut; kurang diskriminatif.
""")

# Footer
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption("Dashboard AwasLink | Capstone Project Data Scientist | Analisis Deteksi Pesan Spam & Phishing Indonesia")