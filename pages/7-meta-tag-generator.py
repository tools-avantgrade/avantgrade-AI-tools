import streamlit as st
import requests
import pandas as pd
import time
from io import BytesIO
from bs4 import BeautifulSoup
import json

# Configurazione pagina
st.set_page_config(
    page_title="Meta Tag Generator - AvantGrade.com",
    page_icon="📝",
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
    <h1>📝 Meta Tag Generator</h1>
    <p>AI-powered meta title & description generator using Claude Sonnet 4.5</p>
</div>
""", unsafe_allow_html=True)

# Info box
st.markdown("""
<div class='info-box'>
    <strong>ℹ️ How it works:</strong><br>
    1. Paste page URLs (one per line) in the textarea below<br>
    2. Optionally add primary keywords (one per line, matching URL order)<br>
    3. Insert your Anthropic API key<br>
    4. Click "Generate Meta Tags" - the tool will scrape each page and use Claude to generate optimized meta tags<br>
    5. Download results in Excel or CSV format
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    
    # API Key input
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        help="Your Anthropic API key (required for Claude)",
        placeholder="sk-ant-..."
    )
    
    st.markdown("---")
    
    # Advanced settings
    st.markdown("### 🎯 Advanced Settings")
    
    batch_size = st.slider(
        "Batch Size",
        min_value=5,
        max_value=20,
        value=10,
        step=5,
        help="Number of URLs to process simultaneously (lower = safer for rate limits)"
    )
    
    retry_attempts = st.slider(
        "Retry Attempts",
        min_value=1,
        max_value=5,
        value=3,
        help="Number of retry attempts for failed requests"
    )
    
    request_delay = st.slider(
        "Request Delay (seconds)",
        min_value=0.5,
        max_value=3.0,
        value=1.0,
        step=0.5,
        help="Delay between API calls to avoid rate limiting"
    )
    
    st.markdown("---")
    
    st.markdown("### 📋 Meta Tag Guidelines")
    st.markdown("""
**Title Best Practices:**
- 55-60 characters optimal
- Include primary keyword
- Brand at the end (optional)
- Unique for each page

**Description Best Practices:**
- 150-160 characters optimal
- Include primary & secondary keywords
- Compelling call-to-action
- Accurate page summary
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔗 Resources")
    st.markdown("""
[Get Anthropic API Key](https://console.anthropic.com/)

[Claude Pricing](https://www.anthropic.com/pricing)
    """)
    
    st.markdown("---")
    
    st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.85em; margin-top: 2rem;'>
    <p><strong>AvantGrade.com</strong></p>
    <p>Meta Tag Generator v1.0</p>
</div>
    """, unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 🌐 Page URLs Input")
    
    page_urls = st.text_area(
        "Paste page URLs here (one per line)",
        height=300,
        placeholder="https://example.com/page1\nhttps://example.com/page2\nhttps://example.com/page3",
        help="Enter one URL per line. Supports up to 1000+ URLs with smart batching."
    )

with col2:
    st.markdown("### 🎯 Primary Keywords (Optional)")
    
    keywords = st.text_area(
        "Primary keywords for each URL (one per line)",
        height=300,
        placeholder="best smartphones 2025\ndigital marketing tips\nSEO tools",
        help="Optional: Enter one keyword per line, matching the order of URLs. Leave empty for automatic keyword extraction."
    )

# Helper functions
def scrape_page_content(url, timeout=10):
    """Scrape page content for meta tag generation"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract existing meta tags
        existing_title = soup.find('title')
        existing_title = existing_title.text.strip() if existing_title else ""
        
        existing_description = soup.find('meta', attrs={'name': 'description'})
        existing_description = existing_description.get('content', '').strip() if existing_description else ""
        
        # Extract h1
        h1_tags = soup.find_all('h1')
        h1_text = ' | '.join([h1.text.strip() for h1 in h1_tags[:3]]) if h1_tags else ""
        
        # Extract first paragraph
        paragraphs = soup.find_all('p')
        first_para = ""
        for p in paragraphs:
            text = p.text.strip()
            if len(text) > 50:  # Skip very short paragraphs
                first_para = text[:500]  # Limit to 500 chars
                break
        
        return {
            'success': True,
            'existing_title': existing_title,
            'existing_description': existing_description,
            'h1': h1_text,
            'first_paragraph': first_para,
            'error': None
        }
    
    except Exception as e:
        return {
            'success': False,
            'existing_title': '',
            'existing_description': '',
            'h1': '',
            'first_paragraph': '',
            'error': str(e)
        }

def generate_meta_tags_claude(url, page_content, primary_keyword, api_key, retry=3):
    """Generate meta tags using Claude API"""
    
    # Build prompt
    prompt = f"""You are an expert SEO specialist. Generate optimized meta title and meta description for the following webpage.

URL: {url}
Primary Keyword: {primary_keyword if primary_keyword else 'Not specified - extract from content'}

Page Content:
- Existing Title: {page_content['existing_title']}
- Existing Description: {page_content['existing_description']}
- H1 Tags: {page_content['h1']}
- First Paragraph: {page_content['first_paragraph']}

Requirements:
1. Meta Title: 55-60 characters (STRICT - must be between 55-60 chars)
2. Meta Description: 150-160 characters (STRICT - must be between 150-160 chars)
3. Include primary keyword naturally if provided
4. Make it compelling and click-worthy
5. Ensure accuracy to page content
6. Use active voice and clear language

Return ONLY a valid JSON object with this exact structure (no markdown, no backticks, no additional text):
{{"meta_title": "your title here", "meta_description": "your description here"}}"""

    for attempt in range(retry):
        try:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            payload = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['content'][0]['text'].strip()
                
                # Clean up response (remove markdown if present)
                content = content.replace('```json', '').replace('```', '').strip()
                
                # Parse JSON
                result = json.loads(content)
                
                return {
                    'success': True,
                    'meta_title': result.get('meta_title', ''),
                    'meta_description': result.get('meta_description', ''),
                    'error': None
                }
            
            elif response.status_code == 429:
                # Rate limit hit - wait and retry
                wait_time = (attempt + 1) * 5
                time.sleep(wait_time)
                continue
            
            else:
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_detail = response.json().get('error', {}).get('message', '')
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    pass
                
                if attempt < retry - 1:
                    time.sleep(2)
                    continue
                else:
                    return {
                        'success': False,
                        'meta_title': '',
                        'meta_description': '',
                        'error': error_msg
                    }
        
        except json.JSONDecodeError as e:
            if attempt < retry - 1:
                time.sleep(2)
                continue
            else:
                return {
                    'success': False,
                    'meta_title': '',
                    'meta_description': '',
                    'error': f"JSON Parse Error: {str(e)}"
                }
        
        except Exception as e:
            if attempt < retry - 1:
                time.sleep(2)
                continue
            else:
                return {
                    'success': False,
                    'meta_title': '',
                    'meta_description': '',
                    'error': str(e)
                }
    
    return {
        'success': False,
        'meta_title': '',
        'meta_description': '',
        'error': 'Max retries exceeded'
    }

# Generate button
st.markdown("---")

if st.button("🚀 Generate Meta Tags", type="primary", use_container_width=True):
    
    # Validation
    if not api_key:
        st.error("❌ Please insert your Anthropic API key in the sidebar")
        st.stop()
    
    if not page_urls.strip():
        st.error("❌ Please insert at least one page URL")
        st.stop()
    
    # Parse URLs and keywords
    urls = [url.strip() for url in page_urls.strip().split('\n') if url.strip()]
    keyword_list = [kw.strip() for kw in keywords.strip().split('\n') if kw.strip()] if keywords.strip() else []
    
    if len(urls) == 0:
        st.error("❌ No valid URLs found")
        st.stop()
    
    # Match keywords to URLs (or leave empty)
    if keyword_list and len(keyword_list) != len(urls):
        st.warning(f"⚠️ {len(urls)} URLs but {len(keyword_list)} keywords. Mismatched entries will use automatic keyword extraction.")
    
    # Ensure keyword list matches URL list length
    while len(keyword_list) < len(urls):
        keyword_list.append("")
    
    st.success(f"✅ Processing {len(urls)} URL(s)")
    
    # Process URLs
    results = []
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    stats_container = st.empty()
    
    total_urls = len(urls)
    processed = 0
    successful = 0
    failed = 0
    
    for idx, (url, keyword) in enumerate(zip(urls, keyword_list)):
        status_text.text(f"🔄 Processing {idx+1}/{total_urls}: {url[:50]}...")
        
        # Step 1: Scrape page content
        page_content = scrape_page_content(url)
        
        if not page_content['success']:
            results.append({
                'URL': url,
                'Primary Keyword': keyword,
                'Meta Title': '',
                'Meta Description': '',
                'Title Length': 0,
                'Description Length': 0,
                'Status': f'Scraping Failed: {page_content["error"]}'
            })
            failed += 1
            processed += 1
            progress_bar.progress(processed / total_urls)
            
            # Update stats
            stats_container.markdown(f"""
            **Progress:** {processed}/{total_urls} | ✅ Success: {successful} | ❌ Failed: {failed}
            """)
            
            continue
        
        # Step 2: Generate meta tags with Claude
        meta_result = generate_meta_tags_claude(
            url=url,
            page_content=page_content,
            primary_keyword=keyword,
            api_key=api_key,
            retry=retry_attempts
        )
        
        if meta_result['success']:
            meta_title = meta_result['meta_title']
            meta_desc = meta_result['meta_description']
            
            results.append({
                'URL': url,
                'Primary Keyword': keyword if keyword else 'Auto-extracted',
                'Meta Title': meta_title,
                'Meta Description': meta_desc,
                'Title Length': len(meta_title),
                'Description Length': len(meta_desc),
                'Status': 'Success'
            })
            successful += 1
        else:
            results.append({
                'URL': url,
                'Primary Keyword': keyword,
                'Meta Title': '',
                'Meta Description': '',
                'Title Length': 0,
                'Description Length': 0,
                'Status': f'Generation Failed: {meta_result["error"]}'
            })
            failed += 1
        
        processed += 1
        
        # Update progress
        progress_bar.progress(processed / total_urls)
        
        # Update stats
        stats_container.markdown(f"""
        **Progress:** {processed}/{total_urls} | ✅ Success: {successful} | ❌ Failed: {failed}
        """)
        
        # Delay between requests
        if idx < len(urls) - 1:
            time.sleep(request_delay)
    
    status_text.empty()
    progress_bar.empty()
    stats_container.empty()
    
    # Display results
    st.markdown("---")
    st.markdown("## 📊 Results")
    
    if results:
        df = pd.DataFrame(results)
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("✅ Successful", successful)
        
        with col2:
            st.metric("❌ Failed", failed)
        
        with col3:
            avg_title = df[df['Status'] == 'Success']['Title Length'].mean() if successful > 0 else 0
            st.metric("📏 Avg Title Length", f"{avg_title:.0f}")
        
        with col4:
            avg_desc = df[df['Status'] == 'Success']['Description Length'].mean() if successful > 0 else 0
            st.metric("📏 Avg Desc Length", f"{avg_desc:.0f}")
        
        st.markdown("---")
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )
        
        # Store in session state
        st.session_state['meta_tag_results'] = df
        
        # Quality check warnings
        issues = []
        
        # Check title lengths
        short_titles = df[(df['Status'] == 'Success') & (df['Title Length'] < 55)]
        long_titles = df[(df['Status'] == 'Success') & (df['Title Length'] > 60)]
        
        if len(short_titles) > 0:
            issues.append(f"⚠️ {len(short_titles)} title(s) are too short (<55 chars)")
        
        if len(long_titles) > 0:
            issues.append(f"⚠️ {len(long_titles)} title(s) are too long (>60 chars)")
        
        # Check description lengths
        short_descs = df[(df['Status'] == 'Success') & (df['Description Length'] < 150)]
        long_descs = df[(df['Status'] == 'Success') & (df['Description Length'] > 160)]
        
        if len(short_descs) > 0:
            issues.append(f"⚠️ {len(short_descs)} description(s) are too short (<150 chars)")
        
        if len(long_descs) > 0:
            issues.append(f"⚠️ {len(long_descs)} description(s) are too long (>160 chars)")
        
        if issues:
            st.markdown("### ⚠️ Quality Warnings")
            for issue in issues:
                st.warning(issue)
        
        # Download section
        st.markdown("---")
        st.markdown("### 📥 Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel download
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Meta Tags')
            
            st.download_button(
                label="📊 Download Excel",
                data=excel_buffer.getvalue(),
                file_name="meta_tags_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            # CSV download
            csv = df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv,
                file_name="meta_tags_results.csv",
                mime="text/csv",
                use_container_width=True
            )

# Display previous results if available
elif 'meta_tag_results' in st.session_state:
    st.markdown("---")
    st.markdown("## 📊 Previous Results")
    
    df = st.session_state['meta_tag_results']
    
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
            df.to_excel(writer, index=False, sheet_name='Meta Tags')
        
        st.download_button(
            label="📊 Download Excel",
            data=excel_buffer.getvalue(),
            file_name="meta_tags_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # CSV download
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name="meta_tags_results.csv",
            mime="text/csv",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>AvantGrade.com</strong> • Meta Tag Generator</p>
    <p>Powered by Claude Sonnet 4.5 • Professional SEO Tools Suite</p>
</div>
""", unsafe_allow_html=True)
