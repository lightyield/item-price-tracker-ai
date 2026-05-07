import os

# Gemini AI Settings
# 優先度の高い順にモデルを並べます。
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
2. 商品説明は、商品の特徴、仕様、状態、転用購入を検討している人が知りたい情報を網羅してください。
3. ハッシュタグを3〜5個含めてください。
4. 丁寧で信頼感のある言葉遣い（です・ます調）を使用してください。

出力形式：
【タイトル】: 
(ここにタイトル)

【商品説明】: 
(ここに商品説明)
"""

# Search URL Settings
SEARCH_URLS = {
    "mercari": "https://jp.mercari.com/search?keyword={keyword}&sort=created_time&order=desc",
    "amazon": "https://www.amazon.co.jp/s?k={keyword}",
    "yodobashi": "https://www.yodobashi.com/?word={keyword}"
}

# UI Settings
ITEMS_LIMIT = 25
COLS_PER_ROW = 5
