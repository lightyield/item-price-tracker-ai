# Item Price Tracker (AI-Powered)

写真からアイテムの商品特定・相場調査を自動化し、出品ドラフトの作成まで支援する、自分専用のローカル実行型ツールです。 マルチモーダルAI（Gemini API）による画像認識と、ブラウザ自動操作（Playwright）を組み合わせて、遺品整理や資産管理の負担を最小化します。

## 1. 開発背景 (Background)

本プロジェクトは、「親戚の遺産整理を円滑に進めること」を主目的として開発されました。
遺品整理において、膨大な品々を適切に扱うための課題をテクノロジーで解決します。

* **鑑定の自動化**: 専門知識がなくても、写真から価値や型番を即座に特定。
* **相場の可視化**: メルカリ等の市場データに基づき、適正な処分・販売価格を把握。
* **出品の効率化**: 調査した情報をそのまま出品情報（タイトル・説明文・価格）へ変換し、処分作業を加速。

## 2. ユースケース (Use Cases)

* **即時レポート**: 遺品を撮影し、その場で相場を確認。残すか売却するかの判断材料にする。
* **一括バッチ処理**: 整理中に撮影した大量の写真を、夜間などにまとめて解析・リスト化。
* **出品ドラフト作成**: 相場情報を元に、メルカリの出品タイトルや説明文をAIが自動生成。

## 3. システム構成 (Architecture)

### 技術スタック
* **UI**: Streamlit (Python-based Web Interface)
* **AI Engine**: Google Gemini 2.5 Flash (google-genai SDK)
* **Search Grounding**: Google Search (正確な商品特定と定価調査)
* **Crawler**: Playwright (メルカリ相場情報取得)
* **Database**: SQLite (ローカル履歴保存用)
* **Language**: Python 3.10+

### 処理フロー
1.  **Input**: 画像（カメラ撮影 or フォルダ一括投入）。
2.  **Analysis**: Gemini API が Google Search を活用して「商品名」「型番」「定価」を特定し、状態に応じた「商品説明文」を生成。
3.  **Search**: 特定したキーワードでメルカリを「新しい順」に自動検索。
4.  **Display**: 上位25件を 5x5 のグリッド形式で表示。SOLD品にはバッジを表示し、視認性の高い高コントラストなデザインを採用。
5.  **Drafting**: (開発中) ブラウザ操作により、メルカリの出品画面に情報を自動入力。

## 4. セットアップ (Setup)

### 必要条件
* Google AI Studio から取得した Gemini API Key
* Python 3.10 以上

### インストール手順
1. `.env` ファイルを作成し、`GEMINI_API_KEY` を設定してください（`.env.example` を参照）。
2. 依存ライブラリをインストールします：
   ```bash
   pip install -r requirements.txt
   ```
3. Playwrightのブラウザをインストールします：
   ```bash
   playwright install chromium
   ```
4. アプリケーションを起動します：
   ```bash
   streamlit run src/main.py
   ```

## 5. コスト管理 (Cost Management)

* **Gemini API**: 無料枠を利用することで、個人利用の範囲内であれば月額費用は無料です。
* **インフラ費**: ローカルPCで実行するため、クラウドサーバー費用は発生しません。
* **検索費用**: 有料検索APIを使わず、ブラウザ自動操作で取得するため無料です。

## 6. 今後の展望 (Roadmap)

* **Phase 1: 精度向上 [進行中]**
    * Google Search Grounding による定価調査・特定精度の向上。
    * バーコード読み取り機能の追加、複数サイト（ヤフオク！、楽天ラクマ）比較。
* **Phase 2: リスト管理**
    * 調査結果のSQLite保存、CSV/Excel出力（遺産目録作成の補助機能）。
* **Phase 3: 出品自動化（Drafting）**
    * AIによるメルカリ出品用タイトル・説明文の自動生成。
    * Playwrightによる出品フォームへの自動入力・下書き保存機能の実装。

## 7. プロジェクト規約 (Project Guidelines)

本プロジェクトの開発ルールや指針については、[GEMINI.md](./GEMINI.md) を参照してください。
