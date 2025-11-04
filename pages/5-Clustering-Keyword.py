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
    </style>
""", unsafe_allow_html=True)

# ===============================
# Header
# ===============================
st.title("🧩 Keyword Clustering Expert")
st.markdown("**AI-powered intent-based clustering con Claude Sonnet 4.5**")
st.markdown("---")

# ===============================
# Sidebar
# ===============================
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
        [100, 150, 200, 300],
        index=1,
        help="IMPORTANTE: Riduci a 100-150 se vedi errori JSON troncati"
    )

    st.markdown("---")
    st.markdown("**Modello:** Claude Sonnet 4.5")
    st.markdown("**Max keywords:** 5000+")
    st.markdown("**⚠️ Rate limit:** 60s delay tra batch")

# ===============================
# Input
# ===============================
col_input1, col_input2 = st.columns([1, 1])

with col_input1:
    st.markdown("### 📝 Input Keywords")
    keywords_input = st.text_area(
        "Inserisci le keyword (una per riga)",
        height=300,
        placeholder="armani lipstick\nbest base makeup for oily skin\nbad gal 24 hour eye pencil waterproof black 0.25 g\ncheap mascara\n...",
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
        placeholder="Generic\nBuy / Compare\nFeature or Finish\nPrice Related\nProblem / Solution\nTutorial / How To\n...",
        help="Una categoria per riga. L'AI userà queste come base."
    )

    if custom_categories.strip():
        categories_list = [cat.strip() for cat in custom_categories.strip().split('\n') if cat.strip()]
        st.info(f"✅ {len(categories_list)} categorie definite")

# ===============================
# Info box
# ===============================
st.markdown("""
<div class='info-box'>
💡 <strong>Intent-Based Clustering:</strong> Keywords categorizzate per MOTIVO della ricerca, non per tipo di prodotto.
Brand rilevati automaticamente in colonna separata.
</div>
""", unsafe_allow_html=True)

if clustering_mode == "Custom (tu definisci categorie)" and not custom_categories.strip():
    st.markdown("""
    <div class='warning-box'>
    ⚠️ <strong>Modalità Custom attiva:</strong> Devi inserire almeno 3 categorie custom nel campo a destra.
    </div>
    """, unsafe_allow_html=True)

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

        # normalizza campi del cluster
        cluster['cluster_name'] = cluster.get('cluster_name', 'Uncategorized')
        cluster['description'] = cluster.get('description', '')

        # normalizza le keywords
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

            # Prompt
            if mode == "Custom (tu definisci categorie)" or (custom_cats and len(custom_cats) > 0):
                categories_text = "\n".join(f"- {cat}" for cat in custom_cats)

                if mode == "Custom (tu definisci categorie)":
                    extra_instruction = f"Use ONLY these {len(custom_cats)} categories."
                else:
                    extra_instruction = f"Prefer these {len(custom_cats)} categories. Create max {max_clusters} additional if needed."

                prompt = f"""You are an expert SEO keyword intent analyzer.

