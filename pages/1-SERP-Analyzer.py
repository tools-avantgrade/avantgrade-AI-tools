import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from urllib.parse import urlparse

# =========================
# CONFIGURAZIONE PAGINA
# =========================
st.set_page_config(
    page_title="SERP Analyzer Pro - Avantgrade",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# CSS Dark Theme
# =========================
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #000000 0%, #1a0a00 100%); }
    .main { background-color: #000000; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: #ffffff !important; }
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white; font-weight: bold; border-radius: 10px;
        padding: 0.75rem 2rem; border: none; width: 100%;
        font-size: 1.1em;
        box-shadow: 0 4px 8px rgba(255, 107, 53, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(255, 107, 53, 0.5); }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #1a1a1a !important; color: #ffffff !important;
        border: 1px solid #FF6B35 !important; border-radius: 8px;
    }
    .url-box {
        background: #1a1a1a; border-left: 4px solid #FF6B35;
        padding: 1rem; margin: 0.5rem 0; border-radius: 8px;
        color: #ffffff; transition: all 0.3s ease;
    }
    .url-box:hover { background: #2a2a2a; transform: translateX(5px); }
    .stats-box {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white; padding: 1.5rem; border-radius: 12px; text-align: center;
        font-weight: bold; box-shadow: 0 4px 8px rgba(255, 107, 53, 0.4);
    }
    .metric-card { background: #1a1a1a; border: 2px solid #FF6B35; border-radius: 12px; padding: 1.5rem; margin: 0.5rem 0; }
    div[data-testid="stExpander"] { background-color: #1a1a1a; border: 1px solid #FF6B35; border-radius: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; color: #FF6B35; border-radius: 8px 8px 0 0; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); color: white; }
    [data-testid="stTextArea"] textarea { background-color: #1a1a1a !important; color: #ffffff !important; border: 1px solid #FF6B35 !important; }
    </style>
""", unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
def extract_domain(link: str) -> str:
    try:
        return urlparse(link).netloc.lower()
    except:
        return ""

def create_excel_export(df, query):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Risultati Completi', index=False)

        stats_df = pd.DataFrame({
            'Metrica': [
                'Totale Risultati',
                'Lunghezza Media Title',
                'Lunghezza Media Snippet',
                'Domini Unici',
                'Query Analizzata'
            ],
            'Valore': [
                len(df),
                f"{df['Lunghezza Title'].mean():.1f} caratteri",
                f"{df['Lunghezza Snippet'].mean():.1f} caratteri",
                df['Dominio'].nunique(),
                query
            ]
        })
        stats_df.to_excel(writer, sheet_name='Statistiche', index=False)

        domain_counts = df['Dominio'].value_counts().reset_index()
        domain_counts.columns = ['Dominio', 'Occorrenze']
        domain_counts.to_excel(writer, sheet_name='Analisi Domini', index=False)

    output.seek(0)
    return output

def create_position_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Posizione'],
        y=df['Lunghezza Title'],
        mode='markers',
        text=df['Dominio'],
        hovertemplate='<b>Posizione:</b> %{x}<br><b>Lunghezza Title:</b> %{y}<br><b>Dominio:</b> %{text}<extra></extra>'
    ))
    fig.update_layout(
        title="Lunghezza Title per Posizione (solo ORGANIC)",
        xaxis_title="Posizione",
        yaxis_title="Lunghezza Title (caratteri)",
        template="plotly_dark",
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#ffffff')
    )
    return fig

def create_domain_chart(df):
    domain_counts = df['Dominio'].value_counts().head(10)
    fig = px.bar(
        x=domain_counts.values,
        y=domain_counts.index,
        orientation='h',
        labels={'x': 'Numero di Risultati', 'y': 'Dominio'},
        title="Top 10 Domini (solo ORGANIC)"
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#ffffff')
    )
    return fig

def create_length_distribution(df):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df['Lunghezza Title'], name='Title', opacity=0.7))
    fig.add_trace(go.Histogram(x=df['Lunghezza Snippet'], name='Snippet', opacity=0.7))
    fig.update_layout(
        title="Distribuzione lunghezze Title/Snippet (solo ORGANIC)",
        xaxis_title="Lunghezza (caratteri)",
        yaxis_title="Frequenza",
        barmode='overlay',
        template="plotly_dark",
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#ffffff')
    )
    return fig

# =========================
# ESTRAZIONE SERP - SOLO ORGANIC
# =========================
def estrai_solo_organic_serpapi(
    query: str,
    num_results: int,
    api_key: str,
    google_domain: str,
    hl: str,
    gl: str,
    location: str,
    device: str = "desktop",
    pause_seconds: float = 0.35,
    max_pages: int = 30
):
    """
    Estrae SOLO data["organic_results"] paginando start=0,10,20...
    Continua anche se una pagina ha <10, finché raggiunge num_results o termina.
    """
    results_data = []
    seen_urls = set()

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

    progress_bar = st.progress(0)
    status_text = st.empty()

    start = 0
    page_num = 1
    empty_pages = 0

    # log debug per capire cosa succede davvero
    debug_lines = []

    while len(results_data) < num_results and page_num <= max_pages:
        progress_bar.progress(min(len(results_data) / num_results, 0.95))
        status_text.markdown(f"**🔄 Pagina {page_num} (start={start}) — {len(results_data)}/{num_results} organic**")

        params = {
            "engine": "google",
            "q": query,
            "google_domain": google_domain,  # es: google.it
            "hl": hl,                        # es: it
            "gl": gl,                        # es: it
            "location": location,            # es: Italy oppure Milan, Italy
            "device": device,                # desktop / mobile
            "num": 10,
            "start": start,
            # utili: riduce personalizzazione e autocorrezioni
            "pws": 0,
            "nfpr": 1,
            "api_key": api_key
        }

        try:
            r = session.get("https://serpapi.com/search.json", params=params, timeout=45)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
            data = r.json()
            if "error" in data:
                raise RuntimeError(data["error"])

            organic = data.get("organic_results", []) or []
            debug_lines.append(f"Pagina {page_num}: organic_results = {len(organic)} (start={start})")

            # se non ci sono organic, conta come pagina "vuota"
            if len(organic) == 0:
                empty_pages += 1
                if empty_pages >= 2:
                    break
            else:
                empty_pages = 0

            for res in organic:
                if len(results_data) >= num_results:
                    break
                link = res.get("link", "")
                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)

                title = res.get("title", "N/A")
                snippet = res.get("snippet", "N/A")
                domain = extract_domain(link)

                results_data.append({
                    "Posizione": len(results_data) + 1,
                    "URL": link,
                    "Title": title,
                    "Snippet": snippet,
                    "Dominio": domain,
                    "Lunghezza Title": len(title),
                    "Lunghezza Snippet": len(snippet)
                })

            # prossima pagina
            start += 10
            page_num += 1
            time.sleep(pause_seconds)

        except Exception as e:
            st.error(f"❌ Errore SerpAPI: {e}")
            break

    progress_bar.progress(1.0)

    # mostra debug
    with st.expander("🧪 Debug paginazione (organic_results per pagina)"):
        st.code("\n".join(debug_lines) if debug_lines else "Nessun log")

    if len(results_data) < num_results:
        status_text.warning(f"⚠️ Estrazione completata: {len(results_data)} organic su {page_num-1} pagine")
        st.info(
            "Se Google ti mostra più risultati organici rispetto a SerpAPI, è normale in alcuni casi: "
            "Google cambia layout/feature e SerpAPI non sempre classifica tutto come 'organic_results'. "
            "Qui però stai prendendo SOLO gli organic, senza inquinare con knowledge_graph o video block."
        )
    else:
        status_text.success(f"✅ Estrazione completata! {len(results_data)} organic")

    return results_data[:num_results]

# =========================
# HEADER
# =========================
st.markdown("""
<div style='background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); 
            padding: 2rem; border-radius: 15px; text-align: center; 
            box-shadow: 0 8px 16px rgba(255, 107, 53, 0.3); margin-bottom: 2rem;'>
    <h1 style='margin: 0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); color: white !important;'>
        🔍 SERP Analyzer PRO
    </h1>
    <p style='margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.95; color: white !important;'>
        Estrazione SOLO Organic Results (paginazione automatica)
    </p>
</div>
""", unsafe_allow_html=True)

# =========================
# FORM
# =========================
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("🔎 Query di ricerca", placeholder="es. gian luca rana")
with col2:
    num_results = st.selectbox("📊 Risultati (organic)", [10, 20, 30, 40, 50, 60, 70, 80, 90, 100], index=9)

col3, col4, col5 = st.columns(3)
with col3:
    google_domain = st.selectbox("🌐 Google domain", ["google.it", "google.com"], index=0)
with col4:
    device = st.selectbox("📱 Device", ["desktop", "mobile"], index=0)
with col5:
    api_key = st.text_input("🔑 API Key SerpAPI", value="", type="password", placeholder="Inserisci la tua API key")

col6, col7, col8 = st.columns(3)
with col6:
    hl = st.selectbox("🗣️ hl (lingua)", ["it", "en", "fr", "de", "es"], index=0)
with col7:
    gl = st.selectbox("🧭 gl (paese)", ["it", "us", "gb", "de", "fr", "es"], index=0)
with col8:
    location = st.text_input("📍 location (SerpAPI)", value="Italy", help="Esempi: Italy / Milan, Italy / Rome, Italy")

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# BUTTON
# =========================
if st.button("🚀 ANALIZZA SERP (solo ORGANIC)", use_container_width=True):
    if not query.strip():
        st.error("⚠️ Inserisci una query di ricerca!")
    elif not api_key.strip():
        st.error("⚠️ Inserisci la tua API key SerpAPI!")
    else:
        with st.spinner("Estrazione organic in corso..."):
            results = estrai_solo_organic_serpapi(
                query=query.strip(),
                num_results=num_results,
                api_key=api_key.strip(),
                google_domain=google_domain,
                hl=hl,
                gl=gl,
                location=location.strip(),
                device=device
            )

        if results:
            st.session_state['results'] = results
            st.session_state['query'] = query.strip()

# =========================
# RESULTS
# =========================
if 'results' in st.session_state and st.session_state['results']:
    df = pd.DataFrame(st.session_state['results'])

    st.markdown("<br>", unsafe_allow_html=True)

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{len(df)}</h3><p style='margin:0; color:white;'>Organic</p></div>", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{df['Dominio'].nunique()}</h3><p style='margin:0; color:white;'>Domini Unici</p></div>", unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{df['Lunghezza Title'].mean():.0f}</h3><p style='margin:0; color:white;'>Media Title</p></div>", unsafe_allow_html=True)
    with col_s4:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{df['Lunghezza Snippet'].mean():.0f}</h3><p style='margin:0; color:white;'>Media Snippet</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Risultati", "📊 Grafici", "🎯 Analisi", "📥 Export", "📝 Raw Data"])

    with tab1:
        st.markdown("### 🎯 Organic Results (solo)")
        all_urls = "\n".join(df['URL'].tolist())
        st.info(f"📊 **{len(df)} URL organic estratti** per: *{st.session_state['query']}*")

        col_copy1, col_copy2 = st.columns(2)
        with col_copy1:
            st.text_area("📋 Seleziona e Copia (Ctrl+A → Ctrl+C)", all_urls, height=150)
        with col_copy2:
            st.markdown("### 💾 Scarica")
            st.download_button("📥 Scarica TXT", all_urls, f"urls_organic_{st.session_state['query'].replace(' ', '_')}.txt", "text/plain", use_container_width=True)
            urls_csv = "URL\n" + "\n".join(df['URL'].tolist())
            st.download_button("📊 Scarica CSV", urls_csv, f"urls_organic_{st.session_state['query'].replace(' ', '_')}.csv", "text/csv", use_container_width=True)

        st.markdown("---")
        st.markdown("### 📋 Dettaglio risultati")
        for _, row in df.iterrows():
            st.markdown(f"""
            <div class='url-box'>
                <strong style='color: #FF6B35; font-size: 1.2em;'>#{row['Posizione']}</strong><br>
                <strong style='color: #4da6ff; font-size: 1.1em;'>{row['Title']}</strong><br>
                <a href='{row['URL']}' target='_blank' style='color: #00cc66; text-decoration: none;'>{row['URL']}</a><br>
                <p style='color: #cccccc; margin-top: 0.5rem;'>{row['Snippet']}</p>
                <small style='color: #999;'>📏 Title: {row['Lunghezza Title']} char | Snippet: {row['Lunghezza Snippet']} char | 🌐 {row['Dominio']}</small>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 📊 Visualizzazioni")
        st.plotly_chart(create_position_chart(df), use_container_width=True)
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.plotly_chart(create_domain_chart(df), use_container_width=True)
        with col_g2:
            st.plotly_chart(create_length_distribution(df), use_container_width=True)

    with tab3:
        st.markdown("### 🎯 Analisi Dettagliata")
        col_a1, col_a2 = st.columns(2)

        with col_a1:
            st.markdown("<div class='metric-card'><h3 style='color: #FF6B35;'>📏 Lunghezze</h3></div>", unsafe_allow_html=True)
            st.metric("Title medio", f"{df['Lunghezza Title'].mean():.1f} caratteri")
            st.metric("Snippet medio", f"{df['Lunghezza Snippet'].mean():.1f} caratteri")
            st.metric("Title più lungo", f"{df['Lunghezza Title'].max()} caratteri")
            st.metric("Title più corto", f"{df['Lunghezza Title'].min()} caratteri")

        with col_a2:
            st.markdown("<div class='metric-card'><h3 style='color: #FF6B35;'>🌐 Domini</h3></div>", unsafe_allow_html=True)
            st.metric("Domini unici", df['Dominio'].nunique())
            st.metric("Dominio più presente", df['Dominio'].mode()[0] if not df['Dominio'].mode().empty else "N/A")
            st.metric("Max occorrenze stesso dominio", df['Dominio'].value_counts().max())

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🏆 Top 10 Domini")
        domain_table = df['Dominio'].value_counts().head(10).reset_index()
        domain_table.columns = ['Dominio', 'Occorrenze']
        st.dataframe(domain_table, use_container_width=True)

    with tab4:
        st.markdown("### 📥 Export")
        col_d1, col_d2, col_d3 = st.columns(3)

        with col_d1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica CSV", csv, f"serp_organic_{st.session_state['query'].replace(' ', '_')}.csv", "text/csv", use_container_width=True)

        with col_d2:
            excel_file = create_excel_export(df, st.session_state['query'])
            st.download_button("📊 Scarica Excel", excel_file, f"serp_organic_{st.session_state['query'].replace(' ', '_')}.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        with col_d3:
            txt = "\n\n".join([f"#{row['Posizione']} - {row['Title']}\n{row['URL']}\n{row['Snippet']}" for _, row in df.iterrows()])
            st.download_button("📝 Scarica TXT", txt, f"serp_organic_{st.session_state['query'].replace(' ', '_')}.txt", "text/plain", use_container_width=True)

    with tab5:
        st.markdown("### 📊 Tabella Completa")
        st.dataframe(df, use_container_width=True, height=500)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999;'>🔍 SERP Analyzer PRO - SOLO Organic Results via SerpAPI</p>", unsafe_allow_html=True)
