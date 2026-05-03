from google import genai
from google.genai import types
from PIL import Image
import io
import sys
import os

# プロジェクトルートをパスに追加してインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_MODEL_ID, GEMINI_TEMPERATURE, IDENTIFICATION_PROMPT

class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = GEMINI_MODEL_ID

    def identify_item(self, image: Image.Image) -> str:
        """
        Identify the item in the image and return a description.
        """
        # Convert PIL Image to bytes for the new SDK
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        prompt = IDENTIFICATION_PROMPT
        
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
                temperature=GEMINI_TEMPERATURE
            )
        )
        
        return response.text
