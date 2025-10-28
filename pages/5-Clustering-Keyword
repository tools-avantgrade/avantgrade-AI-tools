import streamlit as st
import pandas as pd
import json
import time
from openai import OpenAI
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO

# Configurazione pagina
st.set_page_config(
    page_title="Keyword Clustering Expert | Avantgrade Tools",
    page_icon="🧩",
    layout="wide"
)

# CSS personalizzato (identico agli altri tool)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #000000 0%, #1a0a00 100%);
    }
    
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #ffffff !important;
    }
    
    .tool-header {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 20px rgba(255, 107, 53, 0.3);
    }
    
    .feature-card {
        background: linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 2px solid #FF6B35;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.2);
    }
    
    .feature-card h3 {
        color: #FF6B35 !important;
        margin-bottom: 0.5rem;
    }
    
    .cluster-box {
        background: rgba(255, 107, 53, 0.1);
        border-left: 4px solid #FF6B35;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
    }
    
    .cluster-title {
        color: #FF6B35 !important;
        font-size: 1.3em;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .cluster-intent {
        background: linear-gradient(135deg, #F7931E 0%, #FF6B35 100%);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.9em;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .keyword-pill {
        background: #2d2d2d;
        color: #cccccc;
        padding: 0.4rem 1rem;
        border-radius: 15px;
        margin: 0.3rem;
        display: inline-block;
        border: 1px solid #FF6B35;
        font-size: 0.95em;
    }
    
    .stats-box {
        background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        border: 2px solid #FF6B35;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.2);
    }
    
    .stats-number {
        font-size: 2.5em;
        font-weight: bold;
        color: #FF6B35;
        margin: 0;
    }
    
    .stats-label {
        color: #cccccc;
        font-size: 1.1em;
        margin-top: 0.5rem;
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
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255, 107, 53, 0.5);
    }
    
    .info-box {
        background: rgba(247, 147, 30, 0.1);
        border: 1px solid #F7931E;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: rgba(255, 107, 53, 0.1);
        border: 1px solid #FF6B35;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class='tool-header'>
    <h1 style='color: white; margin: 0; font-size: 2.5em;'>🧩 Keyword Clustering Expert</h1>
    <p style='color: white; margin: 0.5rem 0 0 0; font-size: 1.2em; opacity: 0.95;'>
        AI-Powered Semantic Keyword Grouping with GPT-4 Turbo
    </p>
</div>
""", unsafe_allow_html=True)

# Introduzione
st.markdown("""
<div class='info-box'>
    <p style='color: #cccccc; font-size: 1.05em; margin: 0;'>
        <strong style='color: #F7931E;'>Keyword Clustering Expert</strong> analizza automaticamente le tue keyword e le raggruppa 
        per <strong>search intent</strong> e <strong>relazioni semantiche</strong>, aiutandoti a creare strategie di contenuto 
        mirate e ottimizzate per la SEO.
    </p>
</div>
""", unsafe_allow_html=True)

# Features cards
st.markdown("### 💡 Funzionalità Principali")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown("""
    <div class='feature-card'>
        <h3>🎯 Search Intent Classification</h3>
        <p style='color: #cccccc;'>
            Categorizzazione automatica come Commercial, Transactional o Informational
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown("""
    <div class='feature-card'>
        <h3>🧠 Semantic Grouping</h3>
        <p style='color: #cccccc;'>
            Clustering basato su relazioni semantiche per topic coherence
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_f3:
    st.markdown("""
    <div class='feature-card'>
        <h3>📊 Multilingual Support</h3>
        <p style='color: #cccccc;'>
            Analisi keyword in multiple lingue per SEO internazionale
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar - Configurazione
with st.sidebar:
    st.markdown("## ⚙️ Configurazione")
    
    st.markdown("### 🔑 OpenAI API Key")
    api_key = st.text_input(
        "Inserisci la tua API Key",
        type="password",
        help="Ottieni la tua API key da platform.openai.com"
    )
    
    st.markdown("### 🌍 Lingua Target")
    target_language = st.selectbox(
        "Seleziona lingua",
        ["Italiano", "English", "Español", "Français", "Deutsch"],
        help="Lingua per l'analisi delle keyword"
    )
    
    st.markdown("### 🎚️ Parametri Clustering")
    
    min_cluster_size = st.slider(
        "Dimensione minima cluster",
        min_value=2,
        max_value=10,
        value=3,
        help="Numero minimo di keyword per cluster"
    )
    
    max_clusters = st.slider(
        "Numero massimo cluster",
        min_value=3,
        max_value=15,
        value=8,
        help="Limita il numero di cluster generati"
    )
    
    st.markdown("---")
    st.markdown("### 📚 Info Tool")
    st.markdown("""
    **Modello:** GPT-4 Turbo
    
    **Search Intent:**
    - 🛒 Commercial
    - 💰 Transactional
    - 📖 Informational
    
    **Output:**
    - Cluster overview
    - Detailed markdown
    - Excel export
    - Visualizzazioni
    """)

# Form principale
st.markdown("## 📝 Input Keywords")

keywords_input = st.text_area(
    "Inserisci le keyword (una per riga)",
    height=200,
    placeholder="migliori smartphone 2025\nsmartphone economici\ncome scegliere smartphone\nreview iPhone 15\nacquistare Samsung Galaxy...",
    help="Inserisci ogni keyword su una riga separata"
)

# Info box
st.markdown("""
<div class='warning-box'>
    <p style='color: #cccccc; margin: 0; font-size: 0.95em;'>
        <strong style='color: #FF6B35;'>💡 Suggerimento:</strong> 
        Inserisci almeno 10-15 keyword per ottenere cluster significativi. 
        Il tool funziona meglio con keyword correlate allo stesso topic.
    </p>
</div>
""", unsafe_allow_html=True)

# Bottone analisi
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    analyze_button = st.button("🚀 Analizza e Raggruppa Keywords", use_container_width=True)

# Funzione clustering con OpenAI
def cluster_keywords_with_gpt4(keywords_list, api_key, language, min_size, max_clusters):
    """
    Clustering semantico usando GPT-4
    """
    try:
        client = OpenAI(api_key=api_key)
        
        # Prompt engineering per clustering
        prompt = f"""You are a professional SEO expert specializing in keyword clustering and search intent analysis.

Analyze the following list of keywords in {language} language and group them into semantic clusters.

Keywords to analyze:
{chr(10).join(f"- {kw}" for kw in keywords_list)}

Instructions:
1. Create between 3 and {max_clusters} semantic clusters
2. Each cluster should contain at least {min_size} keywords (if possible)
3. Identify the main theme/topic for each cluster
4. Classify the search intent for each cluster as: Commercial, Transactional, or Informational
5. Group keywords that have semantic relationships and similar user search intent

Return ONLY a valid JSON object with this exact structure (no markdown, no code blocks, just raw JSON):
{{
  "clusters": [
    {{
      "cluster_name": "Clear descriptive name for the cluster",
      "search_intent": "Commercial|Transactional|Informational",
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "description": "Brief explanation of why these keywords are grouped together"
    }}
  ],
  "summary": {{
    "total_keywords": number,
    "total_clusters": number,
    "commercial_clusters": number,
    "transactional_clusters": number,
    "informational_clusters": number
  }}
}}

CRITICAL: Return ONLY the JSON object, no additional text, no markdown formatting, no code blocks."""

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional SEO keyword clustering expert. You ONLY respond with valid JSON, nothing else."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Rimuovi eventuali markdown code blocks
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()
        
        result = json.loads(result_text)
        return result, None
        
    except json.JSONDecodeError as e:
        return None, f"Errore parsing JSON: {str(e)}"
    except Exception as e:
        return None, f"Errore durante l'analisi: {str(e)}"

# Logica principale
if analyze_button:
    if not api_key:
        st.error("⚠️ Inserisci la tua OpenAI API Key nella sidebar!")
    elif not keywords_input.strip():
        st.error("⚠️ Inserisci almeno una keyword!")
    else:
        # Parse keywords
        keywords_list = [kw.strip() for kw in keywords_input.strip().split('\n') if kw.strip()]
        
        if len(keywords_list) < 3:
            st.warning("⚠️ Inserisci almeno 3 keyword per un clustering efficace")
        else:
            # Progress bar
            with st.spinner('🤖 Analisi AI in corso con GPT-4...'):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔍 Analisi semantica keyword...")
                progress_bar.progress(25)
                time.sleep(0.5)
                
                status_text.text("🧠 Clustering con AI...")
                progress_bar.progress(50)
                
                # Chiamata API
                result, error = cluster_keywords_with_gpt4(
                    keywords_list, 
                    api_key, 
                    target_language,
                    min_cluster_size,
                    max_clusters
                )
                
                progress_bar.progress(75)
                status_text.text("📊 Generazione visualizzazioni...")
                time.sleep(0.5)
                
                progress_bar.progress(100)
                status_text.text("✅ Analisi completata!")
                time.sleep(0.5)
                
                progress_bar.empty()
                status_text.empty()
            
            if error:
                st.error(f"❌ {error}")
            else:
                # Salva in session state
                st.session_state['clustering_results'] = result
                st.session_state['keywords_analyzed'] = keywords_list
                
                st.success(f"✅ Analisi completata! Trovati {result['summary']['total_clusters']} cluster semantici")

# Visualizzazione risultati
if 'clustering_results' in st.session_state:
    result = st.session_state['clustering_results']
    keywords_analyzed = st.session_state['keywords_analyzed']
    
    st.markdown("---")
    st.markdown("## 📊 Risultati Clustering")
    
    # Statistiche generali
    st.markdown("### 📈 Statistiche Generali")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    
    with col_s1:
        st.markdown(f"""
        <div class='stats-box'>
            <p class='stats-number'>{result['summary']['total_keywords']}</p>
            <p class='stats-label'>Keywords</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_s2:
        st.markdown(f"""
        <div class='stats-box'>
            <p class='stats-number'>{result['summary']['total_clusters']}</p>
            <p class='stats-label'>Clusters</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_s3:
        avg_keywords = round(result['summary']['total_keywords'] / result['summary']['total_clusters'], 1)
        st.markdown(f"""
        <div class='stats-box'>
            <p class='stats-number'>{avg_keywords}</p>
            <p class='stats-label'>Media KW/Cluster</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_s4:
        commercial_pct = round((result['summary']['commercial_clusters'] / result['summary']['total_clusters']) * 100)
        st.markdown(f"""
        <div class='stats-box'>
            <p class='stats-number'>{commercial_pct}%</p>
            <p class='stats-label'>Commercial</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tab per visualizzazioni diverse
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Cluster Overview", "📊 Grafici", "📥 Export", "📝 Tabella Completa"])
    
    with tab1:
        st.markdown("### 🎯 Cluster Dettagliati")
        
        for idx, cluster in enumerate(result['clusters'], 1):
            st.markdown(f"""
            <div class='cluster-box'>
                <p class='cluster-title'>Cluster {idx}: {cluster['cluster_name']}</p>
                <span class='cluster-intent'>{cluster['search_intent']}</span>
                <p style='color: #cccccc; margin-top: 1rem;'>{cluster['description']}</p>
                <p style='color: #999; font-size: 0.9em; margin-top: 0.5rem;'>
                    <strong>{len(cluster['keywords'])}</strong> keywords in questo cluster
                </p>
                <div style='margin-top: 1rem;'>
                    {"".join([f"<span class='keyword-pill'>{kw}</span>" for kw in cluster['keywords']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📊 Visualizzazioni")
        
        # Grafico 1: Distribuzione Search Intent
        intent_counts = {
            'Commercial': result['summary']['commercial_clusters'],
            'Transactional': result['summary']['transactional_clusters'],
            'Informational': result['summary']['informational_clusters']
        }
        
        fig_intent = go.Figure(data=[
            go.Pie(
                labels=list(intent_counts.keys()),
                values=list(intent_counts.values()),
                hole=0.4,
                marker=dict(colors=['#FF6B35', '#F7931E', '#FFA500']),
                textfont=dict(size=14, color='white')
            )
        ])
        
        fig_intent.update_layout(
            title="Distribuzione Search Intent",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12),
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig_intent, use_container_width=True)
        
        # Grafico 2: Keywords per cluster
        cluster_sizes = [len(c['keywords']) for c in result['clusters']]
        cluster_names = [c['cluster_name'][:30] + '...' if len(c['cluster_name']) > 30 else c['cluster_name'] 
                        for c in result['clusters']]
        
        fig_sizes = go.Figure(data=[
            go.Bar(
                x=cluster_names,
                y=cluster_sizes,
                marker=dict(
                    color=cluster_sizes,
                    colorscale=[[0, '#FF6B35'], [1, '#F7931E']],
                    line=dict(color='white', width=1)
                ),
                text=cluster_sizes,
                textposition='outside',
                textfont=dict(color='white', size=12)
            )
        ])
        
        fig_sizes.update_layout(
            title="Keywords per Cluster",
            xaxis_title="Cluster",
            yaxis_title="Numero Keywords",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(26,26,26,0.5)',
            font=dict(color='white', size=12),
            xaxis=dict(tickangle=-45),
            height=400
        )
        
        st.plotly_chart(fig_sizes, use_container_width=True)
    
    with tab3:
        st.markdown("### 📥 Download Risultati")
        
        # Markdown export
        markdown_output = f"# Keyword Clustering Report\n\n"
        markdown_output += f"**Total Keywords:** {result['summary']['total_keywords']}\n\n"
        markdown_output += f"**Total Clusters:** {result['summary']['total_clusters']}\n\n"
        markdown_output += f"**Language:** {target_language}\n\n"
        markdown_output += "---\n\n"
        
        for idx, cluster in enumerate(result['clusters'], 1):
            markdown_output += f"## Cluster {idx}: {cluster['cluster_name']}\n\n"
            markdown_output += f"**Search Intent:** {cluster['search_intent']}\n\n"
            markdown_output += f"**Description:** {cluster['description']}\n\n"
            markdown_output += "**Keywords:**\n"
            for kw in cluster['keywords']:
                markdown_output += f"- {kw}\n"
            markdown_output += "\n---\n\n"
        
        # Excel export
        excel_data = []
        for cluster in result['clusters']:
            for kw in cluster['keywords']:
                excel_data.append({
                    'Keyword': kw,
                    'Cluster': cluster['cluster_name'],
                    'Search Intent': cluster['search_intent'],
                    'Description': cluster['description']
                })
        
        df_export = pd.DataFrame(excel_data)
        
        # Buffer Excel
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_export.to_excel(writer, sheet_name='Clusters', index=False)
            
            # Summary sheet
            summary_df = pd.DataFrame([{
                'Total Keywords': result['summary']['total_keywords'],
                'Total Clusters': result['summary']['total_clusters'],
                'Commercial': result['summary']['commercial_clusters'],
                'Transactional': result['summary']['transactional_clusters'],
                'Informational': result['summary']['informational_clusters']
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        excel_buffer.seek(0)
        
        # Bottoni download
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.download_button(
                label="📄 Download Markdown",
                data=markdown_output,
                file_name="keyword_clustering_report.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col_d2:
            st.download_button(
                label="📊 Download Excel",
                data=excel_buffer,
                file_name="keyword_clustering_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # JSON export
        json_output = json.dumps(result, indent=2, ensure_ascii=False)
        st.download_button(
            label="📋 Download JSON",
            data=json_output,
            file_name="keyword_clustering_report.json",
            mime="application/json",
            use_container_width=True
        )
    
    with tab4:
        st.markdown("### 📝 Tabella Completa")
        
        # Crea dataframe dettagliato
        table_data = []
        for idx, cluster in enumerate(result['clusters'], 1):
            for kw in cluster['keywords']:
                table_data.append({
                    'Cluster #': idx,
                    'Cluster Name': cluster['cluster_name'],
                    'Keyword': kw,
                    'Search Intent': cluster['search_intent'],
                    'Keywords in Cluster': len(cluster['keywords'])
                })
        
        df_table = pd.DataFrame(table_data)
        
        st.dataframe(
            df_table,
            use_container_width=True,
            height=400
        )
        
        # CSV download
        csv = df_table.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="keyword_clustering_table.csv",
            mime="text/csv",
            use_container_width=True
        )

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; padding: 2rem; border-top: 2px solid #FF6B35; color: #999;'>
    <p style='font-size: 1em;'>
        🧩 <strong style='color: #FF6B35;'>Keyword Clustering Expert</strong> | 
        Powered by GPT-4 Turbo
    </p>
    <p style='font-size: 0.9em; margin-top: 0.5rem;'>
        Parte di <strong style='color: #F7931E;'>Avantgrade Tools Suite</strong>
    </p>
</div>
""", unsafe_allow_html=True)
