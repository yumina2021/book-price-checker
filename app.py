import streamlit as st
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import re

st.set_page_config(page_title="Book Price Checker", page_icon="📚", layout="wide")

st.title("📚 Book Price Checker")
st.markdown("メルカリの中古価格を一括検索します。")

# サイドバー
st.sidebar.header("🔍 検索オプション")
only_on_sale = st.sidebar.checkbox("販売中のみ表示", value=False)

query = st.text_input("タイトルまたはISBNを入力", placeholder="例: Python入門 / 9784297123456")

def scrape_mercari(keyword, only_on_sale=False):
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = context.new_page()
        page.set_default_timeout(45000)  # ✅ 45秒に延長
        
        try:
            # 検索URL構築
            status = "on_sale" if only_on_sale else "on_sale%2Con_sale_reserved"
            search_url = f"https://jp.mercari.com/search?keyword={keyword}&status={status}"
            
            st.info(f"検索中: {keyword}...")
            
            # ページ移動＋長め待機
            page.goto(search_url)
            page.wait_for_load_state("networkidle", timeout=30000)  # ✅ 30秒
            time.sleep(3)  # ✅ メルカリ動的読み込み待機
            
            # メルカリ商品リスト取得（最新セレクタ）
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # ✅ メルカリ2026最新セレクタ
            items = soup.find_all('div', class_=re.compile(r'mer-item|item-cell|grid-item'))
            
            if not items:
                items = soup.find_all('li', class_=re.compile(r'item|product'))
            
            for item in items[:12]:  # 最大12件
                try:
                    # タイトル（img alt or a href）
                    title_elem = item.find('img') or item.find('a')
                    title = title_elem.get('alt') or title_elem.get('title') or "不明"
                    
                    # 画像
                    img = item.find('img')
                    img_src = img.get('src') or img.get('data-src') if img else ""
                    
                    # 価格（メルカリ特化）
                    price_match = re.search(r'¥([\d,]+)', item.get_text())
                    price = price_match.group(0) if price_match else "価格不明"
                    
                    # リンク
                    link_elem = item.find('a', href=re.compile(r'/item/m\d+'))
                    link = "https://jp.mercari.com" + link_elem.get('href') if link_elem else ""
                    
                    # 販売状況
                    is_sold = "売り切れ" in item.get_text() or "sold" in item.get_text().lower()
                    
                    if only_on_sale and is_sold:
                        continue
                        
                    results.append({
                        "title": title[:50],
                        "price": price,
                        "image": img_src,
                        "link": link,
                        "is_sold": is_sold
                    })
                except:
                    continue
                    
        except Exception as e:
            st.error(f"検索エラー: {str(e)}")
        finally:
            browser.close()
    
    return results

if st.button("🔍 検索実行", type="primary"):
    if query:
        with st.spinner("メルカリを検索中...（15-30秒）"):
            results = scrape_mercari(query, only_on_sale)
            
            if results:
                st.success(f"✅ {len(results)}件見つかりました！")
                for i, item in enumerate(results, 1):
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.image(item['image'], use_column_width=True)
                    with col2:
                        st.markdown(f"**{item['title']}**")
                        st.caption(f"🟢" if not item['is_sold'] else "🔴")
                        st.markdown(f"**{item['price']}**")
                        st.markdown(f"[📱 詳細ページ]({item['link']})")
                    st.divider()
            else:
                st.warning("😅 商品が見つかりませんでした")
    else:
        st.warning("📝 検索キーワードを入力してください")

st.markdown("---")
st.caption("⚠️ 学習用アプリです。利用規約を遵守し、検索頻度を控えめにしてください。")
