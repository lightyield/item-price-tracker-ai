import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import sys
import urllib.parse
import re

# プロジェクトルートをパスに追加してインポートできるようにする
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai.gemini_client import GeminiClient

# 環境変数の読み込み
load_dotenv()

st.set_page_config(
    page_title="AI商品価格トラッカー",
    page_icon="🔍",
    layout="wide"
)

# 環境変数からAPIキーを取得
api_key = os.getenv("GEMINI_API_KEY", "")

def parse_keywords(ai_result: str) -> str:
    """AIの解析結果から検索キーワードを抽出する"""
    if "【検索キーワード】:" in ai_result:
        return ai_result.split("【検索キーワード】:")[1].strip()
    return ""

def parse_list_price(ai_result: str) -> str:
    """AIの解析結果から定価の数値を抽出する"""
    if "【定価】:" in ai_result:
        price_text = ai_result.split("【定価】:")[1].strip()
        # 数字以外の文字を削除
        digits = re.sub(r'\D', '', price_text)
        return digits
    return ""

def parse_draft(draft_text: str) -> tuple:
    """生成されたドラフトテキストからタイトルと説明文を抽出する"""
    title = ""
    description = ""
    if "【タイトル】:" in draft_text:
        parts = draft_text.split("【タイトル】:")[1].split("【商品説明】:")
        title = parts[0].strip()
        if len(parts) > 1:
            description = parts[1].strip()
    return title, description

st.title("🔍 AI商品価格トラッカー")

if not api_key:
    st.error("⚠️ .envファイルに GEMINI_API_KEY が見つかりません。設定を確認してください。")

st.markdown("""
写真からアイテムを特定し、メルカリでの相場確認をサポートします。
""")

