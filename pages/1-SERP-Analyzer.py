import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from urllib.parse import urlparse

# =========================
# CONFIG + THEME
# =========================
st.set_page_config(
    page_title="SERP Analyzer Pro - Avantgrade",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #000000 0%, #1a0a00 100%); }
    .Usb { background-color: #000000; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: #ffffff !important; }
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white; font-weight: bold; border-radius: 10px; padding: 0.75rem 2rem;
        border: none; width: 100%; font-size: 1.1em;
        box-shadow: 0 4px 8px rgba(255, 107, 53, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(255, 107, 53, 0.5); }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #1a1a1a !important; color: #ffffff !important;
        border: 1px solid #FF6B35 !important; border-radius: 8px;
    }
    .url-box {
        background: #1a1a1a; border-left: 4px solid #FF6B35; padding: 1rem;
        margin: 0.5rem 0; border-radius: 8px; color: #ffffff; transition: all 0.3s ease;
    }
    .url-box:hover { background: #2a2a2a; transform: translateX(5px); }
    .stats-box {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white; padding: 1.5rem; border-radius: 12px; text-align: center; font-weight: bold;
        box-shadow: 0 4px 8px rgba(255, 107, 53, 0.4);
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

def serpapi_request(session: requests.Session, params: dict) -> dict:
    r = session.get("https://serpapi.com/search.json", params=params, timeout=45)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:250]}")
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"SerpAPI error: {data['error']}")
    return data

def serpapi_request_direct(session: requests.Session, url: str, api_key: str) -> dict:
    # pixel_position_endpoint spesso NON include api_key: la aggiungiamo
    sep = "&" if "?" in url else "?"
    url_with_key = f"{url}{sep}api_key={api_key}"
    r = session.get(url_with_key, timeout=45)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:250]}")
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"SerpAPI error: {data['error']}")
    return data

def flatten_serp_by_pixel_position(data_with_pixel: dict):
    """
    Estrae elementi cliccabili da più blocchi e li ordina per pixel_position (Y).
    Questo è il modo più vicino a una SERP "1:1" in ordine visivo.
    """
    items = []

    def add_item(block_name: str, obj: dict):
        link = obj.get("link") or obj.get("serpapi_link") or ""
        title = obj.get("title") or obj.get("question") or obj.get("source") or block_name
        snippet = obj.get("snippet") or obj.get("description") or obj.get("text") or ""

        pp = obj.get("pixel_position", None)
        if isinstance(pp, dict):
            pp_val = pp.get("y", None)
        else:
            pp_val = pp

        items.append({
            "block": block_name,
            "pixel_position": pp_val if pp_val is not None else 10**12,
            "link": link,
            "title": title,
            "snippet": snippet,
            "domain": extract_domain(link),
            "raw_position": obj.get("position", None)
        })

    # Scansiona top-level: liste
    for key, value in data_with_pixel.items():
        if isinstance(value, list):
            for obj in value:
                if isinstance(obj, dict) and (obj.get("link") or obj.get("serpapi_link")):
                    add_item(key, obj)

        # Scansiona dict annidati (es: knowledge_graph.web_results)
        elif isinstance(value, dict):
            for subk, subv in value.items():
                if isinstance(subv, list):
                    for obj in subv:
                        if isinstance(obj, dict) and (obj.get("link") or obj.get("serpapi_link")):
                            add_item(f"{key}.{subk}", obj)

    items.sort(key=lambda x: x["pixel_position"])
    return items

