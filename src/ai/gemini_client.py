from google import genai
from google.genai import types
from PIL import Image
import io
import sys
import os
import time

# プロジェクトルートをパスに追加してインポートできるようにする
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_MODELS, GEMINI_TEMPERATURE, IDENTIFICATION_PROMPT, DRAFT_PROMPT

class GeminiClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.models = GEMINI_MODELS

    def _call_with_fallback(self, func, *args, **kwargs):
        """
        リスト内のモデルを順に試行し、成功したモデル名と結果を返す。
        429（クォータ制限）や503（高負荷）時には待機してから次のモデルを試す。
        """
        last_exception = None
        attempt = 0
        for model_id in self.models:
            try:
                # kwargs に model_id を注入
                kwargs['model'] = model_id
                result = func(*args, **kwargs)
                return result, model_id
            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()
                
                # 再試行すべきエラーの判定（クォータ制限、高負荷、モデル未検出、一時的サーバーエラー）
                is_retryable = any(code in error_msg for code in ["429", "503", "404", "resource_exhausted", "unavailable", "internal_error", "500"])
                
                if is_retryable:
                    attempt += 1
                    # 429や503の場合は待機 (1秒, 2秒, 4秒...)
                    if any(code in error_msg for code in ["429", "503", "resource_exhausted", "unavailable"]):
                        wait_time = attempt * 2 
                        print(f"Model {model_id} failed (Retryable: {error_msg}). Waiting {wait_time}s before trying next...")
                        time.sleep(wait_time)
                    else:
                        print(f"Model {model_id} not found or other transient error. Trying next...")
                    continue
                else:
                    # その他の致命的なエラー（認証エラー等）はそのまま投げる
                    raise e
        
        # すべてのモデルが失敗した場合
        raise last_exception

    def identify_item(self, image: Image.Image) -> tuple:
        """
        Identify the item in the image. Returns (result_text, used_model_id).
        """
        # 画像をリサイズ（長辺が1024px以下になるように）
        max_size = 1024
        if max(image.size) > max_size:
            scale = max_size / max(image.size)
            new_size = (int(image.size[0] * scale), int(image.size[1] * scale))
            image = image.resize(new_size, Image.LANCZOS)

        # PIL Image to bytes (JPEG形式で圧縮)
        img_byte_arr = io.BytesIO()
        # RGBAの場合はRGBに変換（JPEGは透過をサポートしていないため）
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(img_byte_arr, format='JPEG', quality=85)
        img_bytes = img_byte_arr.getvalue()

        def _generate(**kwargs):
            model_id = kwargs.pop('model')
            
            config_args = {
                "temperature": GEMINI_TEMPERATURE
            }

            response = self.client.models.generate_content(
                model=model_id,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'),
                    IDENTIFICATION_PROMPT
                ],
                config=types.GenerateContentConfig(**config_args)
            )
            return response.text

        try:
            # Google検索なしで直接実行
            return self._call_with_fallback(_generate)
        except Exception as e:
            raise e

    def generate_draft(self, identification_result: str, market_results: list) -> tuple:
        """
        Generate a listing draft. Returns (result_text, used_model_id).
        """
        sold_prices = [str(item['price']) for item in market_results if item.get('is_sold')]
        market_prices_str = ", ".join(sold_prices[:10]) if sold_prices else "データなし"
        
        prompt = DRAFT_PROMPT.format(
            identification_result=identification_result,
            market_prices=market_prices_str
        )

        def _generate(**kwargs):
            model_id = kwargs.pop('model')
            response = self.client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=GEMINI_TEMPERATURE
                )
            )
            return response.text

        return self._call_with_fallback(_generate)
