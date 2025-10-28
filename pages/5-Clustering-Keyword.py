import streamlit as st
import pandas as pd
import json
import time
from openai import OpenAI
from io import BytesIO

# Configurazione pagina
st.set_page_config(
    page_title="Keyword Clustering Expert",
    page_icon="🧩",
    layout="wide"
)

# CSS minimale
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
    }
    
    h1, h2, h3, p, label {
        color: #ffffff !important;
    }
    
    .stTextArea textarea {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #FF6B35 !important;
        font-family: monospace;
    }
    
    .stButton>button {
        background-color: #FF6B35;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #F7931E;
    }
    
    .success-box {
        background-color: #1a1a1a;
        border-left: 3px solid #00ff88;
        padding: 1rem;
        margin: 1rem 0;
        color: #cccccc;
    }
    
    .info-box {
        background-color: #1a1a1a;
        border-left: 3px solid #FF6B35;
        padding: 1rem;
        margin: 1rem 0;
        color: #cccccc;
    }
    </style>
""", unsafe_allow_html=True)

# Header minimale
st.title("🧩 Keyword Clustering Expert")
st.markdown("**AI-powered semantic grouping con GPT-4 Turbo**")
st.markdown("---")

# Sidebar minimale
with st.sidebar:
    st.markdown("### ⚙️ Configurazione")
    
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Inserisci la tua API key"
    )
    
    st.markdown("---")
    
    language = st.selectbox(
        "Lingua",
        ["Italiano", "English", "Español", "Français", "Deutsch"]
    )
    
    min_cluster_size = st.slider(
        "Min keywords per cluster",
        2, 10, 3
    )
    
    max_clusters = st.slider(
        "Max clusters",
        3, 20, 10
    )
    
    st.markdown("---")
    st.markdown("**Modello:** GPT-4 Turbo")
    st.markdown("**Max keywords:** 3000+")

# Input area principale
st.markdown("### 📝 Input Keywords")

keywords_input = st.text_area(
    "Inserisci le keyword (una per riga)",
    height=300,
    placeholder="keyword 1\nkeyword 2\nkeyword 3\n...",
    help="Una keyword per riga. Supporta fino a 3000+ keywords."
)

# Info box
st.markdown("""
<div class='info-box'>
💡 <strong>Supporto per liste grandi:</strong> Il tool gestisce automaticamente liste di 3000+ keywords 
dividendole in batch per ottimizzare performance e costi.
</div>
""", unsafe_allow_html=True)

# Bottone analisi
analyze_btn = st.button("🚀 Analizza Keywords", use_container_width=True)

# Funzione clustering con GPT-4 Turbo
def cluster_keywords_gpt4(keywords_list, api_key, language, min_size, max_clusters):
    """
    Clustering con GPT-4 Turbo - supporto liste grandi con batching
    """
    try:
        client = OpenAI(api_key=api_key)
        
        # Per liste molto grandi, usa batching intelligente
        batch_size = 500  # Batch ottimale per GPT-5
        all_clusters = []
        total_batches = (len(keywords_list) + batch_size - 1) // batch_size
        
        if len(keywords_list) > batch_size:
            st.info(f"📦 Lista grande rilevata ({len(keywords_list)} keywords). Elaborazione in {total_batches} batch...")
            
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(keywords_list))
            batch_keywords = keywords_list[start_idx:end_idx]
            
            if total_batches > 1:
                st.text(f"Batch {batch_idx + 1}/{total_batches}: keywords {start_idx+1}-{end_idx}")
            
            # Prompt ottimizzato per GPT-4 Turbo
            prompt = f"""You are a professional SEO keyword clustering expert.

Analyze these {len(batch_keywords)} keywords in {language} and group them into semantic clusters.

KEYWORDS TO CLUSTER:
{chr(10).join(f"{i+1}. {kw}" for i, kw in enumerate(batch_keywords))}

