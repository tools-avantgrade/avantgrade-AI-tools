import streamlit as st

# Configurazione pagina
st.set_page_config(
    page_title="AvantGrade.com Tools",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ultra-minimale con cards cliccabili
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #FF6B35;
    }
    
    h1, h2, h3, p, label {
        color: #ffffff !important;
    }
    
    .hero {
        text-align: center;
        padding: 3rem 1rem 2rem 1rem;
    }
    
    .hero h1 {
        font-size: 3em;
        font-weight: 900;
        color: #FF6B35;
        margin: 0;
    }
    
    .hero p {
        font-size: 1.2em;
        color: #999;
        margin: 1rem 0 0 0;
    }
    
    .tool-card {
        background: #0a0a0a;
        border: 1px solid #FF6B35;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .tool-card:hover {
        border-color: #F7931E;
        background: #111;
        transform: translateY(-2px);
    }
    
    .tool-card h3 {
        color: #FF6B35;
        font-size: 1.4em;
        margin: 0 0 0.5rem 0;
    }
    
    .tool-card p {
        color: #999;
        font-size: 0.95em;
        line-height: 1.5;
        margin: 0;
    }
    
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        margin-top: 3rem;
        border-top: 1px solid #FF6B35;
        color: #666;
        font-size: 0.9em;
    }
    
    /* Hide default streamlit button styling */
    .stButton>button {
        all: unset;
        display: block;
        width: 100%;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class='hero'>
    <h1>AvantGrade.com Tools</h1>
    <p>Professional SEO & Digital Marketing Suite</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tools Grid - 4 tool attivi
col1, col2 = st.columns(2)

with col1:
    # SERP Analyzer
    if st.button("serp_analyzer", key="serp", use_container_width=True):
        st.switch_page("pages/1-SERP-Analyzer.py")
    
    st.markdown("""
    <div class='tool-card' onclick='document.querySelector("[data-testid=\\"baseButton-secondary\\"][key=\\"serp\\"]").click()'>
        <h3>🔍 SERP Analyzer</h3>
        <p>Extract up to 100 organic URLs from Google SERP with real-time data and export to Excel</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Competitor Analyzer
    if st.button("competitor_analyzer", key="competitor", use_container_width=True):
        st.switch_page("pages/4-Competitor-Content-Analyzer.py")
    
    st.markdown("""
    <div class='tool-card' onclick='document.querySelector("[data-testid=\\"baseButton-secondary\\"][key=\\"competitor\\"]").click()'>
        <h3>🕷️ Competitor Content Analyzer</h3>
        <p>Extract HTML tags, metadata, images and complete SEO structure from competitor URLs</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Query Fan-Out
    if st.button("query_fanout", key="fanout", use_container_width=True):
        st.switch_page("pages/3-Query-Fan-Out-Simulator.py")
    
    st.markdown("""
    <div class='tool-card' onclick='document.querySelector("[data-testid=\\"baseButton-secondary\\"][key=\\"fanout\\"]").click()'>
        <h3>🤖 Query Fan-Out Simulator</h3>
        <p>Expand single queries into intelligent variants using Gemini AI for keyword research</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Keyword Clustering
    if st.button("clustering", key="cluster", use_container_width=True):
        st.switch_page("pages/5-Keyword-Clustering-Expert.py")
    
    st.markdown("""
    <div class='tool-card' onclick='document.querySelector("[data-testid=\\"baseButton-secondary\\"][key=\\"cluster\\"]").click()'>
        <h3>🧩 Keyword Clustering Expert</h3>
        <p>AI-powered semantic keyword clustering with Claude Sonnet 4.5 - supports 5000+ keywords</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class='footer'>
    <p><strong>AvantGrade.com</strong> • Professional SEO Tools Suite</p>
    <p>4 Active Tools • Built for Digital Marketing Professionals</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🏠 AvantGrade.com")
    st.markdown("---")
    
    st.markdown("### ✅ Active Tools (4)")
    st.markdown("""
**Click any tool to start:**

- 🔍 SERP Analyzer
- 🤖 Query Fan-Out Simulator
- 🕷️ Competitor Content Analyzer
- 🧩 Keyword Clustering Expert
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔑 Required API Keys")
    st.markdown("""
- **SerpAPI** → SERP Analyzer
- **Google Gemini** → Query Fan-Out
- **Anthropic Claude** → Keyword Clustering
    """)
    
    st.markdown("---")
    
    st.markdown("### 📚 Quick Start")
    st.markdown("""
1. Click a tool card above
2. Insert required parameters
3. Run analysis
4. Download results
    """)
    
    st.markdown("---")
    
    st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.85em;'>
<p><strong>AvantGrade.com</strong></p>
<p>v2.0 • 4 Tools</p>
</div>
    """, unsafe_allow_html=True)
