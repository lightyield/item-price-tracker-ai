from google import genai
from google.genai import types
from PIL import Image
import io
import sys
import os
import time
import re
from typing import List, Tuple, Optional

from src.config import DEFAULT_GEMINI_MODELS, GEMINI_TEMPERATURE, IDENTIFICATION_PROMPT, DRAFT_PROMPT

def get_available_gemini_models(client: Optional[genai.Client] = None, max_candidates: int = 5) -> List[str]:
    """
    利用可能なGeminiモデル一覧を動的に取得し、画像認識・ドラフト生成に適したFlash系モデルを優先順にソートして返却する。
    
    1. generateContent をサポートしているモデルを抽出
    2. 特殊用途モデル（画像生成 imagen、TTS、音声、リアルタイム、embeddingなど）を除外
    3. Flash系モデルを優先し、バージョン降順（安定版優先、-liteは標準の後）でソート
    4. 上位候補（最大 max_candidates 件）を返却
    """
    if client is None:
        return list(DEFAULT_GEMINI_MODELS[:max_candidates])

    try:
        models_pager = client.models.list()
        candidates = []
        for m in models_pager:
            name = getattr(m, 'name', '') or ''
            if not name:
                continue
            model_id = re.sub(r'^models/', '', name)

            # supported_actions をチェック（存在する場合）
            actions = getattr(m, 'supported_actions', None) or []
            if actions and 'generateContent' not in actions:
                continue

            # 特殊用途モデルを除外
            lower = model_id.lower()
            if any(k in lower for k in ['image', 'tts', 'audio', 'realtime', 'embedding', 'imagen']):
                continue

            candidates.append(model_id)

        if not candidates:
            return list(DEFAULT_GEMINI_MODELS[:max_candidates])

        flash_models = [m for m in candidates if 'flash' in m.lower()]
        other_models = [m for m in candidates if 'flash' not in m.lower() and m.lower().startswith('gemini-')]

        def sort_key(model_name: str):
            lower = model_name.lower()
            # プレビュー・実験用より安定版を優先 (0: 安定版, 1: プレビュー/exp)
            is_preview = 1 if ('preview' in lower or 'exp' in lower) else 0
            
            # バージョン番号の抽出 (例: gemini-2.5-flash -> 2.5)
            v_match = re.search(r'gemini-(\d+(?:\.\d+)?)', lower)
            version = float(v_match.group(1)) if v_match else 0.0
            
            # -lite は標準版の後 (0: 標準, 1: lite)
            is_lite = 1 if 'lite' in lower else 0
            
            # 安定版優先(0)、バージョン降順(-version)、標準版優先(0)、名前順
            return (is_preview, -version, is_lite, model_name)

        flash_models.sort(key=sort_key)
        other_models.sort(key=sort_key)

        result = flash_models + other_models
        if result:
            return result[:max_candidates]

        return list(DEFAULT_GEMINI_MODELS[:max_candidates])
    except Exception as e:
        print(f"Geminiモデル一覧の動的取得中にエラーが発生しました: {e}。デフォルトモデルを使用します。")
        return list(DEFAULT_GEMINI_MODELS[:max_candidates])


class GeminiClient:
    def __init__(self, api_key: str, models: Optional[List[str]] = None):
        self.client = genai.Client(api_key=api_key) if api_key else None
        if models:
            self.models = models
        else:
            self.models = get_available_gemini_models(self.client)

    def _call_with_fallback(self, func, *args, **kwargs):
        """
        リスト内のモデルを順に試行し、成功したモデル名と結果を返す。
        429（クォータ制限）や503（高負荷）時には待機してから次のモデルを試す。
        """
        if not self.client:
            raise ValueError("Gemini APIキーが設定されていません。")

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
                    # 429や503の場合は待機 (2秒, 4秒, 6秒...)
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

