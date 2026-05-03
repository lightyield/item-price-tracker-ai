from playwright.sync_api import sync_playwright
import urllib.parse
import time

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
                viewport={'width': 1280, 'height': 1600},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            url = f"https://jp.mercari.com/search?keyword={urllib.parse.quote(keyword)}&sort=created_time&order=desc"
            
            try:
                # ページ遷移と待機
                page.goto(url, wait_until="networkidle", timeout=60000)
                time.sleep(3)
                
                # スクロールして要素を確定させる
                for _ in range(2):
                    page.mouse.wheel(0, 2000)
                    time.sleep(1)
                
                selector = '[data-testid="item-cell"]'
                page.wait_for_selector(selector, timeout=20000)
                
                # 取得処理
                added = 0
                limit = 25
                
                # 要素が動的に増える可能性があるため、ループ内で再取得を考慮
                all_items = page.query_selector_all(selector)
                
                for item in all_items:
                    if added >= limit:
                        break
                    
                    try:
                        price_el = item.query_selector('span[class*="number"]')
                        title_el = item.query_selector('[class*="itemName"]')
                        img_el = item.query_selector('img')
                        link_el = item.query_selector('a')
                        
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
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"Error scraping: {e}")
            
            browser.close()
                
        return results
