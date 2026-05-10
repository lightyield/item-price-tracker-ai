import streamlit as st
import os
from ui.components import render_item_details
from ai.gemini_client import GeminiClient
from utils.parsers import parse_draft

def render_inventory_screen(api_key, inventory_manager):
    st.header("📋 アイテム一覧")
    
    items = inventory_manager.load_items()
    
    if not items:
        st.info("一覧にアイテムがありません。「アイテム分析」タブから保存してください。")
    else:
        # 一括削除機能
        col_count, col_bulk_del = st.columns([4, 1])
        with col_count:
            st.write(f"現在 {len(items)} 件のアイテムが保存されています。")
        
        with col_bulk_del:
            if st.checkbox("一括削除を有効化", key="bulk_del_enable"):
                if st.button("🚨 全アイテムを削除", type="primary", use_container_width=True):
                    for item in items:
                        inventory_manager.delete_item(item.id)
                    st.success("すべてのアイテムを削除しました")
                    st.rerun()

        st.divider()
        
        for item in items:
            # サムネイル、エクスパンダー、削除ボタンのレイアウト
            col_thumb, col_main, col_del = st.columns([1, 8, 1])
            
            image_path = item.image_path
            image_exists = image_path and os.path.exists(image_path)
            
            with col_thumb:
                if image_exists:
                    st.image(image_path, use_container_width=True)
            
            with col_main:
                with st.expander(f"**{item.item_name}** ({item.date})", expanded=False):
                    render_item_details(item, is_interactive=False, api_key=api_key, inventory_manager=inventory_manager)

            with col_del:
                if st.button("🗑️", key=f"del_{item.id}", help="アイテムを削除"):
                    if inventory_manager.delete_item(item.id):
                        st.success("削除しました")
                        st.rerun()
