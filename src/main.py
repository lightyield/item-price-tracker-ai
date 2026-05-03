import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
from ai.gemini_client import GeminiClient
from crawler.mercari_crawler import MercariCrawler

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

def display_item_cards(items, title, initial_limit=25):
    """商品をカード形式で表示する (5列グリッド)"""
    if not items:
        return

    st.write(f"#### {title}")
    
    # 取得件数制限 (上位25件)
    items_to_display = items[:initial_limit]
    
    # グリッド表示 (1行5列)
    cols_per_row = 5
    for i in range(0, len(items_to_display), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(items_to_display):
                item = items_to_display[idx]
                with cols[j]:
                    is_sold = item.get("is_sold")
                    # 高コントラストな配色 (ダークモード・ライトモード両対応を意識)
                    price_color = "#FF3B30" if is_sold else "#007AFF" # 鮮やかな赤 または 鮮やかな青
                    
                    # SOLDバッジのHTML
                    sold_badge = f'<div style="position: absolute; top: 0; left: 0; background-color: #FF3B30; color: white; padding: 2px 8px; border-radius: 8px 0 8px 0; font-weight: bold; font-size: 13px; z-index: 10;">SOLD</div>' if is_sold else ''
                    
                    # カード全体を1つのHTMLブロックとして構成 (表示崩れと</a>漏れを防止)
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

st.title("🔍 AI商品価格トラッカー")

if not api_key:
    st.error("⚠️ .envファイルに GEMINI_API_KEY が見つかりません。設定を確認してください。")

st.markdown("""
写真からアイテムを特定し、相場を調査します。
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
            st.session_state.pop("market_results", None)
            st.session_state.pop("search_keywords", None)

        image = Image.open(uploaded_file)
        # 画像サイズを半分程度にするために列を分ける
        sub_col1, sub_col2 = st.columns([1, 1])
        with sub_col1:
            st.image(image, caption="アップロード画像", use_container_width=True)

with col_right:
    if uploaded_file is not None:
        st.subheader("2. 商品の特定結果")
        
        # 自動商品分析
        if "identification_result" not in st.session_state:
            if not api_key:
                st.error("分析にはAPIキーが必要です。")
            else:
                with st.spinner("Gemini AIで分析中..."):
                    try:
                        client = GeminiClient(api_key)
                        result = client.identify_item(image)
                        st.session_state["identification_result"] = result
                        st.session_state["search_keywords"] = parse_keywords(result)
                        st.rerun() # 結果を表示するために再実行
                    except Exception as e:
                        st.error(f"分析中にエラーが発生しました: {e}")

        # 分析結果
        if "identification_result" in st.session_state:
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

# 3. 検索キーワードの調整 (全幅)
if uploaded_file is not None and "identification_result" in st.session_state:
    st.divider()
    st.subheader("3. 検索キーワードの調整")
    # ユーザーによるキーワード編集
    search_keywords = st.text_input(
        "市場調査に使用するキーワード:", 
        value=st.session_state.get("search_keywords", "")
    )
    # 変更を保存
    st.session_state["search_keywords"] = search_keywords
    
    if st.button("メルカリで相場を検索", use_container_width=True):
        if not search_keywords:
            st.error("検索キーワードを入力してください。")
        else:
            with st.spinner(f"検索中: {search_keywords}..."):
                try:
                    # 検索前に結果をクリア
                    st.session_state.pop("market_results", None)
                    crawler = MercariCrawler(headless=True)
                    results = crawler.search_prices(search_keywords)
                    
                    if results:
                        st.session_state["market_results"] = results
                        st.success(f"「{search_keywords}」の検索データを {len(results)} 件取得しました！")
                        st.rerun() # 確実に表示を更新
                    else:
                        st.warning(f"「{search_keywords}」に該当する商品は見つかりませんでした。")
                except Exception as e:
                    st.error(f"検索中にエラーが発生しました: {e}")

# 4. 市場調査結果 (全幅)
if "market_results" in st.session_state:
    st.divider()
    results = st.session_state["market_results"]
    
    if results:
        st.subheader(f"📊 メルカリ検索結果 (上位 {len(results)} 件)")
        display_item_cards(results, "最新の出品状況")
    else:
        st.warning("検索結果が見つかりませんでした。")


st.divider()
st.caption("Developed by lightyield - テクノロジーで遺品整理をスマートに。")
