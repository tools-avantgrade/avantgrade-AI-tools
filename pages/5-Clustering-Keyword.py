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
    
    .warning-box {
        background-color: #1a1a1a;
        border-left: 3px solid #F7931E;
        padding: 1rem;
        margin: 1rem 0;
        color: #cccccc;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🧩 Keyword Clustering Expert")
st.markdown("**AI-powered intent-based clustering con Claude Sonnet 4.5**")
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
    
    clustering_mode = st.radio(
        "Modalità Clustering",
        ["Auto (AI genera categorie)", "Custom (tu definisci categorie)"],
        help="Auto: AI crea categorie da zero. Custom: usi le tue categorie predefinite"
    )
    
    st.markdown("---")
    
    if clustering_mode == "Auto (AI genera categorie)":
        max_clusters = st.slider(
            "Max categorie da generare",
            5, 30, 15,
            help="Numero massimo di categorie che l'AI può creare"
        )
    else:
        max_clusters = st.slider(
            "Categorie extra da generare",
            0, 10, 2,
            help="Categorie aggiuntive se quelle custom non bastano"
        )
    
    min_cluster_size = st.slider(
        "Min keywords per categoria",
        1, 10, 2,
        help="Minimo keywords per categoria (flessibile)"
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
col_input1, col_input2 = st.columns([1, 1])

with col_input1:
    st.markdown("### 📝 Input Keywords")
    keywords_input = st.text_area(
        "Inserisci le keyword (una per riga)",
        height=300,
        placeholder="best mascara\nmascara for volume\nwaterproof mascara\n...",
        help="Una keyword per riga. Supporta fino a 5000+ keywords."
    )

with col_input2:
    st.markdown("### 🎯 Categorie Custom (Opzionale)")
    
    if clustering_mode == "Custom (tu definisci categorie)":
        st.markdown("**OBBLIGATORIO** - Inserisci le tue categorie:")
    else:
        st.markdown("**OPZIONALE** - Suggerisci categorie iniziali:")
    
    custom_categories = st.text_area(
        "Categorie predefinite",
        height=300,
        placeholder="Generic\nApplication Area\nBuy / Compare\nFeature or Finish\nBrand Specific\nPrice Related\nProblem / Solution\nTutorial / How To\n...",
        help="Una categoria per riga. L'AI userà queste come base."
    )
    
    if custom_categories.strip():
        categories_list = [cat.strip() for cat in custom_categories.strip().split('\n') if cat.strip()]
        st.info(f"✅ {len(categories_list)} categorie definite")

# Info box
st.markdown("""
<div class='info-box'>
💡 <strong>Intent-Based Clustering:</strong> Le keyword vengono categorizzate in base all'intento di ricerca
(Generic, Buy/Compare, Feature, Tutorial, etc.) invece che per prodotto. Rate Limit: ~60s tra batch.
</div>
""", unsafe_allow_html=True)

if clustering_mode == "Custom (tu definisci categorie)" and not custom_categories.strip():
    st.markdown("""
    <div class='warning-box'>
    ⚠️ <strong>Modalità Custom attiva:</strong> Devi inserire almeno 3 categorie custom nel campo a destra.
    </div>
    """, unsafe_allow_html=True)

analyze_btn = st.button("🚀 Analizza Keywords", use_container_width=True)

# Funzione clustering
def cluster_keywords_claude(keywords_list, api_key, language, min_size, max_clusters, batch_size, custom_cats, mode):
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
            
            # Prompt diverso in base alla modalità
            if mode == "Custom (tu definisci categorie)" or (custom_cats and len(custom_cats) > 0):
                # Modalità CUSTOM con categorie predefinite
                categories_text = "\n".join(f"- {cat}" for cat in custom_cats)
                
                if mode == "Custom (tu definisci categorie)":
                    extra_instruction = f"Use ONLY these {len(custom_cats)} categories. Do NOT create new categories."
                else:
                    extra_instruction = f"Use these {len(custom_cats)} categories as PRIMARY options. You can create up to {max_clusters} additional categories ONLY if needed."
                
                prompt = f"""You are a professional SEO keyword clustering expert specializing in INTENT-BASED categorization.

CRITICAL: Group keywords by USER INTENT and SEARCH BEHAVIOR, NOT by product type or brand.

KEYWORDS TO CATEGORIZE:
{chr(10).join(f"{i+1}. {kw}" for i, kw in enumerate(batch_keywords))}

YOUR PREDEFINED INTENT CATEGORIES:
{categories_text}

INTENT CATEGORIZATION RULES:
1. {extra_instruction}
2. EVERY keyword MUST be assigned (all {len(batch_keywords)} keywords)
3. Min {min_size} keywords per category (flexible)
4. **THINK ABOUT USER INTENT**: What is the user trying to DO?
   - Are they learning? → Tutorial/How To
   - Are they comparing prices? → Buy/Compare
   - Are they solving a problem? → Problem/Solution
   - Are they looking for features? → Feature or Finish
   - Are they just browsing? → Generic

EXAMPLES OF INTENT-BASED THINKING:
❌ WRONG: "dior nail polish" → Brand Specific
✅ RIGHT: "dior nail polish" → Generic (broad product search)

❌ WRONG: "makeup brush" → Application Tools
✅ RIGHT: "makeup brush" → Generic (broad search)

❌ WRONG: "best mascara for volume" → Volume Products
✅ RIGHT: "best mascara for volume" → Feature or Finish (seeking specific attribute)

❌ WRONG: "cheap mascara" → Budget Products
✅ RIGHT: "cheap mascara" → Price Related (price-focused intent)

SEARCH INTENT TYPES (for each category):
- Commercial: Ready to buy, high intent
- Transactional: Comparing options, shopping mode
- Informational: Learning, researching, how-to
- Navigational: Seeking specific brand/product

Return ONLY valid JSON:
{{
  "clusters": [
    {{
      "cluster_name": "Category Name (from predefined list)",
      "search_intent": "Commercial|Transactional|Informational|Navigational",
      "keywords": ["kw1", "kw2"],
      "description": "What intent/behavior unites these keywords"
    }}
  ]
}}"""
            else:
                # Modalità AUTO - AI genera categorie intent-based
                prompt = f"""You are a professional SEO keyword clustering expert specializing in INTENT-BASED categorization.

CRITICAL: Group keywords by USER INTENT and SEARCH BEHAVIOR, NOT by product type or brand.

KEYWORDS TO CATEGORIZE:
{chr(10).join(f"{i+1}. {kw}" for i, kw in enumerate(batch_keywords))}

INTENT CATEGORIZATION RULES:
1. Create 5-{max_clusters} INTENT-BASED categories
2. EVERY keyword MUST be assigned (all {len(batch_keywords)} keywords)
3. Min {min_size} keywords per category (flexible)
4. **THINK ABOUT USER INTENT**: What is the user trying to DO?

INTENT CATEGORY TYPES (use these patterns):
- **Generic**: Broad, high-level searches (e.g., "mascara", "nail polish")
- **Application Area**: Specific use case/body part (e.g., "mascara for sensitive eyes")
- **Buy / Compare**: Shopping intent (e.g., "best mascara", "mascara vs eyeliner")
- **Feature or Finish**: Specific attributes (e.g., "waterproof mascara", "matte lipstick")
- **Brand Specific**: Brand-related but still intent-focused (e.g., "dior alternatives")
- **Price Related**: Budget-driven (e.g., "cheap mascara", "luxury makeup")
- **Problem / Solution**: Solving an issue (e.g., "mascara that doesn't smudge")
- **Tutorial / How To**: Educational (e.g., "how to apply mascara")
- **Review / Rating**: Social proof seeking (e.g., "mascara reviews")

EXAMPLES OF CORRECT INTENT THINKING:
✅ "dior nail polish" → Generic (broad product search, not brand-specific)
✅ "best mascara for volume" → Feature or Finish (seeking volume attribute)
✅ "cheap mascara" → Price Related (budget-focused)
✅ "how to remove mascara" → Tutorial / How To (learning intent)
✅ "mascara vs eyeliner" → Buy / Compare (comparison intent)

SEARCH INTENT (for each category):
- Commercial: Ready to buy
- Transactional: Comparing, shopping
- Informational: Learning, researching
- Navigational: Seeking specific brand

Return ONLY valid JSON:
{{
  "clusters": [
    {{
      "cluster_name": "Intent Category Name",
      "search_intent": "Commercial|Transactional|Informational|Navigational",
      "keywords": ["kw1", "kw2"],
      "description": "What user behavior/intent unites these"
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
                        max_tokens=8000,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    break
                    
                except Exception as e:
                    if "rate_limit" in str(e).lower():
                        retry_count += 1
                        if retry_count < max_retries:
                            wait_time = 60 * retry_count
                            st.warning(f"⏳ Rate limit raggiunto. Attesa {wait_time}s (tentativo {retry_count}/{max_retries})...")
                            time.sleep(wait_time)
                        else:
                            return None, f"Rate limit superato dopo {max_retries} tentativi."
                    else:
                        return None, f"Errore API: {str(e)}"
            
            # Delay tra batch
            if batch_idx < total_batches - 1:
                st.info("⏱️ Pausa 60s per rate limit...")
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
                    st.warning(f"⚠️ Batch {batch_idx+1}: {missing} keyword non categorizzate ({batch_kw_count}/{len(batch_keywords)})")
                else:
                    st.success(f"✅ Batch {batch_idx+1}: {batch_kw_count}/{len(batch_keywords)} keyword categorizzate")
                
                all_clusters.extend(batch_result['clusters'])
                
            except json.JSONDecodeError as e:
                st.error(f"❌ Batch {batch_idx+1}: errore JSON")
                st.code(result_text[:500])
                return None, f"JSON error: {str(e)}"
        
        total_clustered = sum(len(c['keywords']) for c in all_clusters)
        missing_total = len(keywords_list) - total_clustered
        
        if missing_total > 0:
            st.warning(f"⚠️ TOTALE: {missing_total} keyword non categorizzate su {len(keywords_list)}")
        
        summary = {
            "total_keywords": total_clustered,
            "total_keywords_input": len(keywords_list),
            "total_clusters": len(all_clusters),
            "commercial_clusters": sum(1 for c in all_clusters if c['search_intent'] == 'Commercial'),
            "transactional_clusters": sum(1 for c in all_clusters if c['search_intent'] == 'Transactional'),
            "informational_clusters": sum(1 for c in all_clusters if c['search_intent'] == 'Informational'),
            "navigational_clusters": sum(1 for c in all_clusters if c['search_intent'] == 'Navigational')
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
    elif clustering_mode == "Custom (tu definisci categorie)" and not custom_categories.strip():
        st.error("⚠️ Modalità Custom attiva: inserisci almeno 3 categorie custom")
    else:
        keywords_list = [kw.strip() for kw in keywords_input.strip().split('\n') if kw.strip()]
        
        custom_cats_list = []
        if custom_categories.strip():
            custom_cats_list = [cat.strip() for cat in custom_categories.strip().split('\n') if cat.strip()]
        
        if clustering_mode == "Custom (tu definisci categorie)" and len(custom_cats_list) < 3:
            st.error("⚠️ Modalità Custom: inserisci almeno 3 categorie")
        elif len(keywords_list) < 3:
            st.warning("⚠️ Minimo 3 keywords richieste")
        else:
            with st.spinner(f'🤖 Clustering intent-based con Claude...'):
                progress = st.progress(0)
                progress.progress(30)
                
                result, error = cluster_keywords_claude(
                    keywords_list,
                    api_key,
                    language,
                    min_cluster_size,
                    max_clusters,
                    batch_size_option,
                    custom_cats_list,
                    clustering_mode
                )
                
                progress.progress(100)
                time.sleep(0.3)
                progress.empty()
            
            if error:
                st.error(f"❌ {error}")
            else:
                st.session_state['clustering_results'] = result
                
                intent_summary = f"{result['summary']['commercial_clusters']} Commercial | {result['summary']['transactional_clusters']} Transactional | {result['summary']['informational_clusters']} Informational"
                if result['summary']['navigational_clusters'] > 0:
                    intent_summary += f" | {result['summary']['navigational_clusters']} Navigational"
                
                st.markdown(f"""
                <div class='success-box'>
                ✅ <strong>Analisi completata!</strong><br>
                • {result['summary']['total_keywords_input']} keywords inviate<br>
                • {result['summary']['total_keywords']} keywords categorizzate<br>
                • {result['summary']['total_clusters']} categorie create<br>
                • {intent_summary}
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
                'Category #': idx,
                'Category Name': cluster['cluster_name'],
                'Search Intent': cluster['search_intent'],
                'Keyword': kw,
                'Intent Description': cluster['description'],
                'Category Size': len(cluster['keywords'])
            })
    
    df = pd.DataFrame(table_data)
    
    st.dataframe(df, use_container_width=True, height=500)
    
    st.markdown("---")
    
    # Excel export
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Categories', index=False)
        
        summary_df = pd.DataFrame([{
            'Total Keywords Input': result['summary']['total_keywords_input'],
            'Total Keywords Categorized': result['summary']['total_keywords'],
            'Total Categories': result['summary']['total_clusters'],
            'Commercial': result['summary']['commercial_clusters'],
            'Transactional': result['summary']['transactional_clusters'],
            'Informational': result['summary']['informational_clusters'],
            'Navigational': result['summary'].get('navigational_clusters', 0)
        }])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        category_summary = []
        for idx, cluster in enumerate(result['clusters'], 1):
            category_summary.append({
                'Category #': idx,
                'Category Name': cluster['cluster_name'],
                'Search Intent': cluster['search_intent'],
                'Keywords Count': len(cluster['keywords']),
                'Intent Description': cluster['description']
            })
        
        category_df = pd.DataFrame(category_summary)
        category_df.to_excel(writer, sheet_name='Category Overview', index=False)
    
    excel_buffer.seek(0)
    
    st.download_button(
        label="📥 Download Excel",
        data=excel_buffer,
        file_name=f"keyword_categorization_{time.strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    st.markdown("---")
    st.markdown(f"**Powered by Claude Sonnet 4.5** • {result['summary']['total_keywords']}/{result['summary']['total_keywords_input']} keywords • {result['summary']['total_clusters']} categories")
