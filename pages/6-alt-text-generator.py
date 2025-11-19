import streamlit as st
import requests
import pandas as pd
import time
from io import BytesIO

# Configurazione pagina
st.set_page_config(
    page_title="Alt Text Generator - AvantGrade.com",
    page_icon="🖼️",
    layout="wide"
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
    
    h1, h2, h3, p, label, .stMarkdown {
        color: #ffffff !important;
    }
    
    .header-container {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(255, 107, 53, 0.3);
    }
    
    .header-container h1 {
        color: #000000 !important;
        font-weight: 900;
        margin: 0;
        font-size: 2.5em;
    }
    
    .header-container p {
        color: #1a1a1a !important;
        margin: 0.5rem 0 0 0;
        font-size: 1.1em;
    }
    
    .info-box {
        background: #1a1a1a;
        border-left: 4px solid #F7931E;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    
    .warning-box {
        background: #2a1a1a;
        border-left: 4px solid #ff4444;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    
    .success-box {
        background: #1a2a1a;
        border-left: 4px solid #44ff44;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    
    div[data-testid="stDataFrame"] {
        background-color: #0a0a0a;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class='header-container'>
    <h1>🖼️ Alt Text Generator</h1>
    <p>Generate SEO-optimized alt text for images using OpenAI Vision API</p>
</div>
""", unsafe_allow_html=True)

# Info box
st.markdown("""
<div class='info-box'>
    <strong>ℹ️ How it works:</strong><br>
    1. Paste image URLs (one per line) in the textarea below<br>
    2. Insert your OpenAI API key<br>
    3. Click "Generate Alt Text" and wait for processing<br>
    4. Download results in Excel or CSV format
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    
    # API Key input
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Your OpenAI API key (required for Vision API)",
        placeholder="sk-..."
    )
    
    st.markdown("---")
    
    st.markdown("### 📋 Instructions")
    st.markdown("""
**Supported formats:**
- JPEG, PNG, GIF, WebP
- Public URLs only
- Max 100 images per batch

**Alt Text Guidelines:**
- Concise and descriptive
- 5-15 words optimal
- Includes key objects and context
- SEO-optimized
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔗 Resources")
    st.markdown("""
[Get OpenAI API Key](https://platform.openai.com/api-keys)

[OpenAI Pricing](https://openai.com/api/pricing/)
    """)
    
    st.markdown("---")
    
    st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.85em; margin-top: 2rem;'>
    <p><strong>AvantGrade.com</strong></p>
    <p>Alt Text Generator v1.0</p>
</div>
    """, unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📸 Image URLs Input")
    
    image_urls = st.text_area(
        "Paste image URLs here (one per line)",
        height=300,
        placeholder="https://example.com/image1.jpg\nhttps://example.com/image2.png\nhttps://example.com/image3.webp",
        help="Enter one image URL per line"
    )

with col2:
    st.markdown("### 🎯 Options")
    
    prompt_template = st.text_area(
        "Custom Prompt (optional)",
        value="Provide a functional and objective description of this image in no more than 15 words. Follow the pattern 'object-action-context' where: the object is the main focal point, the action describes what's happening, and the context describes the surrounding environment. If there is text in the image, transcribe it completely. Do not start with variations of 'The image shows'.",
        height=200,
        help="Customize the prompt sent to OpenAI"
    )
    
    max_tokens = st.slider(
        "Max Tokens",
        min_value=50,
        max_value=200,
        value=100,
        step=10,
        help="Maximum length of generated alt text"
    )

# Generate button
st.markdown("---")

if st.button("🚀 Generate Alt Text", type="primary", use_container_width=True):
    
    # Validation
    if not api_key:
        st.error("❌ Please insert your OpenAI API key in the sidebar")
        st.stop()
    
    if not image_urls.strip():
        st.error("❌ Please insert at least one image URL")
        st.stop()
    
    # Parse URLs
    urls = [url.strip() for url in image_urls.strip().split('\n') if url.strip()]
    
    if len(urls) == 0:
        st.error("❌ No valid URLs found")
        st.stop()
    
    if len(urls) > 100:
        st.warning(f"⚠️ {len(urls)} URLs detected. Processing only first 100 URLs.")
        urls = urls[:100]
    
    st.success(f"✅ Found {len(urls)} image URL(s) to process")
    
    # Process images
    results = []
    errors = []
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, url in enumerate(urls):
        status_text.text(f"Processing image {idx+1}/{len(urls)}...")
        
        try:
            # Call OpenAI Vision API
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_template
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": url
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                alt_text = data['choices'][0]['message']['content'].strip()
                
                # Remove trailing period if present
                if alt_text.endswith('.'):
                    alt_text = alt_text[:-1]
                
                results.append({
                    'Image URL': url,
                    'Alt Text': alt_text,
                    'Status': 'Success',
                    'Character Count': len(alt_text),
                    'Word Count': len(alt_text.split())
                })
            else:
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_detail = response.json().get('error', {}).get('message', '')
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    pass
                
                results.append({
                    'Image URL': url,
                    'Alt Text': '',
                    'Status': f'Failed: {error_msg}',
                    'Character Count': 0,
                    'Word Count': 0
                })
                errors.append(url)
        
        except Exception as e:
            results.append({
                'Image URL': url,
                'Alt Text': '',
                'Status': f'Failed: {str(e)}',
                'Character Count': 0,
                'Word Count': 0
            })
            errors.append(url)
        
        # Update progress
        progress_bar.progress((idx + 1) / len(urls))
        
        # Rate limiting delay (avoid hitting API limits)
        if idx < len(urls) - 1:
            time.sleep(0.5)
    
    status_text.empty()
    progress_bar.empty()
    
    # Display results
    st.markdown("---")
    st.markdown("## 📊 Results")
    
    if results:
        df = pd.DataFrame(results)
        
        # Success/failure stats
        success_count = len([r for r in results if r['Status'] == 'Success'])
        failure_count = len(errors)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("✅ Successful", success_count)
        
        with col2:
            st.metric("❌ Failed", failure_count)
        
        with col3:
            avg_chars = df[df['Status'] == 'Success']['Character Count'].mean() if success_count > 0 else 0
            st.metric("📏 Avg Characters", f"{avg_chars:.0f}")
        
        st.markdown("---")
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )
        
        # Store in session state
        st.session_state['alt_text_results'] = df
        
        # Download section
        st.markdown("---")
        st.markdown("### 📥 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel download
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Alt Text Results')
            
            st.download_button(
                label="📊 Download Excel",
                data=excel_buffer.getvalue(),
                file_name="alt_text_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            # CSV download
            csv = df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name="alt_text_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Errors summary
        if errors:
            st.markdown("---")
            st.markdown("### ⚠️ Failed URLs")
            st.markdown(f"The following {len(errors)} URL(s) could not be processed:")
            for error_url in errors:
                st.text(f"• {error_url}")

# Display previous results if available
elif 'alt_text_results' in st.session_state:
    st.markdown("---")
    st.markdown("## 📊 Previous Results")
    
    df = st.session_state['alt_text_results']
    
    st.dataframe(
        df,
        use_container_width=True,
        height=400
    )
    
    # Download section
    st.markdown("---")
    st.markdown("### 📥 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Excel download
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Alt Text Results')
        
        st.download_button(
            label="📊 Download Excel",
            data=excel_buffer.getvalue(),
            file_name="alt_text_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # CSV download
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name="alt_text_results.csv",
            mime="text/csv",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>AvantGrade.com</strong> • Alt Text Generator</p>
    <p>Powered by OpenAI Vision API • Professional SEO Tools Suite</p>
</div>
""", unsafe_allow_html=True)
