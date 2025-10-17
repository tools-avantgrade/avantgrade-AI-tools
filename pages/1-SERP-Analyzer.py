import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# Configurazione pagina
st.set_page_config(
    page_title="SERP Analyzer Pro - Avantgrade",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Dark Theme
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #000000 0%, #1a0a00 100%);
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
    .metric-card {
        background: #1a1a1a;
        border: 2px solid #FF6B35;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
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
    """Estrae URL e metadati da Google usando SerpAPI"""
    results_data = []
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
            
            for idx, result in enumerate(risultati, start=start+1):
                link = result.get("link", "")
                title = result.get("title", "N/A")
                snippet = result.get("snippet", "N/A")
                
                # Estrai dominio
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(link).netloc
                except:
                    domain = "N/A"
                
                results_data.append({
                    "Posizione": idx,
                    "URL": link,
                    "Title": title,
                    "Snippet": snippet,
                    "Dominio": domain,
                    "Lunghezza Title": len(title),
                    "Lunghezza Snippet": len(snippet)
                })
            
            if page_num < total_pages - 1 and len(results_data) < num_results:
                time.sleep(1)
            
            if len(results_data) >= num_results:
                break
                
        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")
            break
    
    progress_bar.progress(1.0)
    status_text.success(f"✅ Estrazione completata! {len(results_data)} risultati trovati")
    
    return results_data[:num_results]

def create_excel_export(df, query):
    """Crea un file Excel con formattazione avanzata"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Foglio principale con tutti i dati
        df.to_excel(writer, sheet_name='Risultati Completi', index=False)
        
        # Foglio con statistiche
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
        
        # Foglio con analisi domini
        domain_counts = df['Dominio'].value_counts().reset_index()
        domain_counts.columns = ['Dominio', 'Occorrenze']
        domain_counts.to_excel(writer, sheet_name='Analisi Domini', index=False)
    
    output.seek(0)
    return output

def create_position_chart(df):
    """Crea grafico distribuzione posizioni"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Posizione'],
        y=df['Lunghezza Title'],
        mode='markers',
        marker=dict(
            size=10,
            color=df['Posizione'],
            colorscale=[[0, '#FF6B35'], [1, '#F7931E']],
            showscale=True,
            colorbar=dict(title="Posizione")
        ),
        text=df['Dominio'],
        hovertemplate='<b>Posizione:</b> %{x}<br><b>Lunghezza Title:</b> %{y}<br><b>Dominio:</b> %{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Lunghezza Title per Posizione SERP",
        xaxis_title="Posizione",
        yaxis_title="Lunghezza Title (caratteri)",
        template="plotly_dark",
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#ffffff')
    )
    
    return fig

def create_domain_chart(df):
    """Crea grafico domini più presenti"""
    domain_counts = df['Dominio'].value_counts().head(10)
    
    fig = px.bar(
        x=domain_counts.values,
        y=domain_counts.index,
        orientation='h',
        labels={'x': 'Numero di Risultati', 'y': 'Dominio'},
        title="Top 10 Domini nella SERP"
    )
    
    fig.update_traces(marker_color='#FF6B35')
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#ffffff')
    )
    
    return fig

def create_length_distribution(df):
    """Crea grafico distribuzione lunghezze"""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['Lunghezza Title'],
        name='Title',
        marker_color='#FF6B35',
        opacity=0.7
    ))
    
    fig.add_trace(go.Histogram(
        x=df['Lunghezza Snippet'],
        name='Snippet',
        marker_color='#F7931E',
        opacity=0.7
    ))
    
    fig.update_layout(
        title="Distribuzione Lunghezze Title e Snippet",
        xaxis_title="Lunghezza (caratteri)",
        yaxis_title="Frequenza",
        barmode='overlay',
        template="plotly_dark",
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#ffffff')
    )
    
    return fig

