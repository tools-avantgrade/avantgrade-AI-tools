import streamlit as st
import requests
import pandas as pd
import time
from io import BytesIO
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse

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
    2. Insert your brand name for title branding<br>
    3. Optionally add primary keywords (one per line, matching URL order)<br>
    4. Insert your Anthropic API key<br>
    5. Click "Generate Meta Tags" - the tool will scrape each page and use Claude to generate optimized meta tags<br>
    6. Download results in Excel or CSV format
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
    
    # Brand name
    brand_name = st.text_input(
        "Brand Name",
        help="Your brand name (will be added as '| Brand' at the end of titles)",
        placeholder="e.g., AvantGrade"
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
    
    st.markdown("### 📋 SEO Guidelines")
    st.markdown("""
**Title Best Practices:**
- **MAX 60 characters** (including brand)
- Include primary keyword
- Format: "Keyword-rich title | Brand"
- Unique for each page

**Description Best Practices:**
- **MAX 150 characters** (strict limit)
- Include primary keyword naturally
- Use varied styles:
  - Descriptive statements
  - Questions (occasionally)
  - Benefits-focused
- **Always ONE clear CTA**
- Avoid overusing "Scopri"
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
    <p>Meta Tag Generator v1.1</p>
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
def extract_domain_name(url):
    """Extract clean domain name from URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        # Get main domain without TLD
        parts = domain.split('.')
        if len(parts) > 1:
            return parts[0].capitalize()
        return domain.capitalize()
    except:
        return ""

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
        
        # Extract h2 (for additional context)
        h2_tags = soup.find_all('h2')
        h2_text = ' | '.join([h2.text.strip() for h2 in h2_tags[:3]]) if h2_tags else ""
        
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
            'h2': h2_text,
            'first_paragraph': first_para,
            'error': None
        }
    
    except Exception as e:
        return {
            'success': False,
            'existing_title': '',
            'existing_description': '',
            'h1': '',
            'h2': '',
            'first_paragraph': '',
            'error': str(e)
        }

def generate_meta_tags_claude(url, page_content, primary_keyword, brand_name, api_key, retry=3):
    """Generate meta tags using Claude API with enhanced SEO prompt"""
    
    # Build enhanced prompt with strict SEO guidelines
    prompt = f"""You are an expert SEO specialist working for a premium digital marketing agency. Generate highly optimized meta title and meta description for the following webpage.

URL: {url}
Brand Name: {brand_name if brand_name else 'Extract from content'}
Primary Keyword: {primary_keyword if primary_keyword else 'Extract from content - use the most relevant keyword'}

Page Content Analysis:
- Current Title: {page_content['existing_title']}
- Current Description: {page_content['existing_description']}
- H1 Headings: {page_content['h1']}
- H2 Headings: {page_content['h2']}
- Opening Paragraph: {page_content['first_paragraph']}

CRITICAL REQUIREMENTS:

Meta Title Rules (NON-NEGOTIABLE):
1. Maximum 60 characters INCLUDING spaces and brand suffix
2. MUST end with " | {brand_name if brand_name else '[Brand]'}" format
3. Include primary keyword naturally in the first half
4. Front-load the most important keyword
5. Be specific and descriptive
6. Avoid generic words like "Best", "Top" unless truly relevant
7. Example format: "Keyword-Rich Specific Benefit | Brand"

Meta Description Rules (NON-NEGOTIABLE):
1. STRICT maximum of 150 characters INCLUDING spaces
2. MUST include exactly ONE clear call-to-action (CTA)
3. Include primary keyword naturally in the first 50 characters
4. VARY the writing style - use ONE of these approaches:
   A) Descriptive Statement + CTA (60% of cases)
      Example: "Professional SEO tools for digital marketers. Get real-time SERP data. Start your free trial."
   
   B) Question + Answer + CTA (20% of cases)
      Example: "Need reliable SEO analysis? Our AI-powered tools deliver instant insights. Try it free today."
   
   C) Benefit-Focused + CTA (20% of cases)
      Example: "Save 10 hours weekly with automated keyword research and competitor analysis. Get started now."

5. AVOID overusing "Scopri" - use varied CTAs:
   - "Prova ora" / "Try now"
   - "Inizia gratis" / "Start free"
   - "Richiedi demo" / "Request demo"
   - "Leggi di più" / "Learn more"
   - "Scarica la guida" / "Download guide"
   - "Contattaci" / "Contact us"
   - "Ottieni accesso" / "Get access"
   
6. Be specific about benefits, not vague
7. Use active voice
8. Include numbers when relevant (e.g., "Save 50%", "10+ features")
9. Make it compelling and clickworthy
10. Ensure exactly ONE CTA per description - never multiple CTAs

OUTPUT FORMAT:
Return ONLY a valid JSON object with NO markdown, NO backticks, NO additional text:
{{"meta_title": "your title here | {brand_name if brand_name else 'Brand'}", "meta_description": "your description here with ONE CTA"}}

Remember: 
- Title MAX 60 chars (including brand suffix with " | Brand")
- Description MAX 150 chars
- ONE CTA only in description
- Vary description style (descriptive, question-based, benefit-focused)
- Do NOT always use "Scopri" - vary your CTAs
- Be specific and benefit-oriented
- Count your characters carefully before outputting"""

    for attempt in range(retry):
        try:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            payload = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 600,
                "temperature": 0.7,  # Slightly higher for varied outputs
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
                
                meta_title = result.get('meta_title', '')
                meta_description = result.get('meta_description', '')
                
                # Validation checks
                if len(meta_title) > 60:
                    meta_title = meta_title[:57] + "..."
                
                if len(meta_description) > 150:
                    meta_description = meta_description[:147] + "..."
                
                # Ensure brand suffix in title
                if brand_name and f"| {brand_name}" not in meta_title:
                    # Try to add brand if space allows
                    base_title = meta_title.replace(f"| {brand_name}", "").strip()
                    if len(base_title) + len(f" | {brand_name}") <= 60:
                        meta_title = f"{base_title} | {brand_name}"
                
                return {
                    'success': True,
                    'meta_title': meta_title,
                    'meta_description': meta_description,
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
    
    if not brand_name:
        st.warning("⚠️ Brand name not specified. Will attempt to extract from domain.")
    
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
        
        # Extract brand from domain if not provided
        current_brand = brand_name if brand_name else extract_domain_name(url)
        
        # Step 1: Scrape page content
        page_content = scrape_page_content(url)
        
        if not page_content['success']:
            results.append({
                'URL': url,
                'Primary Keyword': keyword,
                'Brand': current_brand,
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
            brand_name=current_brand,
            api_key=api_key,
            retry=retry_attempts
        )
        
        if meta_result['success']:
            meta_title = meta_result['meta_title']
            meta_desc = meta_result['meta_description']
            
            results.append({
                'URL': url,
                'Primary Keyword': keyword if keyword else 'Auto-extracted',
                'Brand': current_brand,
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
                'Brand': current_brand,
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
        
        # Check title lengths (strict 60 max)
        long_titles = df[(df['Status'] == 'Success') & (df['Title Length'] > 60)]
        if len(long_titles) > 0:
            issues.append(f"⚠️ {len(long_titles)} title(s) exceed 60 characters")
        
        # Check description lengths (strict 150 max)
        long_descs = df[(df['Status'] == 'Success') & (df['Description Length'] > 150)]
        if len(long_descs) > 0:
            issues.append(f"⚠️ {len(long_descs)} description(s) exceed 150 characters")
        
        # Check for brand suffix in titles
        if brand_name:
            missing_brand = df[(df['Status'] == 'Success') & (~df['Meta Title'].str.contains(f"| {brand_name}", case=False, na=False))]
            if len(missing_brand) > 0:
                issues.append(f"⚠️ {len(missing_brand)} title(s) missing brand suffix '| {brand_name}'")
        
        if issues:
            st.markdown("### ⚠️ Quality Warnings")
            for issue in issues:
                st.warning(issue)
        else:
            st.success("✅ All meta tags meet SEO quality standards!")
        
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
    <p style='font-size: 0.85em; margin-top: 0.5rem;'>v1.1 - Enhanced SEO Optimization</p>
</div>
""", unsafe_allow_html=True)
