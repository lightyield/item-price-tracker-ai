import streamlit as st
import sys
import os

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ITEMS_LIMIT, COLS_PER_ROW

def display_item_cards(items, title):
    """商品をカード形式で表示する (グリッド表示)"""
    if not items:
        return

    st.write(f"#### {title}")
    
    # 取得件数制限 (設定値を使用)
    items_to_display = items[:ITEMS_LIMIT]
    
    # グリッド表示 (設定値を使用)
    cols_per_row = COLS_PER_ROW
    for i in range(0, len(items_to_display), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(items_to_display):
                item = items_to_display[idx]
                with cols[j]:
                    is_sold = item.get("is_sold")
                    # 高コントラストな配色
                    price_color = "#FF3B30" if is_sold else "#007AFF"
                    
                    # SOLDバッジのHTML
                    sold_badge = f'<div style="position: absolute; top: 0; left: 0; background-color: #FF3B30; color: white; padding: 2px 8px; border-radius: 8px 0 8px 0; font-weight: bold; font-size: 13px; z-index: 10;">SOLD</div>' if is_sold else ''
                    
                    st.markdown(
                        f"""
                        <div style="margin-bottom: 20px; width: 100%;">
                            <a href="{item["link"]}" target="_blank" style="text-decoration: none; color: inherit;">
                                <div style="position: relative; width: 100%; aspect-ratio: 1/1; margin-bottom: 8px; overflow: hidden; border-radius: 8px;">
                                    <img src="{item["image"]}" style="width: 100%; height: 100%; object-fit: cover; {'opacity: 0.7;' if is_sold else ''}">
                                    {sold_badge}
                                </div>
                                <div style="padding: 0 2px;">
                                    <p style="color: {price_color}; font-size: 20px; font-weight: 900; margin: 0; line-height: 1.2;">¥{item["price"]:,}</p>
                                    <p style="font-size: 12px; line-height: 1.4; height: 2.8em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; margin: 4px 0 0 0; opacity: 0.9;">{item.get("title", "名称未設定")}</p>
                                </div>
                            </a>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
