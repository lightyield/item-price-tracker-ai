import re

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

def parse_draft(draft_text: str) -> tuple:
    """生成されたドラフトテキストからタイトルと説明文を抽出する"""
    title = extract_section(draft_text, "タイトル")
    description = extract_section(draft_text, "商品説明")
    return title, description
