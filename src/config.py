import os

# Gemini AI Settings
GEMINI_MODEL_ID = 'gemini-2.5-flash'
GEMINI_TEMPERATURE = 0.7

IDENTIFICATION_PROMPT = """
この画像に写っている商品を特定してください。
Google検索を活用して、できるだけ正確な情報を取得してください。

以下の情報を日本語で出力してください：
1. 商品名（メーカー・ブランド名、型番があればそれも含む）
2. 商品の短い説明
3. 検索に使用するためのキーワード（スペース区切り）
4. 定価（メーカー希望小売価格や発売時の価格。Google検索で確認し、具体的な金額を記載してください。不明な場合は「調査したが不明」と記載）

出力形式（各項目の後に必ず改行を入れてください）：
【商品名】: 
(ここに商品名)

【説明】: 
(ここに説明)

【検索キーワード】: 
(ここにキーワード)

【定価】: 
(ここに調査した定価)
"""

# Mercari Crawler Settings
MERCARI_BASE_URL = "https://jp.mercari.com"
MERCARI_SEARCH_URL = f"{MERCARI_BASE_URL}/search?keyword={{keyword}}&sort=created_time&order=desc"
MERCARI_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MERCARI_VIEWPORT = {'width': 1280, 'height': 1600}

# Mercari Selectors
SELECTORS = {
    "item_cell": '[data-testid="item-cell"]',
    "price": 'span[class*="number"]',
    "title": '[class*="itemName"]',
    "image": 'img',
    "link": 'a'
}

# UI Settings
ITEMS_LIMIT = 25
COLS_PER_ROW = 5
