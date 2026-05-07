import pytest
from src.utils.parsers import parse_keywords, parse_list_price, parse_draft

def test_parse_keywords():
    ai_result = "【商品名】: iPhone 15\n【説明】: Appleのスマートフォン\n【検索キーワード】: iPhone15 Apple 128GB\n【定価】: 124,800円"
    assert parse_keywords(ai_result) == "iPhone15 Apple 128GB"
    
    ai_result_no_keywords = "【商品名】: iPhone 15"
    assert parse_keywords(ai_result_no_keywords) == ""

def test_parse_list_price():
    ai_result = "【定価】: 124,800円"
    assert parse_list_price(ai_result) == "124800"
    
    ai_result_complex = "【定価】: 約150,000円（税込）"
    assert parse_list_price(ai_result_complex) == "150000"
    
    ai_result_none = "【定価】: 調査したが不明"
    assert parse_list_price(ai_result_none) == ""

def test_parse_draft():
    draft_text = "【タイトル】: 【美品】iPhone 15 128GB ブルー\n【商品説明】: 状態は非常に良いです。付属品完備。"
    title, description = parse_draft(draft_text)
    assert title == "【美品】iPhone 15 128GB ブルー"
    assert description == "状態は非常に良いです。付属品完備。"
    
    draft_text_incomplete = "【タイトル】: 途中までのドラフト"
    title, description = parse_draft(draft_text_incomplete)
    assert title == "途中までのドラフト"
    assert description == ""
