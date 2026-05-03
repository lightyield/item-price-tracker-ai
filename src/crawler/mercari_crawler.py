from playwright.sync_api import sync_playwright
import urllib.parse
import sys
import os

# プロジェクトルートをパスに追加してインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MERCARI_SEARCH_URL, MERCARI_USER_AGENT, MERCARI_VIEWPORT, SELECTORS

class MercariCrawler:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def search_prices(self, keyword: str):
        """
        メルカリで商品を検索し、上位のデータを取得する。
        """
        results = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport=MERCARI_VIEWPORT,
                user_agent=MERCARI_USER_AGENT
            )
            page = context.new_page()
            
            url = MERCARI_SEARCH_URL.format(keyword=urllib.parse.quote(keyword))
            
            try:
                # ページ遷移と待機
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # スクロールして要素を確定させる (負荷を避けるためにロード状態を確認)
                for _ in range(2):
                    page.mouse.wheel(0, 2000)
                    page.wait_for_load_state("domcontentloaded")
                
                selector = SELECTORS["item_cell"]
                page.wait_for_selector(selector, timeout=20000)
                
                # 取得処理
                added = 0
                limit = 25
                
                # 要素を再取得
                all_items = page.query_selector_all(selector)
                
                for item in all_items:
                    if added >= limit:
                        break
                    
                    try:
                        # query_selector はタイムアウトなしで要素を探すためそのまま使用
                        price_el = item.query_selector(SELECTORS["price"])
                        title_el = item.query_selector(SELECTORS["title"])
                        img_el = item.query_selector(SELECTORS["image"])
                        link_el = item.query_selector(SELECTORS["link"])
                        
                        if price_el and title_el and img_el and link_el:
                            price_text = price_el.inner_text().replace(',', '').replace('¥', '').strip()
                            title_text = title_el.inner_text().strip()
                            img_url = img_el.get_attribute('src')
                            link = link_el.get_attribute('href')
                            
                            if link and link.startswith('/'):
                                link = f"https://jp.mercari.com{link}"
                            
                            # SOLDラベルの有無を確認
                            item_text = item.inner_text()
                            is_sold = "SOLD" in item_text or "売り切れ" in item_text
                            
                            if price_text.isdigit():
                                results.append({
                                    "price": int(price_text),
                                    "title": title_text,
                                    "image": img_url,
                                    "link": link,
                                    "is_sold": is_sold
                                })
                                added += 1
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"Error scraping: {e}")
            
            browser.close()
                
        return results