TASK: Categorize keywords by USER SEARCH INTENT (why they're searching), NOT by product type.

KEYWORDS ({len(batch_keywords)}):
{chr(10).join(f"{i+1}. {kw}" for i, kw in enumerate(batch_keywords))}

YOUR CATEGORIES:
{categories_text}

INTENT CATEGORIZATION LOGIC:

1. **Generic**: Vague, broad searches with NO specific intent signals
   Examples: "armani lipstick", "nike shoes", "samsung phone"
   → User is just browsing, no clear goal

2. **Buy / Compare**: Contains comparison or shopping modifiers
   Examples: "best base makeup for oily skin", "top 10 laptops", "iphone vs samsung"
   → Words like: best, top, vs, comparison, review, affordable

3. **Feature or Finish**: Describes SPECIFIC attributes or characteristics
   Examples: "waterproof mascara", "bad gal 24 hour eye pencil waterproof black 0.25 g", "matte red lipstick"
   → Has detailed specs, features, colors, finishes

4. **Price Related**: Budget-focused searches
   Examples: "cheap mascara", "luxury skincare", "affordable laptop"
   → Words like: cheap, expensive, luxury, budget, affordable, under $X

5. **Problem / Solution**: Addresses a specific problem
   Examples: "mascara that doesn't smudge", "laptop for gaming", "phone with best camera"
   → User has a problem to solve

6. **Tutorial / How To**: Educational intent
   Examples: "how to apply mascara", "makeup tutorial", "nail art ideas"
   → Words like: how to, tutorial, guide, tips, ideas

BRAND DETECTION:
- If keyword contains a recognizable brand name (Armani, Dior, MAC, Nike, Apple, etc.), extract it
- Put brand name in "brand" field
- Do NOT create "Brand Specific" categories

RULES:
- {extra_instruction}
- EVERY keyword must be categorized (all {len(batch_keywords)})
- Min {min_size} keywords/category (flexible)
- Think: "WHY is the user searching this?"
- Keep "description" field SHORT (max 10 words)

JSON FORMAT:
{{
  "clusters": [
    {{
      "cluster_name": "Category from list",
      "keywords": [
        {{
          "keyword": "the keyword",
          "brand": "Brand Name or null"
        }}
      ],
      "description": "Why these share same intent"
    }}
  ]
}}"""
            else:
                prompt = f"""You are an expert SEO keyword intent analyzer.

TASK: Categorize keywords by USER SEARCH INTENT (why they're searching), NOT by product type.

KEYWORDS ({len(batch_keywords)}):
{chr(10).join(f"{i+1}. {kw}" for i, kw in enumerate(batch_keywords))}

INTENT CATEGORIZATION LOGIC:

1. **Generic**: Vague, broad searches with NO specific intent signals
   Examples: "armani lipstick", "nike shoes", "samsung phone"
   → User is just browsing, no clear goal

2. **Buy / Compare**: Contains comparison or shopping modifiers
   Examples: "best base makeup for oily skin", "top 10 laptops", "iphone vs samsung"
   → Words like: best, top, vs, comparison, review, affordable

3. **Feature or Finish**: Describes SPECIFIC attributes or characteristics
   Examples: "waterproof mascara", "bad gal 24 hour eye pencil waterproof black 0.25 g", "matte red lipstick"
   → Has detailed specs, features, colors, finishes

4. **Price Related**: Budget-focused searches
   Examples: "cheap mascara", "luxury skincare", "affordable laptop"
   → Words like: cheap, expensive, luxury, budget, affordable, under $X

5. **Problem / Solution**: Addresses a specific problem
   Examples: "mascara that doesn't smudge", "laptop for gaming", "phone with best camera"
   → User has a problem to solve

6. **Tutorial / How To**: Educational intent
   Examples: "how to apply mascara", "makeup tutorial", "nail art ideas"
   → Words like: how to, tutorial, guide, tips, ideas

7. **Application Area**: Specific use case or body part/location
   Examples: "mascara for sensitive eyes", "running shoes for flat feet"
   → Specifies WHERE/WHEN it's used

BRAND DETECTION:
- If keyword contains a recognizable brand name, extract it
- Put brand name in "brand" field
- Do NOT create "Brand Specific" categories

CREATE: 5-{max_clusters} intent categories
RULES:
- EVERY keyword must be categorized (all {len(batch_keywords)})
- Min {min_size} keywords/category (flexible)
- Think: "WHY is the user searching this?"
- Focus on INTENT, not product type
- Keep "description" field SHORT (max 10 words)

JSON FORMAT:
{{
  "clusters": [
    {{
      "cluster_name": "Intent Category Name",
      "keywords": [
        {{
          "keyword": "the keyword",
          "brand": "Brand Name or null"
        }}
      ],
      "description": "Why these share same search intent"
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

            # Delay tra batch (per sicurezza)
            if batch_idx < total_batches - 1:
                st.info("⏱️ Pausa 60s per rate limit...")
                time.sleep(60)

            result_text = (response.content[0].text if response and response.content else "").strip()
            if not result_text:
                return None, f"Batch {batch_idx+1}: risposta vuota"

            # Clean markdown fences
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            # Estrai JSON grezzo
            start = result_text.find("{")
            end = result_text.rfind("}")
            if start == -1 or end == -1:
                st.error(f"Batch {batch_idx+1}: JSON non trovato")
                st.code(result_text[:300])
                return None, "JSON invalido"

            result_text = result_text[start:end+1]

            # Tentativo di chiusura se troncato
            if not result_text.endswith("}"):
                st.warning(f"⚠️ Batch {batch_idx+1}: Risposta troncata, tentativo di recupero...")
                # Chiudi in modo conservativo
                open_brackets = result_text.count("[") - result_text.count("]")
                open_braces = result_text.count("{") - result_text.count("}")

                if open_brackets > 0:
                    result_text += "]" * open_brackets
                if open_braces > 0:
                    result_text += "}" * open_braces

            # Parse
            try:
                batch_result = json.loads(result_text)

                # validazione & normalizzazione
                if not isinstance(batch_result, dict) or 'clusters' not in batch_result:
                    st.error(f"❌ Batch {batch_idx+1}: Struttura JSON invalida")
                    st.code(result_text[:500])
                    return None, "Struttura JSON non valida"

                normalized = normalize_clusters(batch_result)
                batch_result['clusters'] = normalized

                # Conteggio
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
                    st.text(f"Lunghezza risposta: {len(result_text)} caratteri")
                    st.text(f"Aperti [: {result_text.count('[') - result_text.count(']')}")
                    st.text(f"Aperti {{: {result_text.count('{') - result_text.count('}')}")
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
            "feature_count": sum(len(c.get('keywords', [])) for c in all_clusters if 'feature' in cname(c)),
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
    elif clustering_mode == "Custom (tu definisci categorie)" and not custom_categories.strip():
        st.error("⚠️ Modalità Custom: inserisci almeno 3 categorie custom")
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
            with st.spinner('🤖 Clustering intent-based con Claude...'):
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

                st.markdown(f"""
                <div class='success-box'>
                ✅ <strong>Analisi completata!</strong><br>
                • {result['summary']['total_keywords_input']} keywords inviate<br>
                • {result['summary']['total_keywords']} keywords categorizzate<br>
                • {result['summary']['total_clusters']} categorie create<br>
                • {result['summary']['branded_count']} keywords con brand
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

    # ===== Export Excel =====
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Sheet 1: flat table
        df.to_excel(writer, sheet_name='Categories', index=False)

        # Sheet 2: summary
        summary_df = pd.DataFrame([{
            'Total Keywords Input': result['summary'].get('total_keywords_input', 0),
            'Total Keywords Categorized': result['summary'].get('total_keywords', 0),
            'Total Categories': result['summary'].get('total_clusters', 0),
            'Keywords with Brand': result['summary'].get('branded_count', 0)
        }])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # Sheet 3: category overview
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
