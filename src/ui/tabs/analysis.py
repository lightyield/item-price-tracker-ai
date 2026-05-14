import streamlit as st
import os
import urllib.parse
from PIL import Image
from pillow_heif import register_heif_opener
from src.ai.gemini_client import GeminiClient
from src.utils.parsers import parse_keywords, parse_list_price, parse_draft, parse_identification_result, generate_search_urls
from src.utils.formatters import format_identification_result
from src.config import SEARCH_URLS
from src.ui.components import render_item_details, open_url_in_new_tab

# HEICをPillowで扱えるように登録
register_heif_opener()

def render_analysis_tab(api_key, inventory_manager):
    st.markdown("""
    写真からアイテムを特定し、メルカリ・Amazon・ヨドバシでの相場確認から出品ドラフト作成までをサポートします。
    """)

    # 2列レイアウトの作成
    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.subheader("1. 画像のアップロード")
        uploaded_file = st.file_uploader("画像を選択してください...", type=["jpg", "jpeg", "png", "heic", "heif"])
        
        if uploaded_file is not None:
            if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != uploaded_file.name:
                st.session_state["last_uploaded_file"] = uploaded_file.name
                st.session_state.pop("identification_result", None)
                st.session_state.pop("search_keywords", None)
                st.session_state.pop("listing_draft", None)
                st.session_state.pop("id_model_used", None)
                st.session_state.pop("draft_price", None)

            image = Image.open(uploaded_file)
            sub_col1, _ = st.columns([1, 1])
            with sub_col1:
                st.image(image, caption="アップロード画像", use_container_width=True)

    with col_right:
        if uploaded_file is not None:
            st.subheader("2. 商品の特定")
            
            if "identification_result" not in st.session_state:
                if not api_key:
                    st.error("分析にはAPIキーが必要です。")
                else:
                    with st.spinner("Gemini AIで分析中..."):
                        try:
                            client = GeminiClient(api_key)
                            result, model_used = client.identify_item(image)
                            st.session_state["identification_result"] = result
                            st.session_state["id_model_used"] = model_used
                            
                            # 解析結果を一括取得
                            parsed_data = parse_identification_result(result)
                            st.session_state["search_keywords"] = parsed_data["search_keywords"]
                            st.session_state["draft_price"] = parsed_data["list_price"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"分析中にエラーが発生しました: {e}")

            if "identification_result" in st.session_state:
                model_name = st.session_state.get("id_model_used", "不明")
                st.caption(f"🤖 使用中のAIモデル: `{model_name}`")
                
                with st.expander("AI分析の詳細結果を表示", expanded=True):
                    st.markdown(format_identification_result(st.session_state["identification_result"]))

    # 3. 検索キーワードの調整と市場相場確認
    if uploaded_file is not None and "identification_result" in st.session_state:
        st.divider()
        col_market, col_price = st.columns([1.5, 1])

        with col_market:
            st.subheader("3. 市場相場を確認")
            current_keywords = st.session_state.get("search_keywords", "")
            search_keywords_input = st.text_input("検索に使用するキーワード:", value=current_keywords, key="search_keywords_widget")

            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            urls = generate_search_urls(st.session_state["search_keywords_widget"])

            with col_btn1:
                if st.button("🚀 メルカリ", use_container_width=True):
                    open_url_in_new_tab(urls["mercari"])
            with col_btn2:
                if st.button("📦 Amazon", use_container_width=True):
                    open_url_in_new_tab(urls["amazon"])
            with col_btn3:
                if st.button("📷 ヨドバシ", use_container_width=True):
                    open_url_in_new_tab(urls["yodobashi"])

        with col_price:
            st.subheader("4. 出品価格の入力")
            st.write("メルカリの相場を参考に、出品価格を決定してください。")
            current_price_val = st.session_state.get("draft_price", "")
            price_input = st.text_input("出品価格 (¥)", value=str(current_price_val), key="listing_price_input_text")
            st.session_state["draft_price"] = price_input

        # 5. 出品ドラフトの作成
        st.divider()
        st.subheader("5. 出品ドラフトの作成")

        if st.button("✨ ドラフトを作成する", use_container_width=False):
            with st.spinner("AIが出品ドラフトを作成中..."):
                try:
                    client = GeminiClient(api_key)
                    draft, model_used = client.generate_draft(st.session_state["identification_result"], [])
                    st.session_state["listing_draft"] = draft
                    st.session_state["draft_model_used"] = model_used
                    st.rerun()
                except Exception as e:
                    st.error(f"ドラフト生成中にエラーが発生しました: {e}")

        if "listing_draft" in st.session_state:
            st.caption(f"🤖 ドラフト作成に使用されたAIモデル: `{st.session_state.get('draft_model_used', '不明')}`")
            title, description = parse_draft(st.session_state["listing_draft"])
            
            st.text_input("出品タイトル (40文字以内)", value=title, key="draft_title")
            
            display_price = st.session_state.get("draft_price", "")
            if display_price and str(display_price).isdigit():
                st.markdown(f"### 設定価格: ¥{int(display_price):,}")
            else:
                st.markdown(f"### 設定価格: ¥{display_price}")
            
            st.markdown("**商品説明文**")
            st.code(description, language=None)

            # 6. アイテム一覧への追加
            st.divider()
            st.subheader("6. アイテム一覧への追加")
            
            if st.button("💾 このアイテムを保存", use_container_width=False):
                keywords = st.session_state.get("search_keywords_widget", "")
                
                # 解析結果から保存用データを準備
                item_data = parse_identification_result(st.session_state["identification_result"])
                
                # UI側の入力値で上書き
                item_data.update({
                    "search_keywords": keywords,
                    "draft_price": st.session_state.get("draft_price", ""),
                    "draft_title": title,
                    "draft_description": description
                })
                
                # キーワードが変更されている可能性があるのでURLを再生成
                urls = generate_search_urls(keywords)
                item_data.update(urls)
                
                inventory_manager.save_item(item_data, image)
                st.success("✅ 保存しました！「アイテム一覧」タブから確認できます。")
