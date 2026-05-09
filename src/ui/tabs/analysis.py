import streamlit as st
import os
import urllib.parse
import re
from PIL import Image
from ai.gemini_client import GeminiClient
from utils.parsers import parse_keywords, parse_list_price, parse_draft
from utils.formatters import format_identification_result
from config import SEARCH_URLS
from ui.components import render_item_details, open_url_in_new_tab

def render_analysis_tab(api_key, inventory_manager):
    st.markdown("""
    写真からアイテムを特定し、メルカリ・Amazon・ヨドバシでの相場確認から出品ドラフト作成までをサポートします。
    """)

    # 2列レイアウトの作成
    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.subheader("1. 画像のアップロード")
        uploaded_file = st.file_uploader("画像を選択してください...", type=["jpg", "jpeg", "png"])
        
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
                            st.session_state["search_keywords"] = parse_keywords(result)
                            st.session_state["draft_price"] = parse_list_price(result)
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
            encoded_keywords = urllib.parse.quote(st.session_state["search_keywords_widget"])

            with col_btn1:
                if st.button("🚀 メルカリ", use_container_width=True):
                    open_url_in_new_tab(SEARCH_URLS["mercari"].format(keyword=encoded_keywords))
            with col_btn2:
                if st.button("📦 Amazon", use_container_width=True):
                    open_url_in_new_tab(SEARCH_URLS["amazon"].format(keyword=encoded_keywords))
            with col_btn3:
                if st.button("📷 ヨドバシ", use_container_width=True):
                    open_url_in_new_tab(SEARCH_URLS["yodobashi"].format(keyword=encoded_keywords))

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
            if display_price.isdigit():
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
                encoded_keywords = urllib.parse.quote(keywords)
                
                # 商品名抽出
                id_res = st.session_state["identification_result"]
                item_name_match = re.search(r"【商品名】:\s*(.*)", id_res)
                item_name = item_name_match.group(1) if item_name_match else "不明なアイテム"

                # 仮の保存用パス作成（InventoryManager内部で実際の保存が行われるが、ここではItemオブジェクトを作成）
                item_data = {
                    "item_name": item_name,
                    "description": id_res,
                    "search_keywords": keywords,
                    "list_price": parse_list_price(id_res),
                    "draft_price": st.session_state.get("draft_price", ""),
                    "mercari_url": SEARCH_URLS["mercari"].format(keyword=encoded_keywords),
                    "amazon_url": SEARCH_URLS["amazon"].format(keyword=encoded_keywords),
                    "yodobashi_url": SEARCH_URLS["yodobashi"].format(keyword=encoded_keywords),
                    "draft_title": title,
                    "draft_description": description
                }
                
                inventory_manager.save_item(item_data, image)
                st.success("✅ 保存しました！「アイテム一覧」タブから確認できます。")
