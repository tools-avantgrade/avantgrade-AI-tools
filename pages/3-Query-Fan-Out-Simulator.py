import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px
from datetime import datetime
import json

# Configurazione pagina
st.set_page_config(
    page_title="Query Fan-Out Simulator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato (coerente con Home.py)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #000000 0%, #1a0a00 100%);
    }
    
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
    
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #ffffff !important;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(255, 107, 53, 0.4);
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 2.8em;
        font-weight: 900;
        margin: 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        color: white !important;
    }
    
    .hero-subtitle {
        font-size: 1.2em;
        margin: 10px 0 0 0;
        opacity: 0.95;
        color: white !important;
    }
    
    .card-section {
        background: linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 2px solid #FF6B35;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.2);
    }
    
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
    
    .error-box {
        background: rgba(255, 100, 100, 0.1);
        border-left: 4px solid #ff6464;
        padding: 1.5rem;
        border-radius: 10px;
    }
    
    .success-box {
        background: rgba(0, 255, 136, 0.1);
        border-left: 4px solid #00ff88;
        padding: 1.5rem;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class='hero-section'>
    <h1 class='hero-title'>🤖 Query Fan-Out Simulator</h1>
    <p class='hero-subtitle'>Powered by Gemini AI - Espandi e Analizza Query Complesse</p>
</div>
""", unsafe_allow_html=True)

# Intro
st.markdown("""
<p style='text-align: center; font-size: 1.1em; color: #cccccc; margin-bottom: 2rem;'>
Trasforma una singola query in <strong style='color: #FF6B35;'>varianti intelligenti</strong> usando l'IA generativa. 
Ideale per <strong>keyword research avanzato</strong>, <strong>content planning</strong> e <strong>query expansion</strong>.
</p>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR - CONFIGURAZIONE
# ============================================
with st.sidebar:
    st.markdown("## ⚙️ Configurazione")
    
    # Gemini API Key
    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Ottieni la tua key da https://aistudio.google.com/app/apikeys"
    )
    
    st.markdown("---")
    st.markdown("## 🎯 Opzioni di Analisi")
    
    # Modalità input
    input_mode = st.radio(
        "Modalità Input",
        options=["Single query", "Bulk list"],
        help="Single: una query alla volta | Bulk: carica lista CSV"
    )
    
    # Search Mode
    search_mode = st.radio(
        "Modalità Ricerca",
        options=["AI Overview (semplice)", "AI Mode (complesso)"],
        help="Overview: rapido e leggero | Complex: analisi profonda"
    )
    
    # Numero varianti
    num_variants = st.slider(
        "Numero Varianti Query",
        min_value=3,
        max_value=15,
        value=7,
        help="Quante varianti generare dalla query principale"
    )
    
    # Language
    language = st.selectbox(
        "Lingua",
        options=["Italian", "English", "Spanish", "French", "German"],
        index=0
    )

