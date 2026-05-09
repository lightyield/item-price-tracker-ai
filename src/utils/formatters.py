def format_identification_result(raw_result: str) -> str:
    """分析結果のテキストを見やすく整形する"""
    if not raw_result:
        return ""
        
    return (
        raw_result.replace("【商品名】:", "**【商品名】**\n")
        .replace("【説明】:", "\n\n**【説明】**\n")
        .replace("【検索キーワード】:", "\n\n**【検索キーワード】**\n")
        .replace("【定価】:", "\n\n**【定価】**\n")
    )
