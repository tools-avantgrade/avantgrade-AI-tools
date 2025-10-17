import streamlit as st

st.set_page_config(
    page_title="Keyword Research - Avantgrade",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #000000 0%, #1a0a00 100%);
    }
    h1, h2, h3, p, label {
        color: #ffffff !important;
    }
    .coming-soon-box {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        margin: 3rem 0;
        box-shadow: 0 10px 30px rgba(255, 107, 53, 0.4);
    }
    .feature-preview {
        background: #1a1a1a;
        border: 2px solid #FF6B35;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div class='coming-soon-box'>
    <h1 style='font-size: 3em; margin: 0; color: white !important;'>📊 KEYWORD RESEARCH</h1>
    <p style='font-size: 1.5em; margin: 1rem 0; color: white !important;'>Coming Soon</p>
    <p style='font-size: 1.1em; color: white !important;'>Strumento di ricerca keyword professionale in fase di sviluppo</p>
</div>
""", unsafe_allow_html=True)

st.markdown("## 🎯 Funzionalità in Arrivo")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class='feature-preview'>
        <h3 style='color: #FF6B35;'>🔍 Ricerca Avanzata</h3>
        <ul style='color: #cccccc; font-size: 1.1em;'>
            <li>Volume di ricerca mensile</li>
            <li>Keyword difficulty</li>
            <li>CPC e competitività</li>
            <li>Trend stagionali</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-preview'>
        <h3 style='color: #FF6B35;'>📈 Analisi Competitor</h3>
        <ul style='color: #cccccc; font-size: 1.1em;'>
            <li>Gap analysis</li>
            <li>Keyword comuni</li>
            <li>Opportunità non sfruttate</li>
            <li>Posizionamenti SERP</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-preview'>
        <h3 style='color: #FF6B35;'>💡 Suggerimenti</h3>
        <ul style='color: #cccccc; font-size: 1.1em;'>
            <li>Long-tail keywords</li>
            <li>Question-based queries</li>
            <li>Related searches</li>
            <li>LSI keywords</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-preview'>
        <h3 style='color: #FF6B35;'>📊 Export & Report</h3>
        <ul style='color: #cccccc; font-size: 1.1em;'>
            <li>Export CSV/Excel</li>
            <li>Report PDF</li>
            <li>Grafici interattivi</li>
            <li>API integration</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<p style='text-align: center; color: #999; font-size: 1.1em;'>
    🔔 Vuoi essere notificato al lancio? Contatta il team Avantgrade
</p>
""", unsafe_allow_html=True)
