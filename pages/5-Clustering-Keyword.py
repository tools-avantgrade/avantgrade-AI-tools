import streamlit as st
import pandas as pd
import json
import time
from anthropic import Anthropic
from io import BytesIO

# ===============================
# Configurazione pagina & stile
# ===============================
st.set_page_config(
    page_title="Keyword Clustering Expert",
    page_icon="🧩",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, label { color: #ffffff !important; }
    .stTextArea textarea {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #FF6B35 !important;
        font-family: monospace;
    }
    .stTextInput input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #FF6B35 !important;
    }
    .stButton>button {
        background-color: #FF6B35;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover { background-color: #F7931E; }
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
    .compact-label {
        font-size: 0.9rem;
        color: #cccccc;
        margin-bottom: 0.3rem;
    }
    </style>
""", unsafe_allow_html=True)

# ===============================
# Header
# ===============================
st.title("🧩 Keyword Clustering Expert")
st.markdown("**AI-powered intent-based clustering con Claude Sonnet 4.5**")
st.markdown("---")

# ===============================
# Sidebar (Minimal)
# ===============================
with st.sidebar:
    st.markdown("### ⚙️ Configurazione")

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        help="Ottieni la tua API key da console.anthropic.com"
    )

    st.markdown("---")

    clustering_mode = st.radio(
        "Modalità Clustering",
        ["Auto (AI genera categorie)", "Custom (tu definisci categorie)"],
        help="Auto: AI crea categorie da zero. Custom: usi le tue 4 categorie predefinite"
    )

    st.markdown("---")

    batch_size_option = st.selectbox(
        "Batch size",
        [100, 150, 200],
        index=1,
        help="⚠️ Riduci a 100 se vedi errori JSON"
    )

    st.markdown("---")
    st.markdown("**Modello:** Claude Sonnet 4.5")
    st.markdown("**Max keywords:** 5000+")
    st.markdown("**Output:** Always English")
    st.markdown("**⚠️ Delay:** 60s tra batch")

# ===============================
# Input Section
# ===============================
col_input1, col_input2 = st.columns([1, 1])

with col_input1:
    st.markdown("### 📝 Input Keywords & Context")
    
    # Keywords input
    keywords_input = st.text_area(
        "Keywords (una per riga)",
        height=200,
        placeholder="armani lipstick\nbest base makeup for oily skin\ncorrettore kiko\nmascara waterproof\nshop near me\n...",
        help="Una keyword per riga. Qualsiasi lingua. Fino a 5000+ keywords."
    )
    
    # Product list input
    st.markdown("<div class='compact-label'>🏷️ Lista Prodotti (opzionale ma consigliato)</div>", unsafe_allow_html=True)
    products_input = st.text_area(
        "prodotti",
        height=100,
        placeholder="correttore\nfondotinta\nmascara\nmatita occhi\nrossetto\n...",
        help="Lista prodotti del tuo brand. Aiuta l'AI a capire il contesto (es. 'correttore' è un prodotto, non un accessorio)",
        label_visibility="collapsed"
    )
    
    # Macro theme input
    st.markdown("<div class='compact-label'>🎯 Macrotema/i (opzionale)</div>", unsafe_allow_html=True)
    macro_theme_input = st.text_input(
        "macrotema",
        placeholder="Makeup, Beauty, Cosmetics",
        help="Tema generale della keyword research. Puoi inserirne più di uno separati da virgola",
        label_visibility="collapsed"
    )

with col_input2:
    st.markdown("### 🎯 Categorie Intent-Based")

    # Info box about categories
    if clustering_mode == "Custom (tu definisci categorie)":
        st.markdown("""
        <div class='info-box'>
        💡 Modifica le 4 categorie default o aggiungine di nuove.<br>
        La <strong>descrizione</strong> è fondamentale per la classificazione.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='info-box'>
        💡 L'AI genera categorie autonomamente.<br>
        Puoi comunque suggerire categorie preferite.
        </div>
        """, unsafe_allow_html=True)

    # Initialize session state for categories with new defaults
    if 'custom_categories_list' not in st.session_state:
        st.session_state['custom_categories_list'] = [
            {"name": "Generic", "description": "Broad searches with no specific intent signals (e.g., 'armani lipstick', 'nike shoes')"},
            {"name": "Buy / Compare", "description": "Shopping/comparison intent with words like 'best', 'top', 'vs', 'review' (e.g., 'best laptop 2024')"},
            {"name": "LOCAL", "description": "Location-based searches with words like 'near me', 'shop', 'store', 'where to buy' (e.g., 'shop near me', 'kiko store milano')"},
            {"name": "HOW TO", "description": "Tutorial/educational intent with 'how to', 'tutorial', 'guide', 'tips' (e.g., 'how to apply mascara', 'makeup tutorial')"}
        ]

    # Display existing categories with inline editing (more compact)
    for idx, cat in enumerate(st.session_state['custom_categories_list']):
        with st.container():
            col_name, col_delete = st.columns([6, 1])
            
            with col_name:
                cat_name = st.text_input(
                    f"Categoria {idx+1}",
                    value=cat['name'],
                    key=f"cat_name_{idx}",
                    placeholder="Nome categoria...",
                    label_visibility="collapsed"
                )
                st.session_state['custom_categories_list'][idx]['name'] = cat_name
            
            with col_delete:
                if st.button("🗑️", key=f"delete_{idx}", help="Elimina", use_container_width=True):
                    st.session_state['custom_categories_list'].pop(idx)
                    st.rerun()
            
            cat_desc = st.text_area(
                f"Descrizione {idx+1}",
                value=cat['description'],
                key=f"cat_desc_{idx}",
                placeholder="Descrizione dettagliata dell'intento...",
                height=60,
                label_visibility="collapsed"
            )
            st.session_state['custom_categories_list'][idx]['description'] = cat_desc
            
            st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

    # Action buttons (more compact)
    col_add, col_reset = st.columns([1, 1])
    
    with col_add:
        if st.button("➕ Aggiungi", use_container_width=True):
            st.session_state['custom_categories_list'].append({
                "name": "",
                "description": ""
            })
            st.rerun()
    
    with col_reset:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state['custom_categories_list'] = [
                {"name": "Generic", "description": "Broad searches with no specific intent signals (e.g., 'armani lipstick', 'nike shoes')"},
                {"name": "Buy / Compare", "description": "Shopping/comparison intent with words like 'best', 'top', 'vs', 'review' (e.g., 'best laptop 2024')"},
                {"name": "LOCAL", "description": "Location-based searches with words like 'near me', 'shop', 'store', 'where to buy' (e.g., 'shop near me', 'kiko store milano')"},
                {"name": "HOW TO", "description": "Tutorial/educational intent with 'how to', 'tutorial', 'guide', 'tips' (e.g., 'how to apply mascara', 'makeup tutorial')"}
            ]
            st.rerun()

    # Count valid categories
    valid_cats = [c for c in st.session_state['custom_categories_list'] if c['name'].strip()]
    if valid_cats:
        st.success(f"✅ {len(valid_cats)} categorie definite")

# Validation warning
if clustering_mode == "Custom (tu definisci categorie)" and len(valid_cats) < 3:
    st.markdown("""
    <div class='warning-box'>
    ⚠️ <strong>Modalità Custom:</strong> Definisci almeno 3 categorie con nome e descrizione.
    </div>
    """, unsafe_allow_html=True)

# Main action button
analyze_btn = st.button("🚀 Analizza Keywords", use_container_width=True)

# ===============================
# Helper: normalizzazione cluster
# ===============================
def normalize_clusters(batch_result):
    """Normalizza i cluster rendendoli robusti a campi mancanti."""
    valid_clusters = []
    for cluster in batch_result.get('clusters', []):
        if not isinstance(cluster, dict):
            continue

        kw_list = cluster.get('keywords', [])
        if not isinstance(kw_list, list):
            continue

        cluster['cluster_name'] = cluster.get('cluster_name', 'Uncategorized')
        cluster['description'] = cluster.get('description', '')

        valid_keywords = []
        for kw in kw_list:
            if isinstance(kw, dict):
                keyword = str(kw.get('keyword', '')).strip()
                brand = kw.get('brand', None)
            else:
                keyword = str(kw).strip()
                brand = None

            if keyword:
                valid_keywords.append({'keyword': keyword, 'brand': brand})

        if valid_keywords:
            cluster['keywords'] = valid_keywords
            valid_clusters.append(cluster)

    return valid_clusters

# ===============================
# Funzione clustering (Claude)
# ===============================
def cluster_keywords_claude(keywords_list, api_key, batch_size, custom_cats, mode, products_list=None, macro_theme=None):
    try:
        client = Anthropic(api_key=api_key)
        all_clusters = []
        total_batches = (len(keywords_list) + batch_size - 1) // batch_size

        if len(keywords_list) > batch_size:
            st.info(f"📦 Elaborazione in {total_batches} batch da ~{batch_size} keywords...")

        # Prepare context sections
        context_section = ""
        
        if products_list:
            products_text = "\n".join(f"- {p}" for p in products_list)
            context_section += f"""
PRODUCT CONTEXT:
These are the products we're analyzing keywords for:
{products_text}

IMPORTANT: When you see these product names in keywords, treat them as PRODUCTS (not accessories or other categories).
Example: If "correttore" is in the product list, keywords like "correttore kiko" should be categorized based on INTENT, not treated as a different product type.
"""

        if macro_theme:
            context_section += f"""
MACRO THEME(S): {macro_theme}
Use this theme to better understand the overall context of the keyword research.
"""

        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(keywords_list))
            batch_keywords = keywords_list[start_idx:end_idx]

            if total_batches > 1:
                st.text(f"📦 Batch {batch_idx + 1}/{total_batches}: keywords {start_idx+1}-{end_idx}")

            # Costruisci testo categorie con descrizioni
            if custom_cats and len(custom_cats) > 0:
                categories_text = "\n".join(
                    f"- **{cat['name']}**: {cat['description']}" 
                    for cat in custom_cats 
                    if cat['name'].strip()
                )
                
                if mode == "Custom (tu definisci categorie)":
                    extra_instruction = f"Use ONLY these {len(custom_cats)} categories with their descriptions as your PRIMARY guide."
                else:
                    extra_instruction = f"Prefer these {len(custom_cats)} categories. Create additional ones ONLY if absolutely necessary."

                prompt = f"""You are an expert SEO keyword intent analyzer.

CRITICAL INSTRUCTIONS:
- ALWAYS respond in ENGLISH (category names, descriptions in English)
- Keywords can be in ANY language - you must understand them all
- Output JSON with English category names and descriptions

{context_section}

TASK: Categorize keywords by USER SEARCH INTENT (why they're searching), NOT by product type.

KEYWORDS ({len(batch_keywords)} - may be in any language):
{chr(10).join(f"{i+1}. {kw}" for i, kw in enumerate(batch_keywords))}

YOUR PREDEFINED CATEGORIES WITH DESCRIPTIONS (in English):
{categories_text}

IMPORTANT: Use the category DESCRIPTIONS as your PRIMARY guide for assignment.
Each description tells you EXACTLY what kind of keywords belong in that category.

BRAND DETECTION:
- If keyword contains a recognizable brand name (Armani, Dior, MAC, Nike, Apple, Samsung, KIKO, etc.), extract it
- Put brand name in "brand" field (capitalize properly)
- Do NOT create "Brand Specific" categories

RULES:
- {extra_instruction}
- EVERY keyword must be categorized (all {len(batch_keywords)})
- Think: "WHY is the user searching this?" and match to category description
- Keep your "description" field SHORT (max 10 words, in English)
- Category names and descriptions MUST be in English

JSON FORMAT:
{{
  "clusters": [
    {{
      "cluster_name": "Exact category name from list (English)",
      "keywords": [
        {{
          "keyword": "the keyword (original language)",
          "brand": "Brand Name or null"
        }}
      ],
      "description": "Brief reason for grouping (English, max 10 words)"
    }}
  ]
}}"""
            else:
                # AUTO mode - genera categorie
                prompt = f"""You are an expert SEO keyword intent analyzer.

CRITICAL INSTRUCTIONS:
- ALWAYS respond in ENGLISH (category names, descriptions in English)
- Keywords can be in ANY language - you must understand them all
- Output JSON with English category names and descriptions

{context_section}

TASK: Categorize keywords by USER SEARCH INTENT (why they're searching), NOT by product type.

KEYWORDS ({len(batch_keywords)} - may be in any language):
{chr(10).join(f"{i+1}. {kw}" for i, kw in enumerate(batch_keywords))}

INTENT CATEGORIZATION LOGIC (create categories with English names):

1. **Generic**: Vague, broad searches with NO specific intent signals
   Examples: "armani lipstick", "nike shoes", "samsung phone", "rossetto", "zapatos"

2. **Buy / Compare**: Contains comparison or shopping modifiers
   Examples: "best base makeup for oily skin", "top 10 laptops", "migliori smartphone"
   Words: best, top, vs, comparison, review, migliori, mejores, etc.

3. **LOCAL**: Location-based searches
   Examples: "shop near me", "kiko store milano", "where to buy mascara", "vicino a me"
   Words: near me, shop, store, where to buy, negozio, tienda, vicino, etc.

4. **HOW TO**: Tutorial/educational intent
   Examples: "how to apply mascara", "makeup tutorial", "come applicare il trucco"
   Words: how to, tutorial, guide, tips, come fare, tutorial, guida, etc.

5. **Feature or Finish**: SPECIFIC attributes/characteristics
   Examples: "waterproof mascara", "matte red lipstick", "mascara impermeabile"

6. **Price Related**: Budget-focused
   Examples: "cheap mascara", "luxury skincare", "economico", "barato"

7. **Problem / Solution**: Addresses specific problem
   Examples: "mascara that doesn't smudge", "laptop for gaming"

BRAND DETECTION:
- Extract recognizable brand names to "brand" field
- Capitalize properly (Armani, Nike, Samsung, KIKO, etc.)
- Do NOT create "Brand Specific" categories

CREATE: 5-15 intent categories with English names
RULES:
- EVERY keyword must be categorized (all {len(batch_keywords)})
- Think: "WHY is the user searching this?"
- Focus on INTENT, not product type
- Keep "description" field SHORT (max 10 words, in English)
- Category names MUST be in English

JSON FORMAT:
{{
  "clusters": [
    {{
      "cluster_name": "Intent Category Name (English)",
      "keywords": [
        {{
          "keyword": "the keyword (original language)",
          "brand": "Brand Name or null"
        }}
      ],
      "description": "Brief reason (English, max 10 words)"
    }}
  ]
}}"""

            # Retry & call
            max_retries = 3
            retry_count = 0
            response = None

            while retry_count < max_retries:
                try:
                    response = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=20000,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    break
                except Exception as e:
                    if "rate_limit" in str(e).lower():
                        retry_count += 1
                        if retry_count < max_retries:
                            wait_time = 60 * retry_count
                            st.warning(f"⏳ Rate limit. Attesa {wait_time}s (tentativo {retry_count}/{max_retries})...")
                            time.sleep(wait_time)
                        else:
                            return None, f"Rate limit superato dopo {max_retries} tentativi."
                    else:
                        return None, f"Errore API: {str(e)}"

            # Delay tra batch
            if batch_idx < total_batches - 1:
                st.info("⏱️ Pausa 60s per rate limit...")
                time.sleep(60)

            result_text = (response.content[0].text if response and response.content else "").strip()
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

            # Tentativo chiusura se troncato
            if not result_text.endswith("}"):
                st.warning(f"⚠️ Batch {batch_idx+1}: Risposta troncata, tentativo recupero...")
                open_brackets = result_text.count("[") - result_text.count("]")
                open_braces = result_text.count("{") - result_text.count("}")
                if open_brackets > 0:
                    result_text += "]" * open_brackets
                if open_braces > 0:
                    result_text += "}" * open_braces

            # Parse
            try:
                batch_result = json.loads(result_text)

                if not isinstance(batch_result, dict) or 'clusters' not in batch_result:
                    st.error(f"❌ Batch {batch_idx+1}: Struttura JSON invalida")
                    st.code(result_text[:500])
                    return None, "Struttura JSON non valida"

                normalized = normalize_clusters(batch_result)
                batch_result['clusters'] = normalized

                batch_kw_count = sum(len(c.get('keywords', [])) for c in batch_result['clusters'])
                if batch_kw_count < len(batch_keywords):
                    missing = len(batch_keywords) - batch_kw_count
                    st.warning(f"⚠️ Batch {batch_idx+1}: {missing} keyword non categorizzate ({batch_kw_count}/{len(batch_keywords)})")
                else:
                    st.success(f"✅ Batch {batch_idx+1}: {batch_kw_count}/{len(batch_keywords)} keyword categorizzate")

                all_clusters.extend(batch_result['clusters'])

            except json.JSONDecodeError as e:
                st.error(f"❌ Batch {batch_idx+1}: errore JSON - {str(e)}")
                st.code(result_text[:500] + "\n...\n" + result_text[-200:])
                with st.expander("🔍 Debug Info"):
                    st.text(f"Lunghezza: {len(result_text)} chars")
                    st.text(f"[ : {result_text.count('[') - result_text.count(']')}")
                    st.text(f"{{ : {result_text.count('{') - result_text.count('}')}")
                return None, f"JSON error: {str(e)}"

        # Totali
        total_clustered = sum(len(c.get('keywords', [])) for c in all_clusters)
        missing_total = len(keywords_list) - total_clustered
        if missing_total > 0:
            st.warning(f"⚠️ TOTALE: {missing_total} keyword non categorizzate su {len(keywords_list)}")

        def cname(c):
            return (c.get('cluster_name') or '').lower()

        summary = {
            "total_keywords": total_clustered,
            "total_keywords_input": len(keywords_list),
            "total_clusters": len(all_clusters),
            "generic_count": sum(len(c.get('keywords', [])) for c in all_clusters if cname(c) == 'generic'),
            "buy_compare_count": sum(len(c.get('keywords', [])) for c in all_clusters if 'buy' in cname(c) or 'compare' in cname(c)),
            "local_count": sum(len(c.get('keywords', [])) for c in all_clusters if 'local' in cname(c)),
            "howto_count": sum(len(c.get('keywords', [])) for c in all_clusters if 'how to' in cname(c)),
            "branded_count": sum(
                1
                for c in all_clusters
                for kw in c.get('keywords', [])
                if isinstance(kw, dict) and kw.get('brand')
            )
        }

        return {"clusters": all_clusters, "summary": summary}, None

    except Exception as e:
        return None, f"Errore: {str(e)}"

# ===============================
# Main logic
# ===============================
if analyze_btn:
    if not api_key:
        st.error("⚠️ Inserisci Anthropic API Key")
    elif not keywords_input.strip():
        st.error("⚠️ Inserisci almeno una keyword")
    elif clustering_mode == "Custom (tu definisci categorie)" and len(valid_cats) < 3:
        st.error("⚠️ Modalità Custom: inserisci almeno 3 categorie con nome e descrizione")
    else:
        keywords_list = [kw.strip() for kw in keywords_input.strip().split('\n') if kw.strip()]
        products_list = [p.strip() for p in products_input.strip().split('\n') if p.strip()] if products_input.strip() else None
        macro_theme = macro_theme_input.strip() if macro_theme_input.strip() else None

        if len(keywords_list) < 3:
            st.warning("⚠️ Minimo 3 keywords richieste")
        else:
            with st.spinner('🤖 Clustering intent-based con Claude...'):
                progress = st.progress(0)
                progress.progress(30)

                result, error = cluster_keywords_claude(
                    keywords_list,
                    api_key,
                    batch_size_option,
                    valid_cats,
                    clustering_mode,
                    products_list,
                    macro_theme
                )

                progress.progress(100)
                time.sleep(0.3)
                progress.empty()

            if error:
                st.error(f"❌ {error}")
            else:
                st.session_state['clustering_results'] = result

                summary_items = [
                    f"• {result['summary']['total_keywords_input']} keywords inviate",
                    f"• {result['summary']['total_keywords']} keywords categorizzate",
                    f"• {result['summary']['total_clusters']} categorie create",
                    f"• {result['summary']['branded_count']} keywords con brand"
                ]
                
                if products_list:
                    summary_items.append(f"• {len(products_list)} prodotti nel contesto")
                if macro_theme:
                    summary_items.append(f"• Macrotema: {macro_theme}")
                
                st.markdown(f"""
                <div class='success-box'>
                ✅ <strong>Analisi completata!</strong><br>
                {"<br>".join(summary_items)}
                </div>
                """, unsafe_allow_html=True)

# ===============================
# Results
# ===============================
if 'clustering_results' in st.session_state:
    result = st.session_state['clustering_results']

    st.markdown("---")
    st.markdown("## 📊 Risultati")

    table_data = []
    for idx, cluster in enumerate(result.get('clusters', []), 1):
        c_name = cluster.get('cluster_name', 'Uncategorized')
        c_desc = cluster.get('description', '')
        kws = cluster.get('keywords', [])
        for kw_data in kws:
            if isinstance(kw_data, dict):
                keyword = kw_data.get('keyword', '')
                brand = kw_data.get('brand', '')
            else:
                keyword = kw_data
                brand = ''
            table_data.append({
                'Category #': idx,
                'Category Name': c_name,
                'Keyword': keyword,
                'Brand': brand if brand else '',
                'Intent Description': c_desc,
                'Category Size': len(kws)
            })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, height=500)

    st.markdown("---")

    # Excel export
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Categories', index=False)

        summary_df = pd.DataFrame([{
            'Total Keywords Input': result['summary'].get('total_keywords_input', 0),
            'Total Keywords Categorized': result['summary'].get('total_keywords', 0),
            'Total Categories': result['summary'].get('total_clusters', 0),
            'Keywords with Brand': result['summary'].get('branded_count', 0),
            'Generic Count': result['summary'].get('generic_count', 0),
            'Buy/Compare Count': result['summary'].get('buy_compare_count', 0),
            'LOCAL Count': result['summary'].get('local_count', 0),
            'HOW TO Count': result['summary'].get('howto_count', 0)
        }])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        category_summary = []
        for idx, cluster in enumerate(result.get('clusters', []), 1):
            category_summary.append({
                'Category #': idx,
                'Category Name': cluster.get('cluster_name', 'Uncategorized'),
                'Keywords Count': len(cluster.get('keywords', [])),
                'Intent Description': cluster.get('description', '')
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
    st.markdown(f"**Powered by Claude Sonnet 4.5** • {result['summary'].get('total_keywords', 0)}/{result['summary'].get('total_keywords_input', 0)} keywords • {result['summary'].get('total_clusters', 0)} categories")
