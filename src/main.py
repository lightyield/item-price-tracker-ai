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

def display_item_cards(items, title, initial_limit=10):
    """商品をカード形式で表示し、「もっと見る」機能を提供する"""
    if not items:
        return

    st.write(f"#### {title}")
    
    # カテゴリごとに表示件数をセッション状態で管理
    state_key = f"limit_{title.lower().replace(' ', '_')}"
    if state_key not in st.session_state:
        st.session_state[state_key] = initial_limit

    current_limit = st.session_state[state_key]
    items_to_display = items[:current_limit]
    
    # グリッド表示 (1行6列)
    cols_per_row = 6
    for i in range(0, len(items_to_display), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(items_to_display):
                item = items_to_display[idx]
                with cols[j]:
                    # サムネイルをリンクとして表示
                    st.markdown(
                        f'<a href="{item["link"]}" target="_blank">'
                        f'<img src="{item["image"]}" style="width:100%; border-radius:5px;">'
                        f'</a>', 
                        unsafe_allow_html=True
                    )
                    # 商品名 (長すぎる場合は省略)
                    display_title = item.get("title", "名称未設定")
                    if len(display_title) > 25:
                        display_title = display_title[:22] + "..."
                    st.caption(display_title)
                    # 価格
                    st.write(f"**¥{item['price']:,}**")

    # もっと見るボタン
    if len(items) > current_limit:
        if st.button(f"さらに表示 ({title})", key=f"btn_{state_key}"):
            st.session_state[state_key] += 10
            st.rerun()

st.title("🔍 AI商品価格トラッカー")

if not api_key:
    st.error("⚠️ .envファイルに GEMINI_API_KEY が見つかりません。設定を確認してください。")

st.markdown("""
写真からアイテムを特定し、相場を調査します。
1. アイテムの写真をアップロードしてください（自動でAI分析が始まります）。
2. 必要に応じてキーワードを調整し、相場を検索します。
""")

# メインコンテンツ
uploaded_file = st.file_uploader("画像を選択してください...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 前回のファイルと異なる場合はセッション状態をリセット
    if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != uploaded_file.name:
        st.session_state["last_uploaded_file"] = uploaded_file.name
        st.session_state.pop("identification_result", None)
        st.session_state.pop("market_results", None)
        st.session_state.pop("search_keywords", None)

    # 1. 画像の表示 (サイズ縮小)
    image = Image.open(uploaded_file)
    col_img, _ = st.columns([1, 4]) 
    with col_img:
        st.image(image, caption="アップロード画像", use_container_width=True)
    
    # 2. 自動商品分析
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

    # 3. 分析結果とキーワード調整
    if "identification_result" in st.session_state:
        st.divider()
        st.subheader("商品特定結果")
        st.write(st.session_state["identification_result"])
        
        st.write("---")
        st.subheader("検索キーワードの調整")
        # ユーザーによるキーワード編集
        search_keywords = st.text_input(
            "市場調査に使用するキーワード:", 
            value=st.session_state.get("search_keywords", "")
        )
        # 変更を保存
        st.session_state["search_keywords"] = search_keywords
        
        if st.button("相場を検索する"):
            if not search_keywords:
                st.error("検索キーワードを入力してください。")
            else:
                with st.spinner(f"メルカリで検索中: {search_keywords}..."):
                    try:
                        crawler = MercariCrawler(headless=True)
                        results = crawler.search_prices(search_keywords)
                        
                        if results["on_sale"] or results["sold_out"]:
                            st.session_state["market_results"] = results
                            # 新規検索時は表示件数をリセット
                            st.session_state.pop("limit_販売中", None)
                            st.session_state.pop("limit_売り切れ", None)
                            st.success(f"「{search_keywords}」の相場データを取得しました！")
                        else:
                            st.warning(f"「{search_keywords}」に該当する商品は見つかりませんでした。")
                    except Exception as e:
                        st.error(f"検索中にエラーが発生しました: {e}")

    # 4. 相場分析結果
    if "market_results" in st.session_state:
        results = st.session_state["market_results"]
        on_sale = results.get("on_sale", [])
        sold_out = results.get("sold_out", [])
        
        st.divider()
        st.subheader("市場分析 (メルカリ)")
        
        # 販売中の状況
        st.write(f"### 現在の出品状況: {len(on_sale)} 件")
        if on_sale:
            on_sale_prices = [item["price"] for item in on_sale]
            avg_on_sale = sum(on_sale_prices) / len(on_sale_prices)
            st.info(f"出品中の平均価格: ¥{int(avg_on_sale):,}")
            display_item_cards(on_sale, "販売中")
        else:
            st.warning("現在販売中の商品はありません。")

        # 売り切れの状況
        st.write(f"### 過去の販売実績: {len(sold_out)} 件")
        if sold_out:
            sold_prices = [item["price"] for item in sold_out]
            avg_sold = sum(sold_prices) / len(sold_prices)
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("平均販売価格", f"¥{int(avg_sold):,}")
            m_col2.metric("最安値", f"¥{min(sold_prices):,}")
            m_col3.metric("最高値", f"¥{max(sold_prices):,}")
            
            st.line_chart(sold_prices)
            display_item_cards(sold_out, "売り切れ")
        else:
            st.warning("販売実績は見つかりませんでした。")

st.divider()
st.caption("Developed by lightyield - テクノロジーで遺品整理をスマートに。")
