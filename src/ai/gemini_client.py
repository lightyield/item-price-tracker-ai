import google.generativeai as genai
from PIL import Image
import os

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Using the latest stable model found in the environment (2026-05)
        self.model_name = 'models/gemini-2.5-flash'
        # Google Search Tool (Grounding) を有効化
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=[{"google_search_retrieval": {}}]
        )

    def identify_item(self, image: Image.Image) -> str:
        """
        Identify the item in the image and return a description.
        """
        prompt = """
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

        """
        
        response = self.model.generate_content([prompt, image])
        return response.text