CRITICAL RULES:
1. Create between 5 and {min(max_clusters, len(batch_keywords)//min_size + 5)} semantic clusters
2. EVERY SINGLE KEYWORD MUST BE ASSIGNED TO A CLUSTER (all {len(batch_keywords)} keywords)
3. Each cluster should ideally contain at least {min_size} keywords, but can have less if needed
4. Classify search intent: Commercial, Transactional, or Informational
5. Group keywords by semantic relationships and user search intent

VALIDATION: Count the total keywords in your output - it MUST equal {len(batch_keywords)}.

Return ONLY a valid JSON object (no markdown, no code blocks):
{{
  "clusters": [
    {{
      "cluster_name": "Clear descriptive name",
      "search_intent": "Commercial|Transactional|Informational",
      "keywords": ["keyword1", "keyword2", ...],
      "description": "Why these keywords are grouped together"
    }}
  ]
}}

Return the JSON now:"""

            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",  # GPT-4 Turbo (stabile e affidabile)
                messages=[
                    {"role": "system", "content": "You are a professional SEO keyword clustering expert. You ONLY respond with valid JSON, nothing else."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            
            if not result_text or result_text.strip() == "":
                return None, "GPT-5 ha restituito una risposta vuota. Riprova o riduci il numero di keywords."
            
            result_text = result_text.strip()
            
            # Clean markdown code blocks
            if result_text.startswith("```"):
                parts = result_text.split("```")
                if len(parts) >= 2:
                    result_text = parts[1]
                    if result_text.startswith("json"):
                        result_text = result_text[4:]
                    result_text = result_text.strip()
            
            # Remove any leading/trailing text before/after JSON
            # Find first { and last }
            start_idx = result_text.find("{")
            end_idx = result_text.rfind("}")
            
            if start_idx == -1 or end_idx == -1:
                # Debug: mostra cosa ha restituito GPT-5
                st.error(f"Risposta GPT-5 non contiene JSON valido. Preview: {result_text[:200]}...")
                return None, "GPT-5 non ha restituito JSON valido. Riprova."
            
            result_text = result_text[start_idx:end_idx+1]
            
            try:
                batch_result = json.loads(result_text)
            except json.JSONDecodeError as e:
                st.error(f"Errore parsing JSON batch {batch_idx+1}. Preview: {result_text[:200]}...")
                return None, f"Errore parsing JSON: {str(e)}"
            
            # Validazione batch
            batch_kw_count = sum(len(c['keywords']) for c in batch_result['clusters'])
            if batch_kw_count < len(batch_keywords):
                st.warning(f"⚠️ Batch {batch_idx+1}: solo {batch_kw_count}/{len(batch_keywords)} keyword clusterizzate")
            
            all_clusters.extend(batch_result['clusters'])
        
        # Merge e calcola summary
        total_clustered = sum(len(cluster['keywords']) for cluster in all_clusters)
        
        # WARNING: se mancano keyword
        if total_clustered < len(keywords_list):
            missing = len(keywords_list) - total_clustered
            st.warning(f"⚠️ Attenzione: {missing} keyword non sono state clusterizzate. Prova ad aumentare 'Max clusters' o ridurre 'Min keywords per cluster'.")
        
        summary = {
            "total_keywords": total_clustered,  # Usa il conteggio reale
            "total_keywords_input": len(keywords_list),  # Keyword originali
            "total_clusters": len(all_clusters),
            "commercial_clusters": sum(1 for c in all_clusters if c['search_intent'] == 'Commercial'),
            "transactional_clusters": sum(1 for c in all_clusters if c['search_intent'] == 'Transactional'),
            "informational_clusters": sum(1 for c in all_clusters if c['search_intent'] == 'Informational')
        }
        
        result = {
            "clusters": all_clusters,
            "summary": summary
        }
        
        return result, None
        
    except json.JSONDecodeError as e:
        return None, f"Errore JSON: {str(e)}"
    except Exception as e:
        return None, f"Errore: {str(e)}"

# Logica principale
if analyze_btn:
    if not api_key:
        st.error("⚠️ Inserisci OpenAI API Key")
    elif not keywords_input.strip():
        st.error("⚠️ Inserisci almeno una keyword")
    else:
        keywords_list = [kw.strip() for kw in keywords_input.strip().split('\n') if kw.strip()]
        
        if len(keywords_list) < 3:
            st.warning("⚠️ Minimo 3 keywords richieste")
        else:
            # Progress
            with st.spinner(f'🤖 Clustering {len(keywords_list)} keywords con GPT-4 Turbo...'):
                progress = st.progress(0)
                
                progress.progress(30)
                result, error = cluster_keywords_gpt4(
                    keywords_list,
                    api_key,
                    language,
                    min_cluster_size,
                    max_clusters
                )
                
                progress.progress(100)
                time.sleep(0.3)
                progress.empty()
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.session_state['clustering_results'] = result
                st.session_state['keywords_analyzed'] = keywords_list
                
                st.markdown(f"""
                <div class='success-box'>
                ✅ <strong>Analisi completata!</strong><br>
                • {result['summary']['total_keywords_input']} keywords inviate<br>
                • {result['summary']['total_keywords']} keywords clusterizzate<br>
                • {result['summary']['total_clusters']} cluster creati<br>
                • {result['summary']['commercial_clusters']} Commercial | {result['summary']['transactional_clusters']} Transactional | {result['summary']['informational_clusters']} Informational
                </div>
                """, unsafe_allow_html=True)

# Visualizzazione risultati
if 'clustering_results' in st.session_state:
    result = st.session_state['clustering_results']
    
    st.markdown("---")
    st.markdown("## 📊 Risultati")
    
    # Crea tabella
    table_data = []
    for idx, cluster in enumerate(result['clusters'], 1):
        for kw in cluster['keywords']:
            table_data.append({
                'Cluster #': idx,
                'Cluster Name': cluster['cluster_name'],
                'Search Intent': cluster['search_intent'],
                'Keyword': kw,
                'Description': cluster['description'],
                'Cluster Size': len(cluster['keywords'])
            })
    
    df = pd.DataFrame(table_data)
    
    # Mostra tabella
    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )
    
    st.markdown("---")
    
    # Download Excel
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Sheet principale
        df.to_excel(writer, sheet_name='Clusters', index=False)
        
        # Sheet summary
        summary_df = pd.DataFrame([{
            'Total Keywords': result['summary']['total_keywords'],
            'Total Clusters': result['summary']['total_clusters'],
            'Commercial': result['summary']['commercial_clusters'],
            'Transactional': result['summary']['transactional_clusters'],
            'Informational': result['summary']['informational_clusters']
        }])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet per cluster (dettaglio)
        cluster_summary = []
        for idx, cluster in enumerate(result['clusters'], 1):
            cluster_summary.append({
                'Cluster #': idx,
                'Cluster Name': cluster['cluster_name'],
                'Search Intent': cluster['search_intent'],
                'Keywords Count': len(cluster['keywords']),
                'Description': cluster['description']
            })
        
        cluster_df = pd.DataFrame(cluster_summary)
        cluster_df.to_excel(writer, sheet_name='Cluster Overview', index=False)
    
    excel_buffer.seek(0)
    
    st.download_button(
        label="📥 Download Excel",
        data=excel_buffer,
        file_name=f"keyword_clustering_{time.strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.markdown("---")
    st.markdown(f"**Powered by GPT-4 Turbo** • {result['summary']['total_keywords']} keywords • {result['summary']['total_clusters']} clusters")
