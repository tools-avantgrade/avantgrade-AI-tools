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
        padding: 3rem 1rem;
        margin-bottom: 2rem;
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
    
    .tool-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .tool-card {
        background: #0a0a0a;
        border: 1px solid #FF6B35;
        border-radius: 8px;
        padding: 1.5rem;
        transition: border-color 0.3s;
    }
    
    .tool-card:hover {
        border-color: #F7931E;
    }
    
    .tool-card h3 {
        color: #FF6B35;
        font-size: 1.3em;
        margin: 0 0 0.5rem 0;
    }
    
    .tool-card p {
        color: #999;
        font-size: 0.95em;
        line-height: 1.5;
        margin: 0;
    }
    
    .status {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.75em;
        font-weight: bold;
        margin-top: 0.5rem;
    }
    
    .active {
        background: #00ff88;
        color: #000;
    }
    
    .coming {
        background: #333;
        color: #999;
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
    <p>SEO & Digital Marketing Suite</p>
</div>
""", unsafe_allow_html=True)

# Tools Grid
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='tool-card'>
        <h3>🔍 SERP Analyzer</h3>
        <p>Extract up to 100 organic URLs from Google SERP with real-time data</p>
        <span class='status active'>ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='tool-card'>
        <h3>📊 Keyword Research</h3>
        <p>Discover keyword opportunities with volume, difficulty and trends</p>
        <span class='status coming'>COMING SOON</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='tool-card'>
        <h3>🤖 Query Fan-Out</h3>
        <p>Expand queries into intelligent variants using Gemini AI</p>
        <span class='status active'>ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='tool-card'>
        <h3>🎯 Content Optimizer</h3>
        <p>Optimize content with readability analysis and SEO suggestions</p>
        <span class='status coming'>COMING SOON</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='tool-card'>
        <h3>🕷️ Competitor Analyzer</h3>
        <p>Extract HTML tags, metadata and SEO structure from competitors</p>
        <span class='status active'>ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='tool-card'>
        <h3>🧩 Keyword Clustering</h3>
        <p>AI-powered semantic clustering with Claude Sonnet 4.5</p>
        <span class='status active'>ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)

# Second row
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
    <div class='tool-card'>
        <h3>🔗 Backlink Checker</h3>
        <p>Monitor backlink profile and analyze link quality</p>
        <span class='status coming'>COMING SOON</span>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class='tool-card'>
        <h3>📈 Analytics Dashboard</h3>
        <p>Centralized dashboard for SEO performance monitoring</p>
        <span class='status coming'>COMING SOON</span>
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
    
    st.markdown("### ✅ Active Tools")
    st.markdown("""
- 🔍 SERP Analyzer
- 🤖 Query Fan-Out
- 🕷️ Competitor Analyzer
- 🧩 Keyword Clustering **NEW**
    """)
    
    st.markdown("### ⏳ Coming Soon")
    st.markdown("""
- 📊 Keyword Research
- 🎯 Content Optimizer
- 📈 Analytics Dashboard
- 🔗 Backlink Checker
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔑 API Keys")
    st.markdown("""
**Required:**
- SerpAPI → SERP Analyzer
- Gemini → Query Fan-Out
- Anthropic → Keyword Clustering
    """)
    
    st.markdown("---")
    
    st.markdown("### 📚 Quick Start")
    st.markdown("""
1. Select tool from sidebar
2. Insert parameters
3. Analyze results
4. Download reports
    """)
    
    st.markdown("---")
    
    st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.85em;'>
<p>AvantGrade.com v2.0</p>
<p>4 Active Tools</p>
</div>
    """, unsafe_allow_html=True)
