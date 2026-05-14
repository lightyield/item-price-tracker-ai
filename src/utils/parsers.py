import re
import urllib.parse
from typing import Dict, Any, Tuple
from src.config import SEARCH_URLS

def extract_section(text: str, section_name: str) -> str:
    """指定されたセクション名の内容を抽出する。次のセクションの開始までを対象とする。"""
    pattern = rf"【{section_name}】:\s*(.*?)(?=\n【|$)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def parse_keywords(ai_result: str) -> str:
    """AIの解析結果から検索キーワードを抽出する"""
    return extract_section(ai_result, "検索キーワード")

def parse_list_price(ai_result: str) -> str:
    """AIの解析結果から定価の数値を抽出する"""
    price_text = extract_section(ai_result, "定価")
    if price_text:
        # 数字以外の文字を削除
        digits = re.sub(r'\D', '', price_text)
        return digits
    return ""

def parse_draft(draft_text: str) -> Tuple[str, str]:
    """生成されたドラフトテキストからタイトルと説明文を抽出する"""
    title = extract_section(draft_text, "タイトル")
    description = extract_section(draft_text, "商品説明")
    return title, description

def generate_search_urls(keywords: str) -> Dict[str, str]:
    """キーワードから各サイトの検索URLを生成する"""
    encoded_keywords = urllib.parse.quote(keywords)
    return {
        "mercari": SEARCH_URLS["mercari"].format(keyword=encoded_keywords),
        "amazon": SEARCH_URLS["amazon"].format(keyword=encoded_keywords),
        "yodobashi": SEARCH_URLS["yodobashi"].format(keyword=encoded_keywords)
    }

def parse_identification_result(ai_result: str) -> Dict[str, Any]:
    """
    AIの特定結果からItem作成に必要なデータを抽出する。
    """
    item_name = extract_section(ai_result, "商品名") or "不明なアイテム"
    keywords = parse_keywords(ai_result)
    urls = generate_search_urls(keywords)
    
    return {
        "item_name": item_name,
        "description": ai_result,
        "search_keywords": keywords,
        "list_price": parse_list_price(ai_result),
        "mercari_url": urls["mercari"],
        "amazon_url": urls["amazon"],
        "yodobashi_url": urls["yodobashi"]
    }
