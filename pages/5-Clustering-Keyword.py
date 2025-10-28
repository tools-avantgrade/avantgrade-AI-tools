import streamlit as st
import pandas as pd
import json
import time
from anthropic import Anthropic
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

# Header
st.title("🧩 Keyword Clustering Expert")
st.markdown("**AI-powered semantic grouping con Claude Sonnet 4.5**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configurazione")
    
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        help="Ottieni la tua API key da console.anthropic.com"
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
        "Max clusters per batch",
        10, 50, 20
    )
    
    batch_size_option = st.selectbox(
        "Batch size (keywords)",
        [250, 500, 1000],
        index=1,
        help="Riduci se hai rate limit errors"
    )
    
    st.markdown("---")
    st.markdown("**Modello:** Claude Sonnet 4.5")
    st.markdown("**Max keywords:** 5000+")
    st.markdown("**⚠️ Rate limit:** 60s delay tra batch")

# Input
st.markdown("### 📝 Input Keywords")

keywords_input = st.text_area(
    "Inserisci le keyword (una per riga)",
    height=300,
    placeholder="keyword 1\nkeyword 2\nkeyword 3\n...",
    help="Una keyword per riga. Supporta fino a 5000+ keywords."
)

st.markdown("""
<div class='info-box'>
💡 <strong>Rate Limit Management:</strong> Il tool gestisce automaticamente i rate limit di Claude
con pause di 60s tra i batch. Per 3000 keywords (~6 batch) ci vogliono circa 6-7 minuti.
</div>
""", unsafe_allow_html=True)

analyze_btn = st.button("🚀 Analizza Keywords", use_container_width=True)

# Funzione clustering
def cluster_keywords_claude(keywords_list, api_key, language, min_size, max_clusters, batch_size=500):
    try:
        client = Anthropic(api_key=api_key)
        all_clusters = []
        total_batches = (len(keywords_list) + batch_size - 1) // batch_size
        
        if len(keywords_list) > batch_size:
            st.info(f"📦 Elaborazione in {total_batches} batch da ~{batch_size} keywords...")
            
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(keywords_list))
            batch_keywords = keywords_list[start_idx:end_idx]
            
            if total_batches > 1:
                st.text(f"📦 Batch {batch_idx + 1}/{total_batches}: keywords {start_idx+1}-{end_idx}")
            
            prompt = f"""You are a professional SEO keyword clustering expert.

Task: Analyze and cluster these {len(batch_keywords)} keywords in {language}.

KEYWORDS:
{chr(10).join(f"{i+1}. {kw}" for i, kw in enumerate(batch_keywords))}

RULES:
1. Create 10-{max_clusters} semantic clusters
2. EVERY keyword MUST be assigned (all {len(batch_keywords)} keywords)
3. Min {min_size} keywords per cluster (flexible if needed)
4. Search intent: Commercial, Transactional, or Informational
5. Group by semantic similarity

Return ONLY valid JSON:
{{
  "clusters": [
    {{
      "cluster_name": "Name",
      "search_intent": "Commercial|Transactional|Informational",
      "keywords": ["kw1", "kw2"],
      "description": "Brief explanation"
    }}
  ]
}}"""

            # Retry logic per rate limits
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=8000,  # Ridotto da 16000 per rate limit
                        messages=[{"role": "user", "content": prompt}]
                    )
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    if "rate_limit" in str(e).lower():
                        retry_count += 1
                        if retry_count < max_retries:
                            wait_time = 60 * retry_count  # 60s, 120s, 180s
                            st.warning(f"⏳ Rate limit raggiunto. Attesa {wait_time}s prima di riprovare (tentativo {retry_count}/{max_retries})...")
                            time.sleep(wait_time)
                        else:
                            return None, f"Rate limit superato dopo {max_retries} tentativi. Attendi qualche minuto e riprova."
                    else:
                        return None, f"Errore API: {str(e)}"
            
            # Delay tra batch per evitare rate limit
            if batch_idx < total_batches - 1:  # Non aspettare dopo l'ultimo batch
                st.info("⏱️ Pausa 60s per rispettare rate limit...")
                time.sleep(60)
            
            result_text = response.content[0].text.strip()
            
            if not result_text:
                return None, f"Batch {batch_idx+1}: risposta vuota"
            
            # Clean markdown
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Extract JSON
            start = result_text.find("{")
            end = result_text.rfind("}")
            
            if start == -1 or end == -1:
                st.error(f"Batch {batch_idx+1}: JSON non trovato")
                st.code(result_text[:300])
                return None, "JSON invalido"
            
            result_text = result_text[start:end+1]
            
            try:
                batch_result = json.loads(result_text)
                batch_kw_count = sum(len(c['keywords']) for c in batch_result['clusters'])
                
                if batch_kw_count < len(batch_keywords):
                    missing = len(batch_keywords) - batch_kw_count
                    st.warning(f"⚠️ Batch {batch_idx+1}: {missing} keyword non clusterizzate ({batch_kw_count}/{len(batch_keywords)})")
                else:
                    st.success(f"✅ Batch {batch_idx+1}: {batch_kw_count}/{len(batch_keywords)} keyword clusterizzate")
                
                all_clusters.extend(batch_result['clusters'])
                
            except json.JSONDecodeError as e:
                st.error(f"❌ Batch {batch_idx+1}: errore JSON")
                st.code(result_text[:500])
                return None, f"JSON error: {str(e)}"
        
        total_clustered = sum(len(c['keywords']) for c in all_clusters)
        missing_total = len(keywords_list) - total_clustered
        
        if missing_total > 0:
            st.warning(f"⚠️ TOTALE: {missing_total} keyword non clusterizzate su {len(keywords_list)}")
        
        summary = {
            "total_keywords": total_clustered,
            "total_keywords_input": len(keywords_list),
            "total_clusters": len(all_clusters),
            "commercial_clusters": sum(1 for c in all_clusters if c['search_intent'] == 'Commercial'),
            "transactional_clusters": sum(1 for c in all_clusters if c['search_intent'] == 'Transactional'),
            "informational_clusters": sum(1 for c in all_clusters if c['search_intent'] == 'Informational')
        }
        
        return {"clusters": all_clusters, "summary": summary}, None
        
    except Exception as e:
        return None, f"Errore: {str(e)}"

