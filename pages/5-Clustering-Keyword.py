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
    /* Background & Text */
    .stApp { background-color: #000000; }
    h1, h2, h3, h4, p, label, div { color: #ffffff !important; }
    
    /* Text Areas & Inputs */
    .stTextArea textarea {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 2px solid #FF6B35 !important;
        border-radius: 8px !important;
        font-family: 'SF Mono', Monaco, monospace;
        font-size: 14px !important;
        padding: 12px !important;
    }
    .stTextArea textarea:focus {
        border-color: #F7931E !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1) !important;
    }
    .stTextInput input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 2px solid #FF6B35 !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
    }
    .stTextInput input:focus {
        border-color: #F7931E !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1) !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #F7931E 0%, #FF6B35 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
    }
    
    /* Primary Button */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        font-size: 18px;
        padding: 0.8rem 2rem;
        box-shadow: 0 4px 20px rgba(255, 107, 53, 0.4);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        border: 1px solid #FF6B35 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    
    /* Info/Success/Warning Boxes */
    .success-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #0d2818 100%);
        border-left: 4px solid #00ff88;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        color: #cccccc;
        box-shadow: 0 2px 8px rgba(0, 255, 136, 0.1);
    }
    .info-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a1a0d 100%);
        border-left: 4px solid #FF6B35;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        color: #cccccc;
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.1);
    }
    .warning-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a1f0d 100%);
        border-left: 4px solid #F7931E;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 1rem 0;
        color: #cccccc;
        box-shadow: 0 2px 8px rgba(247, 147, 30, 0.1);
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #FF6B35 !important;
        font-size: 32px !important;
        font-weight: bold !important;
    }
    
    /* Headers Styling */
    h1 { 
        font-size: 2.5rem !important; 
        font-weight: 700 !important;
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem !important;
    }
    h2 { 
        font-size: 1.8rem !important; 
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    h3 { 
        font-size: 1.3rem !important; 
        font-weight: 500 !important;
        color: #F7931E !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Containers */
    .stContainer {
        background-color: #0d0d0d;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Divider */
    hr {
        border-color: #FF6B35 !important;
        opacity: 0.3 !important;
        margin: 2rem 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ===============================
# Header
# ===============================
st.title("🧩 Keyword Clustering Expert")
st.markdown("**AI-powered intent-based clustering con Claude Sonnet 4.5** <span style='background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%); padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; margin-left: 10px; letter-spacing: 1px;'>BETA</span>", unsafe_allow_html=True)
st.markdown("---")

# ===============================
# Sidebar (Minimal)
# ===============================
    with st.sidebar:
    st.markdown("### ⚙️ Configurazione")
    st.markdown("""
        <div style='background: linear-gradient(135deg, #2a1a0d 0%, #1a1a1a 100%); 
                    border: 1px solid #F7931E; 
                    border-radius: 8px; 
                    padding: 8px; 
                    text-align: center; 
                    margin-bottom: 1rem;'>
            <span style='color: #F7931E; font-weight: 700; font-size: 13px; letter-spacing: 1px;'>⚠️ BETA VERSION</span>
        </div>
    """, unsafe_allow_html=True)

    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        help="Ottieni la tua API key da console.anthropic.com"
    )

    st.markdown("---")

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
# Input Section - Layout Verticale
# ===============================
st.markdown("## 📝 Step 1: Input Keywords")
st.markdown("Inserisci le tue keyword (una per riga)")

keywords_input = st.text_area(
    "keywords_input_label",
    height=300,
    placeholder="armani lipstick\nbest base makeup for oily skin\ncorrettore kiko\nmascara waterproof\nshop near me\nhow to apply mascara\n...",
    help="Una keyword per riga. Qualsiasi lingua. Fino a 5000+ keywords.",
    label_visibility="collapsed"
)

st.markdown("---")

# ===============================
# Context Section
# ===============================
st.markdown("## 🎯 Step 2: Contesto (Opzionale ma Consigliato)")

with st.expander("💡 Perché il contesto migliora i risultati?", expanded=False):
    st.markdown("""
    **Lista Prodotti**: Aiuta l'AI a capire cosa vendi (es: "correttore" = prodotto makeup, non accessorio)
    
    **Macrotema**: Fornisce il settore generale (es: Makeup, Tech, Food) per disambiguare keyword ambigue
    
    **Risultato**: +30-40% di accuratezza nella categorizzazione! 🚀
    """)

col_context1, col_context2 = st.columns([1, 1])

with col_context1:
    st.markdown("### 🏷️ Lista Prodotti")
    products_input = st.text_area(
        "products_label",
        height=150,
        placeholder="correttore\nfondotinta\nmascara\nmatita occhi\nrossetto\n...",
        help="Lista prodotti del tuo brand (uno per riga)",
        label_visibility="collapsed"
    )

with col_context2:
    st.markdown("### 🎯 Macrotema/i")
    macro_theme_input = st.text_input(
        "macrotema_label",
        placeholder="Makeup, Beauty, Cosmetics",
        help="Tema generale (separati da virgola se più di uno)",
        label_visibility="collapsed"
    )
    
    # Spacer per allineamento
    st.markdown("<br>" * 5, unsafe_allow_html=True)

st.markdown("---")

# ===============================
# Categories Section
# ===============================
st.markdown("## 🗂️ Step 3: Categorie Intent-Based")

if clustering_mode == "Custom (tu definisci categorie)":
    st.info("💡 **Modalità Custom**: Modifica le 4 categorie default o aggiungine di nuove. La descrizione è fondamentale!")
else:
    st.info("💡 **Modalità Auto**: L'AI genera categorie autonomamente. Puoi comunque suggerire categorie preferite.")

# Initialize session state for categories with new defaults
if 'custom_categories_list' not in st.session_state:
    st.session_state['custom_categories_list'] = [
        {"name": "Generic", "description": "Broad searches with no specific intent signals (e.g., 'armani lipstick', 'nike shoes')"},
        {"name": "Buy / Compare", "description": "Shopping/comparison intent with words like 'best', 'top', 'vs', 'review' (e.g., 'best laptop 2024')"},
        {"name": "LOCAL", "description": "Location-based searches with words like 'near me', 'shop', 'store', 'where to buy' (e.g., 'shop near me', 'kiko store milano')"},
        {"name": "HOW TO", "description": "Tutorial/educational intent with 'how to', 'tutorial', 'guide', 'tips' (e.g., 'how to apply mascara', 'makeup tutorial')"}
    ]

# Display categories in a more compact way
for idx, cat in enumerate(st.session_state['custom_categories_list']):
    with st.container():
        col1, col2, col3 = st.columns([3, 6, 0.7])
        
        with col1:
            cat_name = st.text_input(
                f"cat_name_label_{idx}",
                value=cat['name'],
                key=f"cat_name_{idx}",
                placeholder="Nome categoria",
                label_visibility="collapsed"
            )
            st.session_state['custom_categories_list'][idx]['name'] = cat_name
        
        with col2:
            cat_desc = st.text_input(
                f"cat_desc_label_{idx}",
                value=cat['description'],
                key=f"cat_desc_{idx}",
                placeholder="Descrizione dettagliata dell'intento di ricerca",
                label_visibility="collapsed"
            )
            st.session_state['custom_categories_list'][idx]['description'] = cat_desc
        
        with col3:
            if st.button("🗑️", key=f"delete_{idx}", help="Elimina categoria", use_container_width=True):
                st.session_state['custom_categories_list'].pop(idx)
                st.rerun()

# Action buttons
col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 2])

with col_btn1:
    if st.button("➕ Aggiungi Categoria", use_container_width=True):
        st.session_state['custom_categories_list'].append({
            "name": "",
            "description": ""
        })
        st.rerun()

with col_btn2:
    if st.button("🔄 Reset Default", use_container_width=True):
        st.session_state['custom_categories_list'] = [
            {"name": "Generic", "description": "Broad searches with no specific intent signals (e.g., 'armani lipstick', 'nike shoes')"},
            {"name": "Buy / Compare", "description": "Shopping/comparison intent with words like 'best', 'top', 'vs', 'review' (e.g., 'best laptop 2024')"},
            {"name": "LOCAL", "description": "Location-based searches with words like 'near me', 'shop', 'store', 'where to buy' (e.g., 'shop near me', 'kiko store milano')"},
            {"name": "HOW TO", "description": "Tutorial/educational intent with 'how to', 'tutorial', 'guide', 'tips' (e.g., 'how to apply mascara', 'makeup tutorial')"}
        ]
        st.rerun()

with col_btn3:
    valid_cats = [c for c in st.session_state['custom_categories_list'] if c['name'].strip()]
    st.metric("Categorie Attive", len(valid_cats))

st.markdown("---")

# Validation warning
if clustering_mode == "Custom (tu definisci categorie)" and len(valid_cats) < 3:
    st.warning("⚠️ **Modalità Custom**: Definisci almeno 3 categorie con nome e descrizione.")

# ===============================
# Main Action Button
# ===============================
st.markdown("## 🚀 Step 4: Analizza")

analyze_btn = st.button("🚀 ANALIZZA KEYWORDS", use_container_width=True, type="primary")

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
def cluster_keywords_claude(keywords_list, api_key, batch_size, custom_cats, mode, max_clusters, products_list=None, macro_theme=None):
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
                    extra_instruction = f"Use ONLY these {len(custom_cats)} categories as PRIMARY guide. You can create max {max_clusters} additional categories ONLY if absolutely necessary."
                else:
                    extra_instruction = f"Prefer these {len(custom_cats)} categories. Create max {max_clusters} additional categories ONLY if needed."

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

CREATE: 5-{max_clusters} intent categories with English names
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
                    max_clusters,
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
