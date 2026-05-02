import google.generativeai as genai
from PIL import Image
import os

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Using the latest stable model found in the environment (2026-05)
        self.model_name = 'models/gemini-2.5-flash'
        self.model = genai.GenerativeModel(self.model_name)

    def identify_item(self, image: Image.Image) -> str:
        """
        Identify the item in the image and return a description.
        """
        prompt = """
        この画像に写っている商品を特定してください。
        以下の情報を日本語で出力してください：
        1. 商品名（メーカー・ブランド名、型番があればそれも含む）
        2. 商品の短い説明
        3. 検索に使用するためのキーワード（スペース区切り）

        出力形式：
        【商品名】: 
        【説明】: 
        【検索キーワード】: 
        """
        
        response = self.model.generate_content([prompt, image])
        return response.text