# Main logic
if analyze_btn:
    if not api_key:
        st.error("⚠️ Inserisci Anthropic API Key")
    elif not keywords_input.strip():
        st.error("⚠️ Inserisci almeno una keyword")
    else:
        keywords_list = [kw.strip() for kw in keywords_input.strip().split('\n') if kw.strip()]
        
        if len(keywords_list) < 3:
            st.warning("⚠️ Minimo 3 keywords richieste")
        else:
            with st.spinner(f'🤖 Clustering {len(keywords_list)} keywords con Claude...'):
                progress = st.progress(0)
                progress.progress(30)
                
                result, error = cluster_keywords_claude(
                    keywords_list,
                    api_key,
                    language,
                    min_cluster_size,
                    max_clusters,
                    batch_size_option
                )
                
                progress.progress(100)
                time.sleep(0.3)
                progress.empty()
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.session_state['clustering_results'] = result
                
                st.markdown(f"""
                <div class='success-box'>
                ✅ <strong>Analisi completata!</strong><br>
                • {result['summary']['total_keywords_input']} keywords inviate<br>
                • {result['summary']['total_keywords']} keywords clusterizzate<br>
                • {result['summary']['total_clusters']} cluster creati<br>
                • {result['summary']['commercial_clusters']} Commercial | {result['summary']['transactional_clusters']} Transactional | {result['summary']['informational_clusters']} Informational
                </div>
                """, unsafe_allow_html=True)

# Results
if 'clustering_results' in st.session_state:
    result = st.session_state['clustering_results']
    
    st.markdown("---")
    st.markdown("## 📊 Risultati")
    
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
    
    st.dataframe(df, use_container_width=True, height=500)
    
    st.markdown("---")
    
    # Excel export
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Clusters', index=False)
        
        summary_df = pd.DataFrame([{
            'Total Keywords Input': result['summary']['total_keywords_input'],
            'Total Keywords Clustered': result['summary']['total_keywords'],
            'Total Clusters': result['summary']['total_clusters'],
            'Commercial': result['summary']['commercial_clusters'],
            'Transactional': result['summary']['transactional_clusters'],
            'Informational': result['summary']['informational_clusters']
        }])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
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
        file_name=f"clustering_{time.strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.markdown("---")
    st.markdown(f"**Powered by Claude Sonnet 4.5** • {result['summary']['total_keywords']}/{result['summary']['total_keywords_input']} keywords • {result['summary']['total_clusters']} clusters")