def estrai_serp_google_1to1_serpapi(
    query: str,
    num_results: int,
    api_key: str,
    google_domain: str,
    hl: str,
    gl: str,
    location: str,
    device: str = "desktop",
    pause_seconds: float = 0.35,
    max_pages: int = 20
):
    """
    Paginazione start=0,10,20... e ricostruzione SERP 1:1 usando pixel_position_endpoint.
    Restituisce elementi di qualunque tipo (organic/video/news/etc.) nell’ordine visivo.
    """
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

    results = []
    start = 0
    page = 1
    empty_pages = 0

    progress = st.progress(0)
    status = st.empty()

    while len(results) < num_results and page <= max_pages:
        progress.progress(min(len(results) / num_results, 0.95))
        status.markdown(f"**🔄 Pagina {page} (start={start}) — {len(results)}/{num_results}**")

        params = {
            "engine": "google",
            "q": query,
            "google_domain": google_domain,
            "hl": hl,
            "gl": gl,
            "location": location,
            "device": device,
            "num": 10,
            "start": start,
            # utili per ridurre "correzioni" e personalizzazione
            "pws": 0,
            "nfpr": 1,
            "api_key": api_key
        }

        try:
            data = serpapi_request(session, params)
        except Exception as e:
            st.error(f"❌ Errore SerpAPI (pagina {page}): {e}")
            break

        pixel_url = (data.get("search_metadata") or {}).get("pixel_position_endpoint")

        if not pixel_url:
            # fallback minimo
            organic = data.get("organic_results", []) or []
            st.caption(f"Pagina {page}: pixel_position_endpoint non disponibile, organic_results={len(organic)}")
            if not organic:
                empty_pages += 1
                if empty_pages >= 2:
                    break
            else:
                empty_pages = 0
                for obj in organic:
                    if len(results) >= num_results:
                        break
                    link = obj.get("link", "")
                    results.append({
                        "Posizione": len(results) + 1,
                        "Tipo": "organic_results",
                        "URL": link,
                        "Title": obj.get("title", "N/A"),
                        "Snippet": obj.get("snippet", "N/A"),
                        "Dominio": extract_domain(link),
                        "PixelY": None
                    })
            start += 10
            page += 1
            time.sleep(pause_seconds)
            continue

        try:
            data_px = serpapi_request_direct(session, pixel_url, api_key)
        except Exception as e:
            st.error(f"❌ Errore pixel_position_endpoint (pagina {page}): {e}")
            break

        items = flatten_serp_by_pixel_position(data_px)
        st.caption(f"Pagina {page}: elementi cliccabili (ordinabili per pixel) = {len(items)}")

        if not items:
            empty_pages += 1
            if empty_pages >= 2:
                break
        else:
            empty_pages = 0
            for it in items:
                if len(results) >= num_results:
                    break
                results.append({
                    "Posizione": len(results) + 1,
                    "Tipo": it["block"],
                    "URL": it["link"],
                    "Title": it["title"],
                    "Snippet": it["snippet"],
                    "Dominio": it["domain"],
                    "PixelY": it["pixel_position"]
                })

        start += 10
        page += 1
        time.sleep(pause_seconds)

    progress.progress(1.0)

    if len(results) < num_results:
        st.warning(f"⚠️ Estratti {len(results)} elementi (richiesti {num_results}).")
        st.info(
            "Nota: la SERP che vedi nel browser può differire per geolocalizzazione precisa, lingua browser, cookie/login, test A/B. "
            "Questa è la ricostruzione 1:1 più vicina che SerpAPI consente usando pixel_position."
        )
    else:
        st.success(f"✅ Estratti {len(results)} elementi")

    return results[:num_results]

