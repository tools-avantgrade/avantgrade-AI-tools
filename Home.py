import streamlit as st

# Configurazione pagina
st.set_page_config(
    page_title="AvantGrade.com Tools",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ultra-minimale
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
    
    .info-note {
        background: #1a1a1a;
        border-left: 3px solid #F7931E;
        padding: 1rem;
        margin: 2rem 0;
        color: #ccc;
    }
    
    .footer {
        text-align: center;
        padding: 2rem 1rem;
        margin-top: 3rem;
        border-top: 1px solid #FF6B35;
        color: #666;
        font-size: 0.9em;
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

# Info box
st.markdown("""
<div class='info-note'>
    👈 <strong>Select a tool from the sidebar</strong> to get started
</div>
""", unsafe_allow_html=True)

# Tools Grid - 6 tool attivi
col1, col2 = st.columns(2)

with col1:
    # SERP Analyzer
    st.markdown("""
    <div class='tool-card'>
        <h3>🔍 SERP Analyzer</h3>
        <p>Extract up to 100 organic URLs from Google SERP with real-time data and export to Excel</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Competitor Analyzer
    st.markdown("""
    <div class='tool-card'>
        <h3>🕷️ Competitor Content Analyzer</h3>
        <p>Extract HTML tags, metadata, images and complete SEO structure from competitor URLs</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Keyword Clustering
    st.markdown("""
    <div class='tool-card'>
        <h3>🧩 Keyword Clustering Expert</h3>
        <p>AI-powered semantic keyword clustering with Claude Sonnet 4.5 - supports 5000+ keywords</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Query Fan-Out
    st.markdown("""
    <div class='tool-card'>
        <h3>🤖 Query Fan-Out Simulator</h3>
        <p>Expand single queries into intelligent variants using Gemini AI for keyword research</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Alt Text Generator
    st.markdown("""
    <div class='tool-card'>
        <h3>🖼️ Alt Text Generator</h3>
        <p>Generate SEO-optimized alt text for images using OpenAI Vision API - batch processing supported</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Meta Tag Generator
    st.markdown("""
    <div class='tool-card'>
        <h3>📝 Meta Tag Generator</h3>
        <p>AI-powered meta title & description generator using Claude - supports 1000+ URLs with smart batching</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class='footer'>
    <p><strong>AvantGrade.com</strong> • Professional SEO Tools Suite</p>
    <p>6 Active Tools • Built for Digital Marketing Professionals</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🏠 AvantGrade.com")
    st.markdown("---")
    
    st.markdown("### ✅ Active Tools (6)")
    st.markdown("""
**Click a tool below to open:**

Use the Streamlit navigation above ☝️
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔑 Required API Keys")
    st.markdown("""
- **SerpAPI** → SERP Analyzer
- **Google Gemini** → Query Fan-Out
- **Anthropic Claude** → Keyword Clustering, Meta Tag Generator
- **OpenAI** → Alt Text Generator
    """)
    
    st.markdown("---")
    
    st.markdown("### 📚 Quick Start")
    st.markdown("""
1. Select tool from sidebar navigation
2. Insert required parameters
3. Run analysis
4. Download results
    """)
    
    st.markdown("---")
    
    st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.85em;'>
<p><strong>AvantGrade.com</strong></p>
<p>v2.1 • 6 Tools</p>
</div>
    """, unsafe_allow_html=True)
