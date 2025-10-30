# HTML to PDF (gensparkスライド用)

このリポジトリには、genspark で生成された（1ページごとに HTML がある）スライド群を1つのPDFにまとめるスクリプトが含まれています。

主なファイル
- `index.py` - HTML（`source/page01.html` など）を PDF にレンダリングして結合するスクリプト。
- `requirements.txt` - 必要な Python パッケージ。

セットアップ（Windows / PowerShell）

1. 仮想環境を作る（任意だが推奨）

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. 依存関係をインストール

```powershell
python -m pip install -r requirements.txt
```

3. Playwright のブラウザをインストール

```powershell
python -m playwright install
```

使い方

スクリプトはプロジェクト直下の `source/` フォルダを参照します。HTML ファイル名は `page01.html`, `page02.html` のようにしておくと順序が自然に決まります。

```powershell
# デフォルト動作: source/ の HTML を探して output.pdf を作る
python index.py

# source フォルダと出力ファイルを指定
python index.py --source source --output slides.pdf

# 一時生成した個別PDFを残す（デバッグ用）
python index.py --keep-temp
```

注意事項
- HTML が外部リソース（CDNやフォント）を参照している場合、オフライン環境では欠落する可能性があります。
- `python -m playwright install --with-deps` を使うとさらに依存を含めたインストールができます（Linuxなど）。

問題が起きたら
- Playwright の import エラー: `pip install playwright` と `python -m playwright install` を確認してください。
- PyPDF2 の import エラー: `pip install PyPDF2` を実行してください。