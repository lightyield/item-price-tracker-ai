import streamlit as st
import os
from src.models.item import Item
from src.utils.formatters import format_identification_result
from src.utils.parsers import parse_draft, generate_search_urls
from src.ai.gemini_client import GeminiClient

def render_item_details(item: Item, is_interactive: bool = False, api_key: str = None, inventory_manager = None):
    """
    アイテムの詳細（ステップ1〜5）を描画する共通コンポーネント
    """
    # インベントリモード（編集可能モード）の判定
    is_inventory_mode = inventory_manager is not None

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
        urls = {
            "mercari": item.mercari_url,
            "amazon": item.amazon_url,
            "yodobashi": item.yodobashi_url
        }

        # インタラクティブモードでキーワードが変更されている可能性を考慮
        if is_interactive and "search_keywords_widget" in st.session_state:
            urls = generate_search_urls(st.session_state["search_keywords_widget"])

        with m_col1:
            if is_interactive:
                if st.button("🚀 メルカリ", use_container_width=True, key=f"btn_mercari_{item.id}"):
                    open_url_in_new_tab(urls["mercari"])
            else:
                st.link_button("🚀 メルカリ", urls["mercari"], use_container_width=True)
                
        with m_col2:
            if is_interactive:
                if st.button("📦 Amazon", use_container_width=True, key=f"btn_amazon_{item.id}"):
                    open_url_in_new_tab(urls["amazon"])
            else:
                st.link_button("📦 Amazon", urls["amazon"], use_container_width=True)
                
        with m_col3:
            if is_interactive:
                if st.button("📷 ヨドバシ", use_container_width=True, key=f"btn_yodobashi_{item.id}"):
                    open_url_in_new_tab(urls["yodobashi"])
            else:
                st.link_button("📷 ヨドバシ", urls["yodobashi"], use_container_width=True)
                
    with col_price:
        st.subheader("4. 出品価格の入力")
        if is_inventory_mode:
            # 在庫一覧では価格を変更可能にする
            initial_price = str(item.draft_price) if item.draft_price is not None else ""
            new_price = st.text_input("出品価格 (¥)", value=initial_price, key=f"price_input_{item.id}")
        else:
            st.markdown(f"### 設定価格: {item.formatted_draft_price}")

    # 5. 出品ドラフト
    st.divider()
    st.subheader("5. 出品ドラフトの作成")
    
    # セッション状態でのドラフト管理（再作成時の上書き用）
    draft_title_key = f"draft_title_{item.id}"
    draft_desc_key = f"draft_desc_{item.id}"
    
    if draft_title_key not in st.session_state:
        st.session_state[draft_title_key] = item.draft_title
    if draft_desc_key not in st.session_state:
        st.session_state[draft_desc_key] = item.draft_description

    if is_inventory_mode:
        # 再作成が実行されたかどうかのフラグ
        recreated_flag_key = f"recreated_{item.id}"
        if recreated_flag_key not in st.session_state:
            st.session_state[recreated_flag_key] = False

        # ドラフト再作成ボタン
        if st.button("✨ ドラフトを再作成する", key=f"recreate_btn_{item.id}"):
            if not api_key:
                st.error("APIキーが設定されていません。")
            else:
                with st.spinner("AIが新しいドラフトを生成中..."):
                    try:
                        client = GeminiClient(api_key)
                        # マーケット結果なしで再作成（元の説明文を使用）
                        new_draft_raw, _ = client.generate_draft(item.description, [])
                        new_title, new_desc = parse_draft(new_draft_raw)
                        st.session_state[draft_title_key] = new_title
                        st.session_state[draft_desc_key] = new_desc
                        st.session_state[recreated_flag_key] = True  # 再作成フラグをオン
                        st.rerun()
                    except Exception as e:
                        st.error(f"ドラフト生成中にエラーが発生しました: {e}")

        # タイトルと説明文の表示
        current_title = st.text_input("出品タイトル", value=st.session_state[draft_title_key], key=f"title_edit_{item.id}")
        st.session_state[draft_title_key] = current_title
        
        st.markdown("**商品説明文**")
        st.code(st.session_state[draft_desc_key], language=None)
        
        # 再作成された場合のみ変更保存ボタンを表示
        if st.session_state[recreated_flag_key]:
            if st.button("💾 変更を保存（上書き）", key=f"save_btn_{item.id}", type="primary"):
                updated_data = {
                    "draft_price": st.session_state[f"price_input_{item.id}"],
                    "draft_title": st.session_state[draft_title_key],
                    "draft_description": st.session_state[draft_desc_key]
                }
                if inventory_manager.update_item(item.id, updated_data):
                    st.success("✅ 保存しました！")
                    st.session_state[recreated_flag_key] = False  # 保存後はフラグを下ろす
                    st.rerun()
                else:
                    st.error("保存に失敗しました。")
    else:
        # 通常表示モード
        if item.draft_title:
            st.markdown("**出品タイトル**")
            st.code(item.draft_title, language=None)
            st.markdown("**商品説明文**")
            st.code(item.draft_description, language=None)
        else:
            st.info("ドラフトはまだ作成されていません。")