# 2列レイアウトの作成
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("1. 画像のアップロード")
    uploaded_file = st.file_uploader("画像を選択してください...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # 前回のファイルと異なる場合はセッション状態をリセット
        if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != uploaded_file.name:
            st.session_state["last_uploaded_file"] = uploaded_file.name
            st.session_state.pop("identification_result", None)
            st.session_state.pop("search_keywords", None)
            st.session_state.pop("listing_draft", None)
            st.session_state.pop("id_model_used", None)
            st.session_state.pop("draft_price", None)

        image = Image.open(uploaded_file)
        # 画像サイズを半分程度にするために列を分ける
        sub_col1, sub_col2 = st.columns([1, 1])
        with sub_col1:
            st.image(image, caption="アップロード画像", use_container_width=True)

with col_right:
    if uploaded_file is not None:
        st.subheader("2. 商品の特定")
        
        # 自動商品分析
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
                        # 定価を抽出して初期価格としてセット
                        st.session_state["draft_price"] = parse_list_price(result)
                        st.rerun() # 結果を表示するために再実行
                    except Exception as e:
                        st.error(f"分析中にエラーが発生しました: {e}")

        # 分析結果
        if "identification_result" in st.session_state:
            # モデル名の表示 (バッジ風)
            model_name = st.session_state.get("id_model_used", "不明")
            st.caption(f"🤖 使用中のAIモデル: `{model_name}`")
            
            with st.expander("AI分析の詳細結果を表示", expanded=True):
                # 結果を見やすく整形
                raw_result = st.session_state["identification_result"]
                formatted_result = (
                    raw_result.replace("【商品名】:", "**【商品名】**\n")
                    .replace("【説明】:", "\n\n**【説明】**\n")
                    .replace("【検索キーワード】:", "\n\n**【検索キーワード】**\n")
                    .replace("【定価】:", "\n\n**【定価】**\n")
                )
                st.markdown(formatted_result)

# 3. 検索キーワードの調整と市場相場確認 (全幅)
if uploaded_file is not None and "identification_result" in st.session_state:
    st.divider()
    st.subheader("3. 市場相場を確認")
    
    current_keywords = st.session_state.get("search_keywords", "")
    
    # ユーザーによるキーワード編集
    search_keywords_input = st.text_input(
        "検索に使用するキーワード:", 
        value=current_keywords,
        key="search_keywords_widget"
    )

    # ボタンを横に並べる
    col_btn1, col_btn2, col_btn3, _ = st.columns([1, 1, 1, 3])
    
    with col_btn1:
        # 「メルカリで開く」
        if st.button("🚀 メルカリ", type="primary", use_container_width=True):
            encoded_keywords = urllib.parse.quote(st.session_state["search_keywords_widget"])
            mercari_url = f"https://jp.mercari.com/search?keyword={encoded_keywords}&sort=created_time&order=desc"
            
            # JavaScriptを用いて新しいタブで開く
            st.components.v1.html(
                f"""
                <script>
                    window.open("{mercari_url}", "_blank");
                </script>
                """,
                height=0,
            )
            
    with col_btn2:
        # 「Amazonで開く」
        if st.button("📦 Amazon", use_container_width=True):
            encoded_keywords = urllib.parse.quote(st.session_state["search_keywords_widget"])
            amazon_url = f"https://www.amazon.co.jp/s?k={encoded_keywords}"
            
            # JavaScriptを用いて新しいタブで開く
            st.components.v1.html(
                f"""
                <script>
                    window.open("{amazon_url}", "_blank");
                </script>
                """,
                height=0,
            )

    with col_btn3:
        # 「ヨドバシで開く」
        if st.button("📷 ヨドバシ", use_container_width=True):
            encoded_keywords = urllib.parse.quote(st.session_state["search_keywords_widget"])
            yodobashi_url = f"https://www.yodobashi.com/?word={encoded_keywords}"
            
            # JavaScriptを用いて新しいタブで開く
            st.components.v1.html(
                f"""
                <script>
                    window.open("{yodobashi_url}", "_blank");
                </script>
                """,
                height=0,
            )

    # 4. 出品価格の入力
    st.divider()
    st.subheader("4. 出品価格の入力")
    st.write("メルカリの相場を参考に、出品価格を決定してください。")
    
    # AIが特定した定価（または空白）をデフォルト値にする
    current_price_val = st.session_state.get("draft_price", "")
    price_input = st.text_input("出品価格 (¥)", value=str(current_price_val), key="listing_price_input_text")
    
    # セッション状態を更新
    st.session_state["draft_price"] = price_input

    # 5. 出品ドラフトの作成
    st.divider()
    st.subheader("5. 出品ドラフトの作成")

    if st.button("✨ ドラフトを作成する", use_container_width=False):
        with st.spinner("AIが出品ドラフトを作成中..."):
            try:
                client = GeminiClient(api_key)
                draft, model_used = client.generate_draft(
                    st.session_state["identification_result"],
                    []
                )
                st.session_state["listing_draft"] = draft
                st.session_state["draft_model_used"] = model_used
                st.rerun()
            except Exception as e:
                st.error(f"ドラフト生成中にエラーが発生しました: {e}")

    if "listing_draft" in st.session_state:
        st.caption(f"🤖 ドラフト作成に使用されたAIモデル: `{st.session_state.get('draft_model_used', '不明')}`")
        
        title, description = parse_draft(st.session_state["listing_draft"])
        
        # 1. 出品タイトル
        st.text_input("出品タイトル (40文字以内)", value=title, key="draft_title")
        
        # 2. 設定価格（タイトルの下）
        display_price = st.session_state.get("draft_price", "")
        if display_price.isdigit():
            st.markdown(f"### 設定価格: ¥{int(display_price):,}")
        else:
            st.markdown(f"### 設定価格: ¥{display_price}")
        
        # 3. 商品説明文（設定価格の下）
        st.markdown("**商品説明文**")
        st.code(description, language=None)


st.divider()
st.caption("Developed by lightyield - テクノロジーで遺品整理をスマートに。")
