import streamlit as st
import os
from dotenv import load_dotenv
import sys

# プロジェクトルートをパスに追加してインポートできるようにする
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.manager import InventoryManager
from ui.tabs.analysis import render_analysis_tab
from ui.tabs.inventory import render_inventory_screen

# 環境変数の読み込み
load_dotenv()

# インベントリマネージャーの初期化
inventory_manager = InventoryManager()

st.set_page_config(
    page_title="AI商品価格トラッカー",
    page_icon="🔍",
    layout="wide"
)

# 環境変数からAPIキーを取得
api_key = os.getenv("GEMINI_API_KEY", "")

st.title("🔍 AI商品価格トラッカー")

if not api_key:
    st.error("⚠️ .envファイルに GEMINI_API_KEY が見つかりません。設定を確認してください。")

# タブの作成
tab_analysis, tab_inventory = st.tabs(["✨ アイテム分析", "📋 アイテム一覧"])

with tab_analysis:
    render_analysis_tab(api_key, inventory_manager)

with tab_inventory:
    render_inventory_screen(api_key, inventory_manager)

st.divider()
st.caption("Developed by lightyield - テクノロジーで整理をスマートに。")
