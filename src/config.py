import os

# Gemini AI Settings
# 優先度の高い順にモデルを並べます。
# 以前の調査で存在が確認できた最新モデルのみをリストアップしています。
GEMINI_MODELS = [
    'gemini-2.0-flash',
    'gemini-2.0-flash-lite',
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite',
    'gemini-2.5-pro',
    'gemini-flash-latest',
    'gemini-pro-latest',
]
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

DRAFT_PROMPT = """
以下の商品情報と市場相場を元に、メルカリでの出品用タイトルと商品説明文を作成してください。

【商品情報】:
{identification_result}

【市場相場（SOLD価格の例）】:
{market_prices}

以下のガイドラインに従ってください：
1. タイトルは40文字以内で、重要なキーワード（ブランド、型番、状態、送料無料など）を盛り込んでください。
2. 商品説明は、商品の特徴、仕様、状態、そして購入を検討している人が知りたい情報を網羅してください。
3. ハッシュタグを3〜5個含めてください。
4. 丁寧で信頼感のある言葉遣い（です・ます調）を使用してください。

出力形式：
【タイトル】: 
(ここにタイトル)

【商品説明】: 
(ここに商品説明)
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

# Pricing Strategy
SUGGESTED_PRICE_PERCENTILE = 50  # SOLD価格の中央値を推奨価格のベースにする
