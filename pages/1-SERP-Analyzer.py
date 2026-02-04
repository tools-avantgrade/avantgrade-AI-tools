import streamlit as st
import requests
import pandas as pd
from io import BytesIO
from urllib.parse import urlparse
import plotly.express as px
import plotly.graph_objects as go

# =========================
# CONFIG PAGINA
# =========================
st.set_page_config(
    page_title="SERP Analyzer PRO (DataForSEO) - Avantgrade",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# CSS (il tuo dark)
# =========================
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg, #000000 0%, #1a0a00 100%); }
    .main { background-color: #000000; }
    h1,h2,h3,h4,h5,h6,p,label,.stMarkdown { color: #ffffff !important; }
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white; font-weight: bold; border-radius: 10px;
        padding: 0.75rem 2rem; border: none; width: 100%;
        font-size: 1.1em; box-shadow: 0 4px 8px rgba(255, 107, 53, 0.3);
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
# UTILS
# =========================
def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except:
        return ""

def create_excel_export(df, query):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Risultati Completi', index=False)

        stats_df = pd.DataFrame({
            'Metrica': ['Totale Risultati', 'Domini Unici', 'Query'],
            'Valore': [len(df), df['Dominio'].nunique(), query]
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
        title="Lunghezza Title per Posizione (SOLO ORGANIC)",
        xaxis_title="Posizione",
        yaxis_title="Lunghezza Title (caratteri)",
        template="plotly_dark",
        plot_bgcolor="#000000",
        paper_bgcolor="#000000",
        font=dict(color="#ffffff")
    )
    return fig

def create_domain_chart(df):
    domain_counts = df['Dominio'].value_counts().head(10)
    fig = px.bar(
        x=domain_counts.values,
        y=domain_counts.index,
        orientation='h',
        labels={'x': 'Numero Risultati', 'y': 'Dominio'},
        title="Top 10 Domini (SOLO ORGANIC)"
    )
    fig.update_layout(template="plotly_dark", plot_bgcolor="#000000", paper_bgcolor="#000000", font=dict(color="#ffffff"))
    return fig

# =========================
# DATAFORSEO CALL
# =========================
def dataforseo_google_organic_top100(
    keyword: str,
    login: str,
    password: str,
    language_code: str = "it",
    location_name: str = "Italy",
    device: str = "desktop",
    depth: int = 100
):
    """
    DataForSEO: POST /v3/serp/google/organic/live/advanced
    Ritorna items tipizzati; filtriamo SOLO type == "organic"
    """
    endpoint = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"

    payload = [{
        "keyword": keyword,
        "language_code": language_code,
        "location_name": location_name,
        "device": device,
        "depth": depth
    }]

    r = requests.post(endpoint, json=payload, auth=(login, password), timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")

    data = r.json()

    # error handling DataForSEO
    tasks = data.get("tasks", [])
    if not tasks:
        raise RuntimeError(f"Nessun task nel response: {data}")

    task0 = tasks[0]
    if task0.get("status_code") not in (20000, 20100):
        raise RuntimeError(f"Errore DataForSEO: {task0.get('status_message')} (code {task0.get('status_code')})")

    result = (task0.get("result") or [])
    if not result:
        return []

    items = result[0].get("items", []) or []

    organic = [it for it in items if it.get("type") == "organic"]

    out = []
    for i, it in enumerate(organic, start=1):
        url = it.get("url") or it.get("link") or ""
        title = it.get("title") or "N/A"
        snippet = it.get("description") or it.get("snippet") or "N/A"
        out.append({
            "Posizione": i,
            "URL": url,
            "Title": title,
            "Snippet": snippet,
            "Dominio": extract_domain(url),
            "Lunghezza Title": len(title),
            "Lunghezza Snippet": len(snippet),
        })
        if len(out) >= depth:
            break

    return out

# =========================
# UI
# =========================
st.markdown("""
<div style='background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            padding: 2rem; border-radius: 15px; text-align: center;
            box-shadow: 0 8px 16px rgba(255, 107, 53, 0.3); margin-bottom: 2rem;'>
    <h1 style='margin: 0; font-size: 2.5em; color: white !important;'>🔍 SERP Analyzer PRO</h1>
    <p style='margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.95; color: white !important;'>
        DataForSEO — SOLO Organic Results (Top 100)
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("🔎 Keyword", placeholder="es. gian luca rana")
with col2:
    depth = st.selectbox("📊 Risultati (organic)", [10, 20, 30, 40, 50, 60, 70, 80, 90, 100], index=9)

col3, col4, col5 = st.columns(3)
with col3:
    language_code = st.selectbox("🗣️ language_code", ["it", "en", "fr", "de", "es"], index=0)
with col4:
    location_name = st.text_input("📍 location_name", value="Italy", help="Esempi: Italy / Milan, Italy / Rome, Italy")
with col5:
    device = st.selectbox("📱 Device", ["desktop", "mobile"], index=0)

col6, col7 = st.columns(2)
with col6:
    dfs_login = st.text_input("🔐 DataForSEO Login", value="", type="password")
with col7:
    dfs_password = st.text_input("🔐 DataForSEO Password", value="", type="password")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 ESTRAI TOP 100 ORGANIC", use_container_width=True):
    if not query.strip():
        st.error("⚠️ Inserisci una keyword!")
    elif not dfs_login.strip() or not dfs_password.strip():
        st.error("⚠️ Inserisci login/password DataForSEO!")
    else:
        with st.spinner("Estrazione in corso..."):
            try:
                rows = dataforseo_google_organic_top100(
                    keyword=query.strip(),
                    login=dfs_login.strip(),
                    password=dfs_password.strip(),
                    language_code=language_code,
                    location_name=location_name.strip(),
                    device=device,
                    depth=depth
                )
                st.session_state["results"] = rows
                st.session_state["query"] = query.strip()
            except Exception as e:
                st.error(f"❌ Errore: {e}")

# =========================
# RISULTATI
# =========================
if st.session_state.get("results"):
    df = pd.DataFrame(st.session_state["results"])

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

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Risultati", "📊 Grafici", "📥 Export", "📝 Raw Data"])

    with tab1:
        st.info(f"📊 **{len(df)} risultati ORGANIC** per: *{st.session_state['query']}*")
        all_urls = "\n".join(df["URL"].tolist())
        col_a, col_b = st.columns(2)
        with col_a:
            st.text_area("📋 Copia URL", all_urls, height=180)
        with col_b:
            st.download_button("📥 TXT", all_urls, f"urls_organic_{st.session_state['query'].replace(' ','_')}.txt", "text/plain", use_container_width=True)
            st.download_button("📊 CSV", df.to_csv(index=False).encode("utf-8"),
                               f"serp_organic_{st.session_state['query'].replace(' ','_')}.csv",
                               "text/csv", use_container_width=True)

        st.markdown("---")
        for _, row in df.iterrows():
            st.markdown(f"""
            <div class='url-box'>
                <strong style='color: #FF6B35; font-size: 1.2em;'>#{row['Posizione']}</strong><br>
                <strong style='color: #4da6ff; font-size: 1.1em;'>{row['Title']}</strong><br>
                <a href='{row['URL']}' target='_blank' style='color: #00cc66; text-decoration: none;'>{row['URL']}</a><br>
                <p style='color: #cccccc; margin-top: 0.5rem;'>{row['Snippet']}</p>
                <small style='color: #999;'>🌐 {row['Dominio']}</small>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.plotly_chart(create_position_chart(df), use_container_width=True)
        st.plotly_chart(create_domain_chart(df), use_container_width=True)

    with tab3:
        excel_file = create_excel_export(df, st.session_state["query"])
        st.download_button("📊 Scarica Excel", excel_file,
                           f"serp_organic_{st.session_state['query'].replace(' ','_')}.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)

    with tab4:
        st.dataframe(df, use_container_width=True, height=520)

st.markdown("---")
st.markdown("<p style='text-align:center; color:#999;'>SERP Analyzer PRO — DataForSEO (solo organic)</p>", unsafe_allow_html=True)
