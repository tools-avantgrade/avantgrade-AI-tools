import streamlit as st

# Configurazione pagina
st.set_page_config(
    page_title="Avantgrade Tools Suite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato
st.markdown("""
    <style>
    /* Sfondo principale */
    .stApp {
        background: linear-gradient(180deg, #000000 0%, #1a0a00 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d0d 0%, #1a1a1a 100%);
        border-right: 2px solid #FF6B35;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* Main content */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(255, 107, 53, 0.4);
        margin-bottom: 3rem;
    }
    
    .hero-title {
        font-size: 3.5em;
        font-weight: 900;
        margin: 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        color: white !important;
    }
    
    .hero-subtitle {
        font-size: 1.4em;
        margin: 15px 0 0 0;
        opacity: 0.95;
        color: white !important;
    }
    
    /* Tool cards */
    .tool-card {
        background: linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 2px solid #FF6B35;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.2);
        height: 100%;
    }
    
    .tool-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(255, 107, 53, 0.4);
        border-color: #F7931E;
    }
    
    .tool-icon {
        font-size: 3em;
        margin-bottom: 1rem;
    }
    
    .tool-title {
        color: #FF6B35 !important;
        font-size: 1.8em;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .tool-description {
        color: #cccccc !important;
        font-size: 1.1em;
        line-height: 1.6;
    }
    
    .tool-status {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: bold;
        margin-top: 1rem;
    }
    
    .status-active {
        background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
        color: #000;
    }
    
    .status-coming {
        background: linear-gradient(135deg, #666666 0%, #999999 100%);
        color: #fff;
    }
    
    /* Features section */
    .feature-box {
        background: rgba(255, 107, 53, 0.1);
        border-left: 4px solid #FF6B35;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
    }
    
    .feature-box h3 {
        color: #FF6B35 !important;
        margin-top: 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 4rem;
        border-top: 2px solid #FF6B35;
        color: #999999;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        border: none;
        font-size: 1.1em;
        box-shadow: 0 4px 8px rgba(255, 107, 53, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255, 107, 53, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class='hero-section'>
    <h1 class='hero-title'>🚀 AVANTGRADE TOOLS</h1>
    <p class='hero-subtitle'>Suite Professionale di Strumenti SEO & Digital Marketing</p>
</div>
""", unsafe_allow_html=True)

# Introduzione
st.markdown("""
<div style='text-align: center; margin-bottom: 3rem;'>
    <p style='font-size: 1.3em; color: #cccccc; line-height: 1.8;'>
        Benvenuto nella <strong style='color: #FF6B35;'>suite completa</strong> di strumenti professionali<br>
        progettati per potenziare la tua <strong style='color: #F7931E;'>strategia digitale</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# Tools Grid - 3 colonne
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='tool-card'>
        <div class='tool-icon'>🔍</div>
        <h2 class='tool-title'>SERP Analyzer</h2>
        <p class='tool-description'>
            Estrai fino a 100 URL organici da Google per qualsiasi query. 
            Analizza la SERP in tempo reale con dati precisi e aggiornati.
        </p>
        <span class='tool-status status-active'>✓ ATTIVO</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='tool-card'>
        <div class='tool-icon'>📊</div>
        <h2 class='tool-title'>Keyword Research</h2>
        <p class='tool-description'>
            Scopri nuove opportunità di keyword con volumi di ricerca, 
            difficoltà e trend. Analisi competitiva avanzata.
        </p>
        <span class='tool-status status-coming'>⏳ COMING SOON</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='tool-card'>
        <div class='tool-icon'>🤖</div>
        <h2 class='tool-title'>Query Fan-Out</h2>
        <p class='tool-description'>
            Espandi query singole in varianti intelligenti usando Gemini AI. 
            Perfetto per keyword expansion e content planning.
        </p>
        <span class='tool-status status-active'>✓ ATTIVO</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='tool-card'>
        <div class='tool-icon'>🎯</div>
        <h2 class='tool-title'>Content Optimizer</h2>
        <p class='tool-description'>
            Ottimizza i tuoi contenuti con analisi avanzate di readability, 
            keyword density e suggerimenti SEO on-page.
        </p>
        <span class='tool-status status-coming'>⏳ COMING SOON</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='tool-card'>
        <div class='tool-icon'>🕷️</div>
        <h2 class='tool-title'>Competitor Content Analyzer</h2>
        <p class='tool-description'>
            Analizza i tag HTML (title, meta, H1-H3) dai competitor.
            Estrai struttura SEO, immagini e metadata in pochi secondi.
        </p>
        <span class='tool-status status-active'>✓ ATTIVO</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='tool-card'>
        <div class='tool-icon'>🧩</div>
        <h2 class='tool-title'>Keyword Clustering Expert</h2>
        <p class='tool-description'>
            Raggruppa automaticamente le keyword per search intent semantico.
            AI-powered clustering con GPT-5 per strategie di contenuto mirate.
        </p>
        <span class='tool-status status-active'>✓ ATTIVO</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='tool-card'>
        <div class='tool-icon'>🔗</div>
        <h2 class='tool-title'>Backlink Checker</h2>
        <p class='tool-description'>
            Monitora il profilo backlink del tuo sito e dei competitor. 
            Analisi completa di autorità e qualità dei link.
        </p>
        <span class='tool-status status-coming'>⏳ COMING SOON</span>
    </div>
    """, unsafe_allow_html=True)

# Seconda riga tools
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div class='tool-card'>
        <div class='tool-icon'>📈</div>
        <h2 class='tool-title'>Analytics Dashboard</h2>
        <p class='tool-description'>
            Dashboard centralizzata per monitorare performance SEO, 
            traffico organico e conversioni in un unico posto.
        </p>
        <span class='tool-status status-coming'>⏳ COMING SOON</span>
    </div>
    """, unsafe_allow_html=True)

# Features Section
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("## 💎 Caratteristiche Principali")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown("""
    <div class='feature-box'>
        <h3>⚡ Velocità</h3>
        <p style='color: #cccccc;'>Strumenti ottimizzati per risultati rapidi e affidabili</p>
    </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown("""
    <div class='feature-box'>
        <h3>🎯 Precisione</h3>
        <p style='color: #cccccc;'>Dati accurati da fonti certificate e aggiornate</p>
    </div>
    """, unsafe_allow_html=True)

with col_f3:
    st.markdown("""
    <div class='feature-box'>
        <h3>🔒 Sicurezza</h3>
        <p style='color: #cccccc;'>Le tue API key sono protette e mai memorizzate</p>
    </div>
    """, unsafe_allow_html=True)

# Getting Started
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("## 🚀 Come Iniziare")

st.markdown("""
<div style='background: rgba(255, 107, 53, 0.1); padding: 2rem; border-radius: 15px; border: 2px solid #FF6B35;'>
    <ol style='color: #cccccc; font-size: 1.1em; line-height: 2;'>
        <li><strong style='color: #FF6B35;'>Seleziona</strong> uno strumento dalla sidebar a sinistra</li>
        <li><strong style='color: #FF6B35;'>Inserisci</strong> i parametri richiesti (query, API key, ecc.)</li>
        <li><strong style='color: #FF6B35;'>Analizza</strong> i risultati e scarica i dati</li>
        <li><strong style='color: #FF6B35;'>Ottimizza</strong> la tua strategia con insights professionali</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class='footer'>
    <p style='font-size: 1.1em;'>
        🚀 <strong style='color: #FF6B35;'>Avantgrade Tools</strong> - Professional SEO Suite
    </p>
    <p style='font-size: 0.9em; margin-top: 1rem;'>
        Sviluppato con ❤️ per professionisti del Digital Marketing
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar Info
with st.sidebar:
    st.markdown("## 📚 Guida Rapida")
    st.markdown("""
    **Strumenti Attivi:**
    - 🔍 SERP Analyzer
    - 🤖 Query Fan-Out
    - 🕷️ Competitor Content Analyzer
    - 🧩 Keyword Clustering Expert
    
    **Coming Soon:**
    - 📊 Keyword Research
    - 🎯 Content Optimizer
    - 📈 Analytics Dashboard
    - 🔗 Backlink Checker
    
    ---
    
    **Supporto:**
    Per assistenza contatta il team Avantgrade
    """)