# =========================
# EXPORT + CHARTS
# =========================
def create_excel_export(df, query):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Risultati Completi', index=False)

        stats_df = pd.DataFrame({
            'Metrica': [
                'Totale Risultati',
                'Domini Unici',
                'Query Analizzata'
            ],
            'Valore': [
                len(df),
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
    # usa PixelY se presente, altrimenti Posizione
    xcol = "PixelY" if "PixelY" in df.columns and df["PixelY"].notna().any() else "Posizione"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[xcol],
        y=df['Posizione'],
        mode='markers',
        text=df['Dominio'],
        hovertemplate=f"<b>{xcol}:</b> %{{x}}<br><b>Posizione:</b> %{{y}}<br><b>Dominio:</b> %{{text}}<extra></extra>"
    ))
    fig.update_layout(
        title="Distribuzione risultati (ordine visivo vs posizione)",
        xaxis_title=xcol,
        yaxis_title="Posizione (output)",
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
        title="Top 10 Domini nella SERP"
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#ffffff')
    )
    return fig

# =========================
# UI
# =========================
st.markdown("""
<div style='background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); 
            padding: 2rem; border-radius: 15px; text-align: center; 
            box-shadow: 0 8px 16px rgba(255, 107, 53, 0.3); margin-bottom: 2rem;'>
    <h1 style='margin: 0; font-size: 2.5em; color: white !important;'>
        🔍 SERP Analyzer PRO
    </h1>
    <p style='margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.95; color: white !important;'>
        SERP 1:1 (ordine visivo) via SerpAPI pixel_position_endpoint
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("🔎 Query di ricerca", placeholder="es. gian luca rana")
with col2:
    num_results = st.selectbox("📊 Elementi da estrarre", [10,20,30,40,50,60,70,80,90,100], index=9)

col3, col4, col5 = st.columns(3)
with col3:
    google_domain = st.selectbox("🌐 Google domain", ["google.it", "google.com"], index=0)
with col4:
    device = st.selectbox("📱 Device", ["desktop", "mobile"], index=0)
with col5:
    hl = st.selectbox("🗣️ hl (lingua)", ["it", "en", "fr", "de", "es"], index=0)

col6, col7, col8 = st.columns(3)
with col6:
    gl = st.selectbox("🧭 gl (paese)", ["it", "us", "gb", "de", "fr", "es"], index=0)
with col7:
    location = st.text_input("📍 location (SerpAPI)", value="Italy", help="Esempi: Italy, Milan, Italy / Rome, Italy / United States / Zurich, Switzerland")
with col8:
    api_key = st.text_input("🔑 API Key SerpAPI", value="", type="password", placeholder="Inserisci la tua API key")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 ANALIZZA SERP", use_container_width=True):
    if not query.strip():
        st.error("⚠️ Inserisci una query di ricerca!")
    elif not api_key.strip():
        st.error("⚠️ Inserisci la tua API key SerpAPI!")
    else:
        with st.spinner("Estrazione SERP (1:1) in corso..."):
            results = estrai_serp_google_1to1_serpapi(
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
# RESULTS VIEW
# =========================
if 'results' in st.session_state and st.session_state['results']:
    df = pd.DataFrame(st.session_state['results'])

    st.markdown("<br>", unsafe_allow_html=True)

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{len(df)}</h3><p style='margin:0; color:white;'>Elementi</p></div>", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{df['Dominio'].nunique()}</h3><p style='margin:0; color:white;'>Domini Unici</p></div>", unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{df['Tipo'].nunique()}</h3><p style='margin:0; color:white;'>Tipi di blocco</p></div>", unsafe_allow_html=True)
    with col_s4:
        non_null_pix = int(df["PixelY"].notna().sum()) if "PixelY" in df.columns else 0
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{non_null_pix}</h3><p style='margin:0; color:white;'>Con PixelY</p></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Risultati", "📊 Grafici", "📥 Export", "📝 Raw Data"])

    with tab1:
        st.markdown("### 🎯 SERP (ordine visivo)")
        all_urls = "\n".join([u for u in df["URL"].tolist() if isinstance(u, str) and u.strip()])
        st.info(f"📊 **{len(df)} elementi estratti** per: *{st.session_state['query']}*")

        col_copy1, col_copy2 = st.columns(2)
        with col_copy1:
            st.text_area("📋 Seleziona e Copia (Ctrl+A → Ctrl+C)", all_urls, height=150)
        with col_copy2:
            st.markdown("### 💾 Scarica")
            st.download_button("📥 TXT (solo URL)", all_urls, f"urls_{st.session_state['query'].replace(' ', '_')}.txt", "text/plain", use_container_width=True)
            urls_csv = "URL\n" + "\n".join([u for u in df["URL"].tolist() if isinstance(u, str)])
            st.download_button("📊 CSV (solo URL)", urls_csv, f"urls_{st.session_state['query'].replace(' ', '_')}.csv", "text/csv", use_container_width=True)

        st.markdown("---")
        st.markdown("### 📋 Dettaglio elementi")
        for _, row in df.iterrows():
            url = row.get("URL", "")
            title = row.get("Title", "N/A")
            snippet = row.get("Snippet", "N/A")
            tipo = row.get("Tipo", "N/A")
            dom = row.get("Dominio", "")
            pix = row.get("PixelY", None)

            st.markdown(f"""
            <div class='url-box'>
                <strong style='color: #FF6B35; font-size: 1.1em;'>#{row['Posizione']} — {tipo}</strong><br>
                <strong style='color: #4da6ff; font-size: 1.05em;'>{title}</strong><br>
                <a href='{url}' target='_blank' style='color: #00cc66; text-decoration: none;'>{url}</a><br>
                <p style='color: #cccccc; margin-top: 0.5rem;'>{snippet}</p>
                <small style='color: #999;'>🌐 {dom} | PixelY: {pix}</small>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 📊 Grafici")
        st.plotly_chart(create_position_chart(df), use_container_width=True)
        st.plotly_chart(create_domain_chart(df), use_container_width=True)

    with tab3:
        st.markdown("### 📥 Export")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Scarica CSV completo",
                csv,
                f"serp_1to1_{st.session_state['query'].replace(' ', '_')}.csv",
                "text/csv",
                use_container_width=True
            )
        with col_d2:
            excel_file = create_excel_export(df, st.session_state['query'])
            st.download_button(
                "📊 Scarica Excel",
                excel_file,
                f"serp_1to1_{st.session_state['query'].replace(' ', '_')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    with tab4:
        st.markdown("### 📝 Raw Data")
        st.dataframe(df, use_container_width=True, height=500)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("<p style='text-align: center; color: #999;'>🔍 SERP Analyzer PRO - 1:1 SERP via SerpAPI pixel_position_endpoint</p>", unsafe_allow_html=True)
