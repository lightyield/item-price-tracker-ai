from playwright.sync_api import sync_playwright

def test_url(url):
    print(f"URL: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        items = page.query_selector_all('[data-testid="item-cell"]')
        print(f"  Found {len(items)} items")
        browser.close()

test_url("https://jp.mercari.com/search?keyword=iPhone%2015&status_id=1")
test_url("https://jp.mercari.com/search?keyword=iPhone%2015&status_id=2")
test_url("https://jp.mercari.com/search?keyword=iPhone%2015&status_id=2%2C3")
test_url("https://jp.mercari.com/search?keyword=iPhone%2015&item_status_id=2")
