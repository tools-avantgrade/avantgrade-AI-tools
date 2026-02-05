import streamlit as st
import requests
import time
import pandas as pd
from urllib.parse import urlparse
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64

# ----------------------------
# PAGE CONFIG + CSS
# ----------------------------
st.set_page_config(
    page_title="SERP Analyzer Pro - Avantgrade",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #000000 0%, #1a0a00 100%); }
    .main { background-color: #000000; }
    h1,h2,h3,h4,h5,h6,p,label,.stMarkdown { color:#ffffff !important; }
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white; font-weight: bold; border-radius: 10px;
        padding: 0.75rem 2rem; border: none; width: 100%;
        font-size: 1.1em; box-shadow: 0 4px 8px rgba(255,107,53,0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(255,107,53,0.5); }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #1a1a1a !important; color:#ffffff !important;
        border: 1px solid #FF6B35 !important; border-radius: 8px;
    }
    .url-box {
        background:#1a1a1a; border-left:4px solid #FF6B35;
        padding:1rem; margin:0.5rem 0; border-radius:8px;
        color:#ffffff; transition: all 0.3s ease;
    }
    .url-box:hover { background:#2a2a2a; transform: translateX(5px); }
    .stats-box {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color:white; padding:1.5rem; border-radius:12px;
        text-align:center; font-weight:bold;
        box-shadow:0 4px 8px rgba(255,107,53,0.4);
    }
    .metric-card {
        background:#1a1a1a; border:2px solid #FF6B35;
        border-radius:12px; padding:1.5rem; margin:0.5rem 0;
    }
    div[data-testid="stExpander"] { background:#1a1a1a; border:1px solid #FF6B35; border-radius:10px; }
    .stTabs [data-baseweb="tab-list"] { gap:10px; }
    .stTabs [data-baseweb="tab"] {
        background:#1a1a1a; color:#FF6B35; border-radius:8px 8px 0 0;
        padding:10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color:white;
    }
    [data-testid="stTextArea"] textarea {
        background:#1a1a1a !important; color:#ffffff !important;
        border:1px solid #FF6B35 !important;
    }
    </style>
""", unsafe_allow_html=True)


# ----------------------------
# DATAFORSEO HELPERS
# ----------------------------
# Codici paese ISO 3166-1 alpha-2 corretti per Google
PAESI = {
    "Italia 🇮🇹": {"gl": "it", "hl": "it", "location_code": 2380, "language_code": "it", "se_domain": "google.it"},
    "Spagna 🇪🇸": {"gl": "es", "hl": "es", "location_code": 2724, "language_code": "es", "se_domain": "google.es"},
    "Francia 🇫🇷": {"gl": "fr", "hl": "fr", "location_code": 2250, "language_code": "fr", "se_domain": "google.fr"},
    "UK 🇬🇧": {"gl": "gb", "hl": "en", "location_code": 2826, "language_code": "en", "se_domain": "google.co.uk"},
    "Germania 🇩🇪": {"gl": "de", "hl": "de", "location_code": 2276, "language_code": "de", "se_domain": "google.de"},
    "USA 🇺🇸": {"gl": "us", "hl": "en", "location_code": 2840, "language_code": "en", "se_domain": "google.com"},
}

def _basic_auth_header(login: str, password: str) -> str:
    token = base64.b64encode(f"{login}:{password}".encode("utf-8")).decode("utf-8")
    return f"Basic {token}"

def fetch_google_organic_100_dataforseo(
    keyword: str,
    login: str,
    password: str,
    location_code: int,
    language_code: str,
    se_domain: str,
    gl: str,
    hl: str,
    device: str = "desktop",
    target_results: int = 100,
    sleep_s: float = 0.3
):
    """
    Estrae fino a target_results ORGANIC (solo type=='organic') paginando con start=0,10,20...
    Usa LIVE ADVANCED per avere items con vari tipi, ma poi filtra esclusivamente organic.
    """
    endpoint = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
    session = requests.Session()
    session.headers.update({
        "Authorization": _basic_auth_header(login, password),
        "Content-Type": "application/json"
    })

    results = []
    seen = set()

    progress_bar = st.progress(0)
    status = st.empty()

    start = 0
    page = 1
    no_new_pages = 0
    max_pages = 30  # 30 pagine = 300 posizioni (ampio margine)

    while len(results) < target_results and page <= max_pages:
        progress_bar.progress(min(len(results) / target_results, 0.95))
        status.markdown(f"**🔄 Pagina {page} (start={start}) — Organic raccolti: {len(results)}/{target_results}**")

        # Parametri Google per ridurre differenze col browser:
        # pws=0 (personalization off), nfpr=1 (no auto-correct / no filter), num=10
        search_param = f"num=10&start={start}&pws=0&nfpr=1&hl={hl}&gl={gl}"

        payload = [{
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "se_domain": se_domain,
            "device": device,
            "search_param": search_param,
            "depth": 10  # prendiamo 10 per pagina, come Google
        }]

        try:
            r = session.post(endpoint, json=payload, timeout=60)
            if r.status_code != 200:
                status.error(f"❌ HTTP {r.status_code}: {r.text[:300]}")
                break

            data = r.json()
            if data.get("status_code") != 20000:
                status.error(f"❌ DataForSEO error: {data.get('status_message')}")
                break

            task = (data.get("tasks") or [{}])[0]
            task_result = (task.get("result") or [{}])[0]

            # Qui c'è la "pagina" completa con tanti item (organic, paa, kg, ecc.)
            items = task_result.get("items") or []
            organic_items = [it for it in items if it.get("type") == "organic"]

            new_this_page = 0
            for it in organic_items:
                url = it.get("url") or it.get("link") or ""
                title = it.get("title") or "N/A"
                snippet = it.get("description") or it.get("snippet") or "N/A"

                if not url or url in seen:
                    continue

                seen.add(url)
                try:
                    domain = urlparse(url).netloc.lower()
                except:
                    domain = ""

                results.append({
                    "Posizione": len(results) + 1,
                    "URL": url,
                    "Title": title,
                    "Snippet": snippet,
                    "Dominio": domain,
                    "Lunghezza Title": len(title),
                    "Lunghezza Snippet": len(snippet),
                })
                new_this_page += 1

                if len(results) >= target_results:
                    break

            # Se per 2 pagine consecutive non troviamo nuovi organic, probabilmente la SERP è finita o sta "collassando"
            if new_this_page == 0:
                no_new_pages += 1
                if no_new_pages >= 2:
                    break
            else:
                no_new_pages = 0

            # prossima pagina
            start += 10
            page += 1
            time.sleep(sleep_s)

        except requests.exceptions.Timeout:
            status.warning(f"⚠️ Timeout su pagina {page}. Ritento andando avanti...")
            start += 10
            page += 1
            time.sleep(1.0)
        except Exception as e:
            status.error(f"❌ Errore: {str(e)}")
            break

    progress_bar.progress(1.0)

    if len(results) < target_results:
        status.warning(f"⚠️ Finito: trovati {len(results)} risultati ORGANIC. (Google/risposta API non ne ha restituiti di più)")
    else:
        status.success(f"✅ OK: trovati {len(results)} risultati ORGANIC")

    return results


# ----------------------------
# EXPORT + CHARTS (tuoi)
# ----------------------------
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
                f"{df['Lunghezza Title'].mean():.1f} caratteri" if len(df) else "0",
                f"{df['Lunghezza Snippet'].mean():.1f} caratteri" if len(df) else "0",
                df['Dominio'].nunique() if len(df) else 0,
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
        marker=dict(size=10, color=df['Posizione'], showscale=True, colorbar=dict(title="Posizione")),
        text=df['Dominio'],
        hovertemplate='<b>Posizione:</b> %{x}<br><b>Lunghezza Title:</b> %{y}<br><b>Dominio:</b> %{text}<extra></extra>'
    ))
    fig.update_layout(
        title="Lunghezza Title per Posizione SERP (solo Organic)",
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
        title="Top 10 Domini nella SERP (solo Organic)"
    )
    fig.update_layout(template="plotly_dark", plot_bgcolor='#000000', paper_bgcolor='#000000', font=dict(color='#ffffff'))
    return fig

def create_length_distribution(df):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df['Lunghezza Title'], name='Title', opacity=0.7))
    fig.add_trace(go.Histogram(x=df['Lunghezza Snippet'], name='Snippet', opacity=0.7))
    fig.update_layout(
        title="Distribuzione Lunghezze Title e Snippet (solo Organic)",
        xaxis_title="Lunghezza (caratteri)",
        yaxis_title="Frequenza",
        barmode='overlay',
        template="plotly_dark",
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#ffffff')
    )
    return fig


# ----------------------------
# UI
# ----------------------------
st.markdown("""
<div style='background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            padding: 2rem; border-radius: 15px; text-align: center;
            box-shadow: 0 8px 16px rgba(255, 107, 53, 0.3); margin-bottom: 2rem;'>
    <h1 style='margin: 0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); color: white !important;'>
        🔍 SERP Analyzer PRO
    </h1>
    <p style='margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.95; color: white !important;'>
        Analisi SERP Google (DataForSEO) — SOLO Organic
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("🔎 Query di ricerca", placeholder="es. gian luca rana")
with col2:
    num_results = st.selectbox("📊 Risultati (Organic)", [10, 20, 30, 40, 50, 60, 70, 80, 90, 100], index=9)

col3, col4 = st.columns(2)
with col3:
    paese_sel = st.selectbox("🌍 Paese", list(PAESI.keys()), index=0)
with col4:
    device = st.selectbox("📱 Device", ["desktop", "mobile"], index=0)

st.markdown("### 🔐 Credenziali DataForSEO")
c5, c6 = st.columns(2)
with c5:
    dfs_login = st.text_input("Login (DataForSEO)", value="", placeholder="email o login DataForSEO")
with c6:
    dfs_password = st.text_input("Password (DataForSEO)", value="", type="password", placeholder="password DataForSEO")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 ANALIZZA SERP (SOLO ORGANIC)", use_container_width=True):
    if not query.strip():
        st.error("⚠️ Inserisci una query di ricerca!")
    elif not dfs_login.strip() or not dfs_password.strip():
        st.error("⚠️ Inserisci login e password DataForSEO!")
    else:
        info = PAESI[paese_sel]
        with st.spinner("Estrazione SERP (organic) in corso..."):
            results = fetch_google_organic_100_dataforseo(
                keyword=query.strip(),
                login=dfs_login.strip(),
                password=dfs_password.strip(),
                location_code=info["location_code"],
                language_code=info["language_code"],
                se_domain=info["se_domain"],
                gl=info["gl"],
                hl=info["hl"],
                device=device,
                target_results=int(num_results),
            )

        st.session_state['results'] = results
        st.session_state['query'] = query.strip()
        st.session_state['paese'] = paese_sel

# ----------------------------
# RESULTS
# ----------------------------
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
        st.markdown("### 🎯 Risultati SERP — SOLO Organic")
        all_urls = "\n".join(df['URL'].tolist())
        st.info(f"📊 **{len(df)} URL (organic)** estratti dalla query: *{st.session_state['query']}*")

        c1, c2 = st.columns(2)
        with c1:
            st.text_area("📋 Seleziona e Copia (Ctrl+A → Ctrl+C)", all_urls, height=150)
        with c2:
            st.markdown("### 💾 Scarica")
            st.download_button("📥 Scarica TXT", all_urls, f"urls_{st.session_state['query'].replace(' ', '_')}.txt", "text/plain", use_container_width=True)
            urls_csv = "URL\n" + "\n".join(df['URL'].tolist())
            st.download_button("📊 Scarica CSV", urls_csv, f"urls_{st.session_state['query'].replace(' ', '_')}.csv", "text/csv", use_container_width=True)

        st.markdown("---")
        st.markdown("### 📋 Dettaglio Risultati")
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
        st.markdown("### 📊 Visualizzazioni Grafiche")
        st.plotly_chart(create_position_chart(df), use_container_width=True)
        cg1, cg2 = st.columns(2)
        with cg1:
            st.plotly_chart(create_domain_chart(df), use_container_width=True)
        with cg2:
            st.plotly_chart(create_length_distribution(df), use_container_width=True)

    with tab3:
        st.markdown("### 🎯 Analisi Dettagliata")
        ca1, ca2 = st.columns(2)
        with ca1:
            st.markdown("<div class='metric-card'><h3 style='color:#FF6B35;'>📏 Lunghezze Medie</h3></div>", unsafe_allow_html=True)
            st.metric("Title medio", f"{df['Lunghezza Title'].mean():.1f} caratteri")
            st.metric("Snippet medio", f"{df['Lunghezza Snippet'].mean():.1f} caratteri")
            st.metric("Title più lungo", f"{df['Lunghezza Title'].max()} caratteri")
            st.metric("Title più corto", f"{df['Lunghezza Title'].min()} caratteri")
        with ca2:
            st.markdown("<div class='metric-card'><h3 style='color:#FF6B35;'>🌐 Analisi Domini</h3></div>", unsafe_allow_html=True)
            st.metric("Domini unici", df['Dominio'].nunique())
            st.metric("Dominio più presente", df['Dominio'].mode()[0] if not df['Dominio'].mode().empty else "N/A")
            st.metric("Max occorrenze stesso dominio", df['Dominio'].value_counts().max())

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🏆 Top 10 Domini")
        domain_table = df['Dominio'].value_counts().head(10).reset_index()
        domain_table.columns = ['Dominio', 'Occorrenze']
        st.dataframe(domain_table, use_container_width=True)

    with tab4:
        st.markdown("### 📥 Esporta i Risultati")
        cd1, cd2, cd3 = st.columns(3)
        with cd1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Scarica CSV", csv, f"serp_organic_{st.session_state['query'].replace(' ', '_')}.csv", "text/csv", use_container_width=True)
        with cd2:
            excel_file = create_excel_export(df, st.session_state['query'])
            st.download_button("📊 Scarica Excel", excel_file, f"serp_organic_{st.session_state['query'].replace(' ', '_')}.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with cd3:
            txt = "\n\n".join([f"#{row['Posizione']} - {row['Title']}\n{row['URL']}\n{row['Snippet']}" for _, row in df.iterrows()])
            st.download_button("📝 Scarica TXT", txt, f"serp_organic_{st.session_state['query'].replace(' ', '_')}.txt", "text/plain", use_container_width=True)

    with tab5:
        st.markdown("### 📊 Tabella Dati Completa (SOLO Organic)")
        st.dataframe(df, use_container_width=True, height=500)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #999;'>🔍 SERP Analyzer PRO - DataForSEO (SOLO Organic)</p>", unsafe_allow_html=True)