# Header
st.markdown("""
<div style='background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); 
            padding: 2rem; border-radius: 15px; text-align: center; 
            box-shadow: 0 8px 16px rgba(255, 107, 53, 0.3); margin-bottom: 2rem;'>
    <h1 style='margin: 0; font-size: 2.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); color: white !important;'>
        🔍 SERP Analyzer PRO
    </h1>
    <p style='margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.95; color: white !important;'>
        Analisi Avanzata SERP con Grafici e Export Excel
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
    query = st.text_input("🔎 Query di ricerca", placeholder="es. migliori smartphone 2025")
with col2:
    num_results = st.selectbox("📊 Risultati", [10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

col3, col4 = st.columns(2)
with col3:
    paese_sel = st.selectbox("🌍 Paese", list(paesi.keys()))
with col4:
    api_key = st.text_input("🔑 API Key", value="", type="password", placeholder="Inserisci la tua API key")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 ANALIZZA SERP", use_container_width=True):
    if not query.strip():
        st.error("⚠️ Inserisci una query di ricerca!")
    elif not api_key.strip():
        st.error("⚠️ Inserisci la tua API key SerpAPI!")
    else:
        paese_info = paesi[paese_sel]
        with st.spinner("Estrazione e analisi in corso..."):
            results = estrai_url_con_serpapi(query, num_results, paese_info['lang'], paese_info['code'], api_key)
        
        if results:
            st.session_state['results'] = results
            st.session_state['query'] = query
            st.session_state['paese'] = paese_info['code']

# Risultati
if 'results' in st.session_state and st.session_state['results']:
    df = pd.DataFrame(st.session_state['results'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Statistiche principali
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{len(df)}</h3><p style='margin:0; color:white;'>Risultati</p></div>", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{df['Dominio'].nunique()}</h3><p style='margin:0; color:white;'>Domini Unici</p></div>", unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{df['Lunghezza Title'].mean():.0f}</h3><p style='margin:0; color:white;'>Media Title</p></div>", unsafe_allow_html=True)
    with col_s4:
        st.markdown(f"<div class='stats-box'><h3 style='margin:0; color:white;'>{df['Lunghezza Snippet'].mean():.0f}</h3><p style='margin:0; color:white;'>Media Snippet</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Risultati", "📊 Grafici", "🎯 Analisi", "📥 Export", "📝 Raw Data"])
    
    with tab1:
        st.markdown("### 🎯 Risultati SERP Completi")
        
        all_urls = "\n".join(df['URL'].tolist())
        
        # Header con info
        st.info(f"📊 **{len(df)} URL estratti** dalla query: *{st.session_state['query']}*")
        
        # Tab per copia
        col_copy1, col_copy2 = st.columns(2)
        
        with col_copy1:
            # Text area per copia manuale
            st.text_area(
                "📋 Seleziona e Copia (Ctrl+A → Ctrl+C)",
                all_urls,
                height=150
            )
        
        with col_copy2:
            st.markdown("### 💾 Oppure Scarica")
            
            # Download TXT
            st.download_button(
                "📥 Scarica TXT",
                all_urls,
                f"urls_{st.session_state['query'].replace(' ', '_')}.txt",
                "text/plain",
                use_container_width=True
            )
            
            # Download CSV (solo URL)
            urls_csv = "URL\n" + "\n".join(df['URL'].tolist())
            st.download_button(
                "📊 Scarica CSV",
                urls_csv,
                f"urls_{st.session_state['query'].replace(' ', '_')}.csv",
                "text/csv",
                use_container_width=True
            )
            
            st.markdown("""
            <div style='background: #1a1a1a; padding: 1rem; border-radius: 8px; 
                        border-left: 4px solid #00cc66; margin-top: 1rem;'>
                <small style='color: #00cc66;'>
                    💡 <strong>Tip:</strong> Usa Ctrl+A per selezionare tutto, 
                    poi Ctrl+C per copiare!
                </small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Lista risultati completi
        st.markdown("### 📋 Dettaglio Risultati")
        
        for idx, row in df.iterrows():
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
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.plotly_chart(create_domain_chart(df), use_container_width=True)
        with col_g2:
            st.plotly_chart(create_length_distribution(df), use_container_width=True)
    
    with tab3:
        st.markdown("### 🎯 Analisi Dettagliata")
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            st.markdown("""
            <div class='metric-card'>
                <h3 style='color: #FF6B35;'>📏 Lunghezze Medie</h3>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Title medio", f"{df['Lunghezza Title'].mean():.1f} caratteri")
            st.metric("Snippet medio", f"{df['Lunghezza Snippet'].mean():.1f} caratteri")
            st.metric("Title più lungo", f"{df['Lunghezza Title'].max()} caratteri")
            st.metric("Title più corto", f"{df['Lunghezza Title'].min()} caratteri")
        
        with col_a2:
            st.markdown("""
            <div class='metric-card'>
                <h3 style='color: #FF6B35;'>🌐 Analisi Domini</h3>
            </div>
            """, unsafe_allow_html=True)
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
        
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Scarica CSV",
                csv,
                f"serp_analysis_{st.session_state['query'].replace(' ', '_')}.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col_d2:
            excel_file = create_excel_export(df, st.session_state['query'])
            st.download_button(
                "📊 Scarica Excel Avanzato",
                excel_file,
                f"serp_analysis_{st.session_state['query'].replace(' ', '_')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_d3:
            txt = "\n\n".join([f"#{row['Posizione']} - {row['Title']}\n{row['URL']}\n{row['Snippet']}" for idx, row in df.iterrows()])
            st.download_button(
                "📝 Scarica TXT",
                txt,
                f"serp_analysis_{st.session_state['query'].replace(' ', '_')}.txt",
                "text/plain",
                use_container_width=True
            )
    
    with tab5:
        st.markdown("### 📊 Tabella Dati Completa")
        st.dataframe(df, use_container_width=True, height=500)

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
    
    ---
    
    **✨ Nuove Funzionalità:**
    - 📊 Export Excel con statistiche multiple
    - 📈 Grafici interattivi per analisi visiva
    - 🎯 Analisi dettagliata title, snippet e domini
    - 📏 Metriche di lunghezza media
    - 🌐 Analisi distribuzione domini
    - 📋 Copia rapida URL con text area
    """)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #999;'>🔍 SERP Analyzer PRO - Powered by Avantgrade Tools</p>", unsafe_allow_html=True)