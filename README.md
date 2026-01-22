# Book Price Checker 📚

メルカリから本の中古価格情報を取得し、一覧表示する Streamlit アプリケーションです。
タイトルや ISBN コードで検索でき、販売中の商品のみをフィルタリングする機能も備えています。

## 機能

- **キーワード検索**: 本のタイトルまたは ISBN コードで検索可能。
- **フィルタリング**: サイドバーのチェックボックスで「販売中のみ」に絞り込み可能。
- **価格比較**: 検索結果を画像・価格・ステータス（販売中/売り切れ）付きでリスト表示。
- **負荷対策**: サーバー負荷を考慮し、検索ごとに必ず待機時間を設けています。

## 必要環境

- Python 3.9 以上推奨
- Google Chrome (Playwright用)

## ローカルでのセットアップ手順

以下のコマンドを順に実行して、環境構築を行ってください。

### 1. 仮想環境の作成と有効化

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Mac / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 3. Playwright ブラウザのインストール

Playwright が使用するブラウザバイナリをインストールします。

```bash
playwright install
```

### 4. アプリの起動

```bash
streamlit run app.py
```

ブラウザが立ち上がり、アプリが表示されます。

## GitHub へのプッシュ手順

このプロジェクトを GitHub にアップロードする手順です。

```bash
# 1. Gitの初期化（まだ行っていない場合）
git init

# 2. 全ファイルをステージング
git add .

# 3. コミット
git commit -m "Initial commit: book-price-checker"

# 4. メインブランチ名を main に変更
git branch -M main

# 5. リモートリポジトリを追加（各自のURLに置き換えてください）
git remote add origin https://github.com/yumina2021/book-price-checker.git

# 6. プッシュ
git push -u origin main
```

## Streamlit Cloud でのデプロイ手順

1. [Streamlit Cloud](https://streamlit.io/cloud) にログインします。
2. "New app" をクリックします。
3. GitHub リポジトリ（`book-price-checker`）を選択します。
4. Main file path に `app.py` を指定します。
5. "Deploy!" をクリックします。

※ リポジトリ内の `packages.txt` により、自動的に必要なブラウザ環境が構築されます。

## 注意事項

- 本アプリはスクレイピング技術を使用しています。各サイトの利用規約を遵守し、短時間に大量のリクエストを送らないよう注意してください。
- アプリ内では検索ごとに意図的に1秒以上のウェイトを入れています。