# ============================================
# CONTROLLO API KEY
# ============================================
if not gemini_api_key:
    st.markdown("""
    <div class='error-box'>
        <strong>⚠️ API Key Mancante</strong><br>
        Inserisci la tua Gemini API Key nella sidebar per iniziare
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Configura Gemini
try:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    st.error(f"❌ Errore configurazione Gemini: {str(e)}")
    st.stop()

# ============================================
# TABS
# ============================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Input Query",
    "🧠 Analisi Varianti",
    "📊 Statistiche",
    "📥 Download",
    "💾 Raw Data"
])

# ============================================
# TAB 1: INPUT QUERY
# ============================================
with tab1:
    st.markdown("<div class='card-section'>", unsafe_allow_html=True)
    st.markdown("### Inserisci Query Principale")
    
    if input_mode == "Single query":
        query_input = st.text_area(
            "Query",
            value="What's the best electric SUV for driving up mt rainier?",
            height=100,
            placeholder="Inserisci la tua query...",
            label_visibility="collapsed"
        )
        queries_to_process = [query_input] if query_input else []
    else:
        uploaded_file = st.file_uploader("Carica CSV con queries", type=["csv"])
        if uploaded_file:
            df_input = pd.read_csv(uploaded_file)
            queries_to_process = df_input.iloc[:, 0].tolist()
            st.info(f"✓ Caricate {len(queries_to_process)} queries")
        else:
            queries_to_process = []
            st.info("👆 Carica un file CSV con colonna contenente le queries")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Pulsante Analizza
    if st.button("🚀 Analizza Query", use_container_width=True, type="primary"):
        if not queries_to_process or (isinstance(queries_to_process, list) and len(queries_to_process) == 0):
            st.error("❌ Inserisci almeno una query")
        else:
            st.session_state['processing'] = True

# ============================================
# PROCESSAMENTO QUERY
# ============================================
if st.session_state.get('processing'):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_results = []
    max_queries = min(len(queries_to_process), 5)
    
    for idx, query in enumerate(queries_to_process[:max_queries]):
        if not query or not str(query).strip():
            continue
            
        status_text.text(f"⏳ Elaborando query {idx+1}/{max_queries}...")
        progress_bar.progress((idx + 1) / max_queries)
        
        try:
            # Prompt di espansione query
            expansion_prompt = f"""Tu sei un esperto SEO e Query Expansion AI. 
Il tuo compito è generare {num_variants} varianti intelligenti e diverse della seguente query originale.

QUERY ORIGINALE: "{query}"
LINGUA: {language}
MODALITÀ: {"AI Overview (semplice)" if search_mode == "AI Overview (semplice)" else "AI Mode (complesso)"}

ISTRUZIONI:
1. Genera ESATTAMENTE {num_variants} varianti diverse
2. Includi: varianti semantiche, sinonimi, riformulazioni, domande correlate
3. Ogni variante deve essere pragmatica e cercabile
4. Restituisci SOLO un JSON valido, niente altro

FORMATO RISPOSTA (JSON):
{{
    "original_query": "{query}",
    "variants": [
        {{"query": "variante 1", "type": "semantic_variation", "intent": "descrizione intento"}},
        {{"query": "variante 2", "type": "question_variation", "intent": "descrizione intento"}}
    ],
    "expansion_metadata": {{
        "total_variants": {num_variants},
        "language": "{language}",
        "search_mode": "{search_mode}"
    }}
}}"""
            
            # Chiama Gemini
            response = model.generate_content(expansion_prompt)
            response_text = response.text
            
            # Estrai JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text)
            all_results.append(result)
            
        except json.JSONDecodeError:
            st.warning(f"⚠️ Errore parsing JSON per query {idx+1}")
        except Exception as e:
            st.error(f"❌ Errore elaborazione query {idx+1}: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    
    # Salva risultati in session state
    st.session_state['fan_out_results'] = all_results
    st.session_state['processing'] = False
    
    if all_results:
        st.success(f"✓ Analisi completata! {len(all_results)} query elaborate")

# ============================================
# TAB 2: ANALISI VARIANTI
# ============================================
with tab2:
    if st.session_state.get('fan_out_results'):
        results = st.session_state['fan_out_results']
        
        for idx, result in enumerate(results):
            st.markdown(f"### 🔍 Query #{idx+1}: {result['original_query']}")
            
            variants_df = pd.DataFrame([
                {
                    "Query": v['query'],
                    "Type": v['type'],
                    "Intent": v['intent']
                }
                for v in result['variants']
            ])
            
            st.dataframe(variants_df, use_container_width=True, hide_index=True)
            
            # Metriche
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Varianti Generate", len(result['variants']))
            with col2:
                st.metric("Lingua", result['expansion_metadata']['language'])
            with col3:
                st.metric("Modalità", "Semplice" if "semplice" in result['expansion_metadata']['search_mode'] else "Complessa")
            
            st.divider()
    else:
        st.info("👆 Elabora una query per vedere le varianti")

# ============================================
# TAB 3: STATISTICHE
# ============================================
with tab3:
    if st.session_state.get('fan_out_results'):
        results = st.session_state['fan_out_results']
        
        # Aggregazione tipi
        all_types = []
        for result in results:
            for variant in result['variants']:
                all_types.append(variant['type'])
        
        type_counts = pd.Series(all_types).value_counts()
        
        # Grafico 1: Distribuzione Tipi
        fig1 = px.bar(
            x=type_counts.index,
            y=type_counts.values,
            labels={'x': 'Tipo Variante', 'y': 'Conteggio'},
            title="Distribuzione Tipi di Varianti",
            color=type_counts.values,
            color_continuous_scale="Oranges"
        )
        fig1.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(20,20,20,0.5)',
            font=dict(color='white'),
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Statistiche
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Query Elaborate", len(results))
        with col2:
            st.metric("Tot. Varianti", sum(len(r['variants']) for r in results))
        with col3:
            st.metric("Tipo Dominante", type_counts.index[0] if len(type_counts) > 0 else "N/A")
        with col4:
            avg_variants = sum(len(r['variants']) for r in results) / len(results) if results else 0
            st.metric("Avg Varianti", f"{avg_variants:.1f}")
    else:
        st.info("👆 Elabora una query per vedere statistiche")

# ============================================
# TAB 4: DOWNLOAD
# ============================================
with tab4:
    if st.session_state.get('fan_out_results'):
        results = st.session_state['fan_out_results']
        
        # Prepara dati per export
        export_data = []
        for result in results:
            for variant in result['variants']:
                export_data.append({
                    "Original Query": result['original_query'],
                    "Variant Query": variant['query'],
                    "Type": variant['type'],
                    "Intent": variant['intent'],
                    "Language": result['expansion_metadata']['language'],
                    "Search Mode": result['expansion_metadata']['search_mode'],
                    "Timestamp": datetime.now().isoformat()
                })
        
        df_export = pd.DataFrame(export_data)
        
        # CSV
        csv = df_export.to_csv(index=False)
        st.download_button(
            "📥 Scarica CSV",
            csv,
            "query_fan_out_results.csv",
            "text/csv",
            use_container_width=True
        )
        
        # JSON
        json_str = json.dumps(results, indent=2, ensure_ascii=False)
        st.download_button(
            "🔗 Scarica JSON",
            json_str,
            "query_fan_out_results.json",
            "application/json",
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Anteprima dati
        st.markdown("### 📋 Anteprima Export")
        st.dataframe(df_export, use_container_width=True, height=400)
    else:
        st.info("👆 Elabora una query per scaricare i risultati")

# ============================================
# TAB 5: RAW DATA
# ============================================
with tab5:
    if st.session_state.get('fan_out_results'):
        results = st.session_state['fan_out_results']
        st.json(results, expanded=False)
    else:
        st.info("👆 Elabora una query per vedere i dati raw")

# ============================================
# FOOTER SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("---")
    st.markdown("## 📚 Info Tool")
    st.markdown("""
    **Query Fan-Out Simulator** è uno strumento AI-powered per:
    
    - 🎯 Espandere query singole
    - 📝 Generare varianti semantiche
    - 🔍 Analizzare intenti di ricerca
    - 📊 Esportare dati strutturati
    
    **Supportato da:** Gemini AI
    **Versione:** 1.0
    """)