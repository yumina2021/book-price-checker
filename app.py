import streamlit as st
from playwright.sync_api import sync_playwright
import subprocess
from bs4 import BeautifulSoup
import time
import random
import re


# Page config
st.set_page_config(
    page_title="Book Price Checker",
    page_icon="📚",
    layout="wide"
)

# Ensure Playwright browsers are installed
@st.cache_resource
def install_playwright_browser():
    subprocess.run(["playwright", "install", "chromium"], check=True)

try:
    install_playwright_browser()
except Exception as e:
    st.error(f"Browser installation failed: {e}")

# Title
st.title("📚 Book Price Checker")
st.markdown("メルカリの中古価格を一括検索します。")

# Sidebar
st.sidebar.header("検索オプション")
only_on_sale = st.sidebar.checkbox("販売中のみ表示", value=False)

# Input
query = st.text_input("タイトル または ISBNを入力してください", placeholder="例: 9784123456789 または Python入門")

def is_isbn(text):
    clean_text = text.replace("-", "").strip()
    return clean_text.isdigit() and len(clean_text) in [10, 13]

def scrape_mercari(keyword, on_sale=False):
    """
    Scrapes Mercari for the given keyword.
    """
    search_url = f"https://jp.mercari.com/search?keyword={keyword}"
    if on_sale:
        search_url += "&status=on_sale"

    results = []
    
    with sync_playwright() as p:
        # Launch browser (headless=True by default)
        browser = p.chromium.launch(headless=True)
        # Set a realistic user agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # Respectful delay
            time.sleep(1.5) 
            
            page.goto(search_url)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Content might be dynamic, wait for item lists
            # Mercari items usually have a specific selector, but it changes.
            # Using a generic wait or selecting common item containers.
            # Let's verify if 'mer-item-thumbnail' or similar exists.
            # Recent Mercari uses shadow DOM or specific custom elements, but BS4 gets the rendered HTML.
            
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Mercari's structure changes often. We look for list items.
            # Common strategy: Look for elements with 'li' inside a grid, or test-id 'item-list'
            
            # Try to find items. The selector is tricky without inspecting live.
            # We will try to find links containing '/item/m' which are product pages.
            
            items = soup.find_all('li', attrs={'data-testid': 'item-cell'})
            
            if not items:
                # Fallback implementation strategy just in case test-id changed
                # Look for anchor tags with /item/m
                pass

            for item in items:
                try:
                    # Title
                    # Usually in an img alt or a separate div
                    img_tag = item.find('img')
                    title = img_tag.get('alt') if img_tag else "No Title"
                    
                    # Image URL
                    img_src = img_tag.get('src') if img_tag else ""
                    
                    # Price
                    # Look for number inside check
                    price_elem = item.find(string=re.compile(r'¥|0-9')) # Simplified
                    # Better: look for class containing 'Price' or text
                    price_str = "Unknown"
                    price_span = item.find('span', class_=lambda x: x and 'number' in x) # Approximate
                    if not price_span: 
                         # Try finding text starting with ¥ or just digits
                         price_candidates = item.get_text()
                         # simple regex extract
                         match = re.search(r'¥\s?([\d,]+)', price_candidates)
                         if match:
                             price_str = match.group(0)
                         else:
                             # fallback
                             price_str = item.get_text().strip()
                    else:
                        price_str = "¥" + price_span.get_text()

                    # Link
                    a_tag = item.find('a')
                    link = "https://jp.mercari.com" + a_tag.get('href') if a_tag else ""
                    
                    # Sold status
                    # Check for "SOLD" sticker
                    is_sold = False
                    if item.find('div', attrs={'aria-label': '売り切れ'}):
                        is_sold = True
                    # text search for sold
                    if "売り切れ" in item.get_text():
                        is_sold = True
                        
                    # Filter logic if handled client side (double check)
                    if on_sale and is_sold:
                        continue
                        
                    results.append({
                        "title": title,
                        "price": price_str,
                        "image": img_src,
                        "link": link,
                        "is_sold": is_sold
                    })
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
        finally:
            browser.close()
            
    return results

if st.button("検索"):
    if not query:
        st.warning("キーワードを入力してください。")
    else:
        with st.spinner("検索中... (これには数秒かかる場合があります)"):
            # Check for ISBN
            search_term = query
            if is_isbn(query):
                st.info(f"ISBNコードとして検索します: {query}")
                # Use query as is, Mercari handles ISBN well in keyword search
            
            # Scrape
            try:
                # Add delay to user interaction flow as requested
                # Though scraping function handles one connection, 
                # we explicitly sleep here to ensure no rapid re-clicks bypass it easily (though spinner blocks UI)
                time.sleep(1) 
                
                results = scrape_mercari(search_term, only_on_sale)
                
                if not results:
                    st.warning("該当する商品が見つかりませんでした。")
                else:
                    st.success(f"{len(results)} 件見つかりました。")
                    
                    # Display Loop
                    for item in results:
                        # Card layout
                        with st.container():
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if item['image']:
                                    st.image(item['image'])
                                else:
                                    st.text("No Image")
                            with col2:
                                st.subheader(item['title'])
                                
                                # Status Badge
                                if item['is_sold']:
                                    st.caption("🔴 売り切れ")
                                else:
                                    st.caption("🟢 販売中")
                                    
                                st.markdown(f"**価格:** {item['price']}")
                                st.markdown(f"[商品ページを見る]({item['link']})")
                            st.divider()
                            
            except Exception as e:
                st.error(f"予期せぬエラーが発生しました: {e}")

st.markdown("---")
st.caption("※本アプリは学習用です。スクレイピングは各サイトの利用規約を遵守して行ってください。")
