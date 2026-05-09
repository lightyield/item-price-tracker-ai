import streamlit as st
import os
from models.item import Item
from utils.formatters import format_identification_result

def open_url_in_new_tab(url: str):
    """URLを新しいタブで開くためのJavaScriptを埋め込む"""
    st.components.v1.html(
        f"""
        <script>
            window.open("{url}", "_blank");
        </script>
        """,
        height=0,
    )

def render_item_details(item: Item, is_interactive: bool = False):
    """
    アイテムの詳細（ステップ1〜5）を描画する共通コンポーネント
    
    Args:
        item: 表示するアイテムデータ
        is_interactive: 分析中などのインタラクティブなモードかどうか
    """
    # 1. 画像と2. 特定
    col_left, col_right = st.columns([1, 1.2])
    
    with col_left:
        st.subheader("1. 画像のアップロード" if is_interactive else "1. 画像")
        if item.image_path and os.path.exists(item.image_path):
            st.image(item.image_path, caption="商品画像", use_container_width=True)
        else:
            st.warning("画像が見つかりません")
            
    with col_right:
        st.subheader("2. 商品の特定")
        st.markdown(format_identification_result(item.description))

    # 3. 市場相場と 4. 出品価格
    st.divider()
    col_market, col_price = st.columns([1.5, 1])
    
    with col_market:
        st.subheader("3. 市場相場を確認")
        if is_interactive:
            st.info("キーワードを調整して各サイトで検索できます。")
        else:
            st.write(f"キーワード: `{item.search_keywords}`")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            if is_interactive:
                if st.button("🚀 メルカリ", use_container_width=True):
                    open_url_in_new_tab(item.mercari_url)
            else:
                st.link_button("🚀 メルカリ", item.mercari_url, use_container_width=True)
                
        with m_col2:
            if is_interactive:
                if st.button("📦 Amazon", use_container_width=True):
                    open_url_in_new_tab(item.amazon_url)
            else:
                st.link_button("📦 Amazon", item.amazon_url, use_container_width=True)
                
        with m_col3:
            if is_interactive:
                if st.button("📷 ヨドバシ", use_container_width=True):
                    open_url_in_new_tab(item.yodobashi_url)
            else:
                st.link_button("📷 ヨドバシ", item.yodobashi_url, use_container_width=True)
                
    with col_price:
        st.subheader("4. 出品価格の入力")
        price = item.draft_price
        if price.isdigit():
            st.markdown(f"### 設定価格: ¥{int(price):,}")
        else:
            st.markdown(f"### 設定価格: ¥{price}")

    # 5. 出品ドラフト
    st.divider()
    st.subheader("5. 出品ドラフトの作成")
    if item.draft_title:
        st.markdown("**出品タイトル**")
        st.code(item.draft_title, language=None)
        st.markdown("**商品説明文**")
        st.code(item.draft_description, language=None)
    else:
        st.info("ドラフトはまだ作成されていません。")
