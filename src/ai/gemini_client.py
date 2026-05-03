from google import genai
from google.genai import types
from PIL import Image
import io

class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        # Using the latest stable model found in 2026
        self.model_id = 'gemini-2.5-flash'

    def identify_item(self, image: Image.Image) -> str:
        """
        Identify the item in the image and return a description.
        """
        # Convert PIL Image to bytes for the new SDK
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

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
        
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type='image/png'),
                prompt
            ],
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch()
                    )
                ],
                temperature=0.7
            )
        )
        
        return response.text
