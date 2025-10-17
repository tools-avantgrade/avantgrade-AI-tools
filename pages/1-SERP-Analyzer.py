import streamlit as st
import requests
import time
import pandas as pd

# Configurazione pagina
st.set_page_config(
    page_title="100 SerpGrade Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Dark Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
    }
    .main {
        background-color: #000000;
    }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #ffffff !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        border: none;
        width: 100%;
        font-size: 1.1em;
        box-shadow: 0 4px 8px rgba(255, 107, 53, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255, 107, 53, 0.5);
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #FF6B35 !important;
        border-radius: 8px;
    }
    .url-box {
        background: #1a1a1a;
        border-left: 4px solid #FF6B35;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        color: #ffffff;
        transition: all 0.3s ease;
    }
    .url-box:hover {
        background: #2a2a2a;
        transform: translateX(5px);
    }
    .stats-box {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(255, 107, 53, 0.4);
    }
    div[data-testid="stExpander"] {
        background-color: #1a1a1a;
        border: 1px solid #FF6B35;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a;
        color: #FF6B35;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white;
    }
    [data-testid="stTextArea"] textarea {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #FF6B35 !important;
    }
    </style>
""", unsafe_allow_html=True)

def estrai_url_con_serpapi(query, num_results=100, lingua='it', geolocalizzazione='IT', api_key=''):
    """Estrae URL da Google usando SerpAPI"""
    urls = []
    risultati_per_pagina = 10
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_pages = (num_results + risultati_per_pagina - 1) // risultati_per_pagina
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    for page_num in range(total_pages):
        start = page_num * risultati_per_pagina
        progress = (page_num + 1) / total_pages
        progress_bar.progress(progress)
        status_text.markdown(f"**🔄 Estrazione in corso... Pagina {page_num + 1}/{total_pages}**")
        
        params = {
            "engine": "google",
            "q": query,
            "hl": lingua,
            "gl": geolocalizzazione,
            "num": risultati_per_pagina,
            "start": start,
            "api_key": api_key
        }
        
        try:
            response = session.get("https://serpapi.com/search", params=params, timeout=30)
            
            if response.status_code != 200:
                st.error(f"❌ Errore HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        st.error(f"Dettaglio: {error_data['error']}")
                except:
                    pass
                break
            
            data = response.json()
            
            if 'error' in data:
                st.error(f"❌ Errore API: {data['error']}")
                break
            
            risultati = data.get("organic_results", [])
            
            if not risultati:
                break
            
            for result in risultati:
                link = result.get("link")
                if link and link not in urls:
                    urls.append(link)
            
            if page_num < total_pages - 1 and len(urls) < num_results:
                time.sleep(1)
            
            if len(urls) >= num_results:
                break
                
        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")
            break
    
    progress_bar.progress(1.0)
    status_text.success(f"✅ Estrazione completata! {len(urls)} URL trovati")
    
    return urls[:num_results]

# Header
st.markdown("""
<div style='background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); 
            padding: 2rem; border-radius: 15px; text-align: center; 
            box-shadow: 0 8px 16px rgba(255, 107, 53, 0.3); margin-bottom: 2rem;'>
    <h1 style='margin: 0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
        🔍 100 SerpGrade Analyzer
    </h1>
    <p style='margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.95;'>
        Estrai fino a 100 URL organici da Google con SerpAPI
    </p>
</div>
""", unsafe_allow_html=True)

# Paesi
paesi = {
    "Italia 🇮🇹": {"code": "IT", "lang": "it"},
    "Spagna 🇪🇸": {"code": "ES", "lang": "es"},
    "Francia 🇫🇷": {"code": "FR", "lang": "fr"},
    "UK 🇬🇧": {"code": "GB", "lang": "en"},
    "Germania 🇩🇪": {"code": "DE", "lang": "de"},
    "USA 🇺🇸": {"code": "US", "lang": "en"}
}

# Form
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("🔎 Query di ricerca", placeholder="es. gianluca rana")
with col2:
    num_results = st.selectbox("📊 Risultati", [10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

col3, col4 = st.columns(2)
with col3:
    paese_sel = st.selectbox("🌍 Paese", list(paesi.keys()))
with col4:
    api_key = st.text_input("🔑 API Key", value="", type="password", placeholder="Inserisci la tua API key")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 ESTRAI URL", use_container_width=True):
    if not query.strip():
        st.error("⚠️ Inserisci una query di ricerca!")
    elif not api_key.strip():
        st.error("⚠️ Inserisci la tua API key SerpAPI!")
    else:
        paese_info = paesi[paese_sel]
        with st.spinner("Estrazione in corso..."):
            urls = estrai_url_con_serpapi(query, num_results, paese_info['lang'], paese_info['code'], api_key)
        
        if urls:
            st.session_state['urls'] = urls
            st.session_state['query'] = query
            st.session_state['paese'] = paese_info['code']

# Risultati
if 'urls' in st.session_state and st.session_state['urls']:
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{len(st.session_state['urls'])}</h3><p style='margin:0; color:white;'>URL Trovati</p></div>", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{st.session_state['query']}</h3><p style='margin:0; color:white;'>Query</p></div>", unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{st.session_state.get('paese', 'IT')}</h3><p style='margin:0; color:white;'>Paese</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista URL", "📊 Tabella", "💾 Esporta"])
    
    with tab1:
        st.markdown("### URL Estratti")
        for idx, url in enumerate(st.session_state['urls'], 1):
            st.markdown(f"""<div class='url-box'><strong style='color: #FF6B35;'>{idx}.</strong> <a href='{url}' target='_blank' style='color: #4da6ff; text-decoration: none;'>{url}</a></div>""", unsafe_allow_html=True)
    
    with tab2:
        df = pd.DataFrame({'N°': range(1, len(st.session_state['urls']) + 1), 'URL': st.session_state['urls']})
        st.dataframe(df, use_container_width=True, height=500)
    
    with tab3:
        st.markdown("### Esporta i Risultati")
        
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Scarica CSV", 
                csv, 
                f"serp_{st.session_state['query'].replace(' ', '_')}.csv", 
                "text/csv", 
                use_container_width=True
            )
        
        with col_d2:
            txt = "\n".join(st.session_state['urls'])
            st.download_button(
                "📥 Scarica TXT", 
                txt, 
                f"serp_{st.session_state['query'].replace(' ', '_')}.txt", 
                "text/plain", 
                use_container_width=True
            )
        
        st.markdown("### Copia tutto")
        st.text_area("", txt, height=200)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("ℹ️ Come ottenere una API Key gratuita di SerpAPI"):
    st.markdown("""
    **Passaggi per ottenere la tua API key:**
    
    1. Vai su **https://serpapi.com/**
    2. Clicca su **"Register"** per creare un account
    3. Completa la registrazione (è gratuito!)
    4. Una volta loggato, vai nel **Dashboard**
    5. Troverai la tua **API key** nella sezione principale
    6. Copiala e incollala nel campo "API Key" qui sopra
    
    **Piano gratuito:** 100 ricerche al mese
    """)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #999;'>🔍 100 SerpGrade Analyzer - Powered by SerpAPI</p>", unsafe_allow_html=True)
