import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import urllib3
from datetime import datetime
import io
import pyperclip

# Disabilita SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configurazione pagina
st.set_page_config(
    page_title="Competitor Content Analyzer",
    page_icon="🕷️",
    layout="wide"
)

# CSS personalizzato
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #000000 0%, #1a0a00 100%);
    }
    
    h1, h2, h3, p, label {
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        background: #1a1a1a;
        color: #ffffff;
        border: 2px solid #FF6B35;
        border-radius: 10px;
        margin: 5px;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: #FF6B35;
        color: #000;
    }
    
    .metric-box {
        background: rgba(255, 107, 53, 0.1);
        border-left: 4px solid #FF6B35;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🕷️ Competitor Content Analyzer")
st.markdown("Analizza la struttura SEO dei competitor estraendo title, meta description, heading tags e altro.")

# ======================== FORM INPUT ========================
with st.expander("📝 Configura Analisi", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        primary_keyword = st.text_input(
            "🎯 Primary Keyword",
            placeholder="es. Ristoranti panoramici Roma",
            help="La keyword principale che analizzerai"
        )
    
    with col2:
        secondary_keywords_input = st.text_input(
            "🔑 Secondary Keywords (separate da virgola)",
            placeholder="es. Rooftop Roma, Terrazza con vista, Best restaurants",
            help="Keywords correlate per il context"
        )
    
    notes = st.text_area(
        "📌 Note e Struttura di Riferimento",
        placeholder="Inserisci note sul progetto, competitor, o structure da seguire...",
        height=100
    )
    
    st.markdown("**📋 Inserisci URL Competitor**")
    
    # Textarea per incollare URL riga per riga
    urls_textarea = st.text_area(
        "Incolla gli URL (uno per riga)",
        placeholder="https://example.com/1\nhttps://example.com/2\nhttps://example.com/3",
        height=150,
        help="Puoi incollare direttamente da un file o da una lista. Ogni URL su una riga nuova."
    )
    
    # Processa gli URL dalla textarea
    if urls_textarea:
        urls_list_preview = [url.strip() for url in urls_textarea.split('\n') if url.strip()]
        st.success(f"✓ {len(urls_list_preview)} URL rilevati")
        
        # Mostra preview degli URL
        with st.expander("👁️ Anteprima URL"):
            for idx, url in enumerate(urls_list_preview, 1):
                st.caption(f"{idx}. {url}")

# ======================== FUNZIONI ANALISI ========================
def extract_metadata(url):
    """Estrae metadata da un URL"""
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Rimuovi header, footer, aside
        for element in soup.find_all(['header', 'footer', 'aside', 'script', 'style']):
            element.decompose()
        
        # Estrai dati
        meta_title = soup.find('title').text if soup.find('title') else "N/A"
        meta_desc_elem = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc_elem['content'] if meta_desc_elem and 'content' in meta_desc_elem.attrs else "N/A"
        
        h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
        h2_tags = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]
        h3_tags = [h3.get_text(strip=True) for h3 in soup.find_all('h3')]
        
        # Estrai immagini
        images = soup.find_all('img')
        img_data = [
            {
                'alt': img.get('alt', 'N/A'),
                'src': img.get('src', 'N/A'),
                'title': img.get('title', 'N/A')
            }
            for img in images
        ]
        
        return {
            'url': url,
            'title': meta_title,
            'description': meta_description,
            'h1_tags': h1_tags,
            'h2_tags': h2_tags,
            'h3_tags': h3_tags,
            'images_count': len(images),
            'images_data': img_data,
            'status': '✓ Success'
        }
    
    except requests.exceptions.Timeout:
        return {'url': url, 'status': '❌ Timeout'}
    except requests.exceptions.RequestException as e:
        return {'url': url, 'status': f'❌ Errore: {str(e)[:30]}'}

# ======================== BOTTONE ANALIZZA ========================
if st.button("🚀 Avvia Analisi", type="primary", use_container_width=True):
    
    # Validazione
    urls_list = [url.strip() for url in urls_textarea.split('\n') if url.strip()]
    
    if not urls_list:
        st.error("❌ Incolla almeno un URL valido nella textarea")
    elif not primary_keyword:
        st.error("❌ Inserisci una primary keyword")
    else:
        # Mostra info configurazione
        st.info(f"""
        **Configurazione Analisi:**
        - 🎯 Primary Keyword: {primary_keyword}
        - 🔑 Secondary Keywords: {secondary_keywords_input if secondary_keywords_input else 'Nessuna'}
        - 📊 URL da analizzare: {len(urls_list)}
        """)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Raccogli risultati
        results = []
        
        for idx, url in enumerate(urls_list):
            status_text.text(f"Analizzando {idx+1}/{len(urls_list)}: {url[:50]}...")
            result = extract_metadata(url)
            if result:
                results.append(result)
            progress_bar.progress((idx + 1) / len(urls_list))
        
        status_text.text("✓ Analisi completata!")
        
        # ======================== TABS RISULTATI ========================
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏷️ Meta Tags",
            "📸 Immagini",
            "📊 Statistiche",
            "💾 Download"
        ])
        
        # TAB 1: META TAGS (NUOVO RIEPILOGO)
        with tab1:
            st.markdown("### 🏷️ Meta Tags & Heading Structure")
            
            # Genera testo copiabile COMPLETO per tutti gli URL
            all_copy_text = f"""ANALISI COMPETITOR - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
{'='*80}
🎯 PRIMARY KEYWORD: {primary_keyword}
🔑 SECONDARY KEYWORDS: {secondary_keywords_input if secondary_keywords_input else 'Nessuna'}
📌 NOTE: {notes if notes else 'Nessuna nota'}
{'='*80}

"""
            
            for result in results:
                if result['status'] != '✓ Success':
                    st.warning(f"{result['url']} - {result['status']}")
                    continue
                
                # Aggiungi a testo completo
                all_copy_text += f"""
{'─'*80}
📍 URL: {result['url']}
{'─'*80}

🔤 META TITLE ({len(result['title'])} char):
{result['title']}

📝 META DESCRIPTION ({len(result['description'])} char):
{result['description']}

📌 H1 TAGS ({len(result['h1_tags'])} trovati):
{chr(10).join(result['h1_tags']) if result['h1_tags'] else 'Nessun H1 trovato'}

📌 H2 TAGS ({len(result['h2_tags'])} trovati):
{chr(10).join(result['h2_tags']) if result['h2_tags'] else 'Nessun H2 trovato'}

📌 H3 TAGS ({len(result['h3_tags'])} trovati):
{chr(10).join(result['h3_tags']) if result['h3_tags'] else 'Nessun H3 trovato'}

"""
                
                with st.expander(f"📑 {result['url']}", expanded=False):
                    # Title e Meta Description
                    st.markdown("**🔤 Meta Title**")
                    st.code(result['title'])
                    st.caption(f"Lunghezza: {len(result['title'])} caratteri")
                    
                    st.markdown("**📝 Meta Description**")
                    st.code(result['description'])
                    st.caption(f"Lunghezza: {len(result['description'])} caratteri")
                    
                    st.divider()
                    
                    # H1 Tags
                    st.markdown("**H1 Tags**")
                    if result['h1_tags']:
                        for h1 in result['h1_tags']:
                            st.write(f"→ {h1}")
                    else:
                        st.warning("❌ Nessun H1 trovato")
                    
                    st.divider()
                    
                    # H2 Tags
                    st.markdown("**H2 Tags**")
                    if result['h2_tags']:
                        for h2 in result['h2_tags']:
                            st.write(f"→ {h2}")
                    else:
                        st.write("Nessun H2 trovato")
                    
                    st.divider()
                    
                    # H3 Tags
                    st.markdown("**H3 Tags**")
                    if result['h3_tags']:
                        for h3 in result['h3_tags']:
                            st.write(f"→ {h3}")
                    else:
                        st.write("Nessun H3 trovato")
            
            # Output Completo - Soluzione Pulita
            st.markdown("---")
            st.markdown("### 📄 Output Completo")
            
            # Usa st.text_area() nativo di Streamlit
            st.text_area(
                "Testo copiabile - Seleziona tutto e copia (Ctrl+C / Cmd+C)",
                value=all_copy_text,
                height=400,
                disabled=True,
                key="output_textarea"
            )
            
            # Pulsanti download
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Scarica TXT",
                    data=all_copy_text,
                    file_name=f"competitor_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                st.info("💡 Seleziona il testo sopra e premi Ctrl+C (o Cmd+C) per copiare")
        
        # TAB 2: IMMAGINI
        with tab2:
            st.markdown("### 📸 Analisi Immagini (ALT Tags)")
            
            for result in results:
                if result['status'] != '✓ Success':
                    continue
                
                with st.expander(f"🖼️ {result['url']} ({result['images_count']} immagini)", expanded=False):
                    if result['images_data']:
                        for idx, img in enumerate(result['images_data'][:10], 1):
                            col_img_num, col_img_alt = st.columns([1, 5])
                            
                            with col_img_num:
                                st.write(f"**{idx}.**")
                            
                            with col_img_alt:
                                st.markdown(f"**Alt:** {img['alt']}")
                                if img['title']:
                                    st.caption(f"Title: {img['title']}")
                        
                        if len(result['images_data']) > 10:
                            st.info(f"... e altri {len(result['images_data']) - 10} tag immagine")
                    else:
                        st.warning("Nessuna immagine trovata")
        
        # TAB 3: STATISTICHE
        with tab3:
            st.markdown("### 📊 Statistiche Comparative")
            
            stats_data = []
            for result in results:
                if result['status'] == '✓ Success':
                    stats_data.append({
                        'URL': result['url'][:40],
                        'Title Length': len(result['title']),
                        'Meta Length': len(result['description']),
                        'H1 Count': len(result['h1_tags']),
                        'H2 Count': len(result['h2_tags']),
                        'H3 Count': len(result['h3_tags']),
                        'Images': result['images_count']
                    })
            
            if stats_data:
                df_stats = pd.DataFrame(stats_data)
                st.dataframe(df_stats, use_container_width=True)
                
                # Metriche chiave
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                
                with col_m1:
                    avg_title = df_stats['Title Length'].mean()
                    st.metric("Avg Title Length", f"{avg_title:.0f} char")
                
                with col_m2:
                    avg_meta = df_stats['Meta Length'].mean()
                    st.metric("Avg Meta Length", f"{avg_meta:.0f} char")
                
                with col_m3:
                    avg_h1 = df_stats['H1 Count'].mean()
                    st.metric("Avg H1 Tags", f"{avg_h1:.1f}")
                
                with col_m4:
                    total_img = df_stats['Images'].sum()
                    st.metric("Total Images", f"{total_img}")
        
        # TAB 4: DOWNLOAD
        with tab4:
            st.markdown("### 💾 Scarica Risultati")
            
            # Prepara DataFrame per export
            export_data = []
            for result in results:
                if result['status'] == '✓ Success':
                    export_data.append({
                        'URL': result['url'],
                        'Meta Title': result['title'],
                        'Meta Description': result['description'],
                        'H1 Tags': ' | '.join(result['h1_tags']),
                        'H2 Tags': ' | '.join(result['h2_tags']),
                        'H3 Tags': ' | '.join(result['h3_tags']),
                        'Images Count': result['images_count']
                    })
            
            if export_data:
                df_export = pd.DataFrame(export_data)
                
                # Download Excel
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_export.to_excel(writer, sheet_name='Competitor Analysis', index=False)
                    
                    # Sheet immagini
                    img_sheet_data = []
                    for result in results:
                        if result['status'] == '✓ Success' and result['images_data']:
                            for img in result['images_data']:
                                img_sheet_data.append({
                                    'URL Pagina': result['url'],
                                    'Alt Text': img['alt'],
                                    'Src': img['src'],
                                    'Title': img['title']
                                })
                    
                    if img_sheet_data:
                        df_images = pd.DataFrame(img_sheet_data)
                        df_images.to_excel(writer, sheet_name='Images Analysis', index=False)
                
                excel_buffer.seek(0)
                
                st.download_button(
                    label="📥 Scarica Excel Report",
                    data=excel_buffer,
                    file_name=f"competitor_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Download CSV
                csv_buffer = df_export.to_csv(index=False).encode('utf-8-sig')
                
                st.download_button(
                    label="📊 Scarica CSV",
                    data=csv_buffer,
                    file_name=f"competitor_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ Nessun dato da esportare")
        
        # Footer con info
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #999999; font-size: 0.9em; margin-top: 2rem;'>
            <p>✓ Analisi completata con successo</p>
            <p>Scarica i dati e integra i risultati nella tua strategia SEO</p>
        </div>
        """, unsafe_allow_html=True)