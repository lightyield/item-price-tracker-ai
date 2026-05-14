import pytest
from src.utils.parsers import parse_keywords, parse_list_price, parse_draft, parse_identification_result

def test_parse_keywords():
    ai_result = "【商品名】: iPhone 15\n【説明】: Appleのスマートフォン\n【検索キーワード】: iPhone15 Apple 128GB\n【定価】: 124,800円"
    assert parse_keywords(ai_result) == "iPhone15 Apple 128GB"

def test_parse_list_price():
    ai_result = "【定価】: 124,800円"
    assert parse_list_price(ai_result) == "124800"

def test_parse_draft():
    draft_text = "【タイトル】: 【美品】iPhone 15 128GB ブルー\n【商品説明】: 状態は非常に良いです。付属品完備。"
    title, description = parse_draft(draft_text)
    assert title == "【美品】iPhone 15 128GB ブルー"
    assert description == "状態は非常に良いです。付属品完備。"

def test_parse_identification_result():
    ai_result = """
【商品名】: 
ソニー ワイヤレスヘッドホン WH-1000XM5

【説明】: 
業界最高クラスのノイズキャンセリング機能を搭載したオーバーイヤーヘッドホン。

【検索キーワード】: 
SONY WH-1000XM5 ノイズキャンセリング

【定価】: 
59,400円
"""
    result = parse_identification_result(ai_result)
    assert result["item_name"] == "ソニー ワイヤレスヘッドホン WH-1000XM5"
    assert result["search_keywords"] == "SONY WH-1000XM5 ノイズキャンセリング"
    assert result["list_price"] == "59400"
    assert "mercari.com" in result["mercari_url"]
    assert "amazon.co.jp" in result["amazon_url"]
    assert "yodobashi.com" in result["yodobashi_url"]
