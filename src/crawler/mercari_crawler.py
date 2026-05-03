from playwright.sync_api import sync_playwright
import urllib.parse
import time

class MercariCrawler:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def search_prices(self, keyword: str):
        """
        メルカリで商品を検索し、販売中と売り切れのデータを取得する。
        """
        results = {
            "on_sale": [],
            "sold_out": []
        }
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 1600}, # 縦長にして多くの要素を一気に読み込む
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # カテゴリごとに個別に取得
            for category in ["on_sale", "sold_out"]:
                # パラメータを最新の文字列形式に更新
                status_param = "on_sale" if category == "on_sale" else "trading%2Csold_out"
                url = f"https://jp.mercari.com/search?keyword={urllib.parse.quote(keyword)}&status_id={status_param}"
                
                try:
                    page.goto(url, wait_until="load", timeout=45000)
                    page.wait_for_load_state("networkidle")
                    time.sleep(3)
                    
                    # より多くの商品を読み込むためにスクロールを強化
                    for _ in range(4): # 2回から4回に増加
                        page.mouse.wheel(0, 3000)
                        time.sleep(1.5)
                    
                    selector = '[data-testid="item-cell"]'
                    page.wait_for_selector(selector, timeout=15000)
                    items = page.query_selector_all(selector)
                    
                    limit = 50
                    added = 0
                    for item in items:
                        if added >= limit: break
                        
                        try:
                            # 実際に売り切れかどうかを確認するロジックを追加
                            # メルカリのアイテムセルには SOLD の情報が含まれる
                            item_text = item.inner_text()
                            is_item_sold = "SOLD" in item_text or "売り切れ" in item_text
                            
                            # カテゴリと一致しない場合はスキップ（混在対策）
                            if category == "sold_out" and not is_item_sold:
                                continue
                            if category == "on_sale" and is_item_sold:
                                continue

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
                                
                                if price_text.isdigit():
                                    results[category].append({
                                        "price": int(price_text),
                                        "title": title_text,
                                        "image": img_url,
                                        "link": link
                                    })
                                    added += 1
                        except Exception:
                            continue
                            
                except Exception as e:
                    print(f"Error scraping {category}: {e}")
            
            browser.close()
                
        return results
