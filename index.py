"""
HTMLスライド（複数の pageNN.html）を1つのPDFにまとめるスクリプト

使い方（簡単）:
  python index.py --source source --output output.pdf

実装方針:
  - Playwright (Chromium) を用いて各HTMLを PDF にレンダリング
  - 一時的に生成した PDF を PyPDF2 で結合して最終出力を作成
  - Playwright 未インストール時は分かりやすい案内を出力する

注意:
  - 初回は `pip install -r requirements.txt` と `python -m playwright install` が必要
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import List


def find_html_files(source_dir: Path) -> List[Path]:
	# 優先的に pageNN.html パターンを探す。無ければ *.html を全部使う
	files = sorted(source_dir.glob("page*.html"))
	if not files:
		files = sorted(source_dir.glob("*.html"))
	return files


def render_pdfs_with_playwright(html_files: List[Path], out_dir: Path) -> List[Path]:
	"""各HTMLをPlaywrightでPDFにして一時ファイルとして保存し、パス一覧を返す"""
	try:
		from playwright.sync_api import sync_playwright
	except Exception as e:  # pragma: no cover - runtime environment dependent
		raise RuntimeError(
			"Playwright のインポートに失敗しました。\n"
			"まず `pip install -r requirements.txt` を実行し、\n"
			"続いて `python -m playwright install` を実行してブラウザをインストールしてください。\n"
			f"詳細: {e}"
		)

	pdf_paths: List[Path] = []
	with sync_playwright() as p:
		browser = p.chromium.launch()
		page = browser.new_page()
		for html in html_files:
			uri = html.resolve().as_uri()
			out_pdf = out_dir / f"{html.stem}.pdf"
			# ページに移動してから PDF を出力
			page.goto(uri, wait_until="networkidle")
			# print_background=True で背景CSSを含める
			page.pdf(path=str(out_pdf), print_background=True)
			pdf_paths.append(out_pdf)
		browser.close()

	return pdf_paths


def merge_pdfs(pdf_files: List[Path], output_path: Path) -> None:
	try:
		from PyPDF2 import PdfMerger
	except Exception as e:  # pragma: no cover
		raise RuntimeError(
			"PyPDF2 のインポートに失敗しました。\n"
			"`pip install PyPDF2` を実行してください。\n"
			f"詳細: {e}"
		)

	merger = PdfMerger()
	for pdf in pdf_files:
		merger.append(str(pdf))
	with open(output_path, "wb") as f:
		merger.write(f)
	merger.close()


def main(argv: List[str] | None = None) -> int:
	p = argparse.ArgumentParser(description="Merge HTML slides (pageXX.html) into a single PDF using Playwright")
	p.add_argument("--source", "-s", default="source", help="source フォルダ（HTML が入っている場所）")
	p.add_argument("--output", "-o", default="output.pdf", help="出力 PDF ファイル名")
	p.add_argument("--keep-temp", action="store_true", help="一時生成したPDFを削除せずに残す")
	args = p.parse_args(argv)

	script_dir = Path(__file__).parent.resolve()
	source_dir = (script_dir / args.source).resolve()
	if not source_dir.exists() or not source_dir.is_dir():
		print(f"source フォルダが見つかりません: {source_dir}")
		return 2

	html_files = find_html_files(source_dir)
	if not html_files:
		print(f"HTML ファイルが見つかりませんでした: {source_dir}")
		return 3

	print(f"見つかったHTMLファイル({len(html_files)}):")
	for hf in html_files:
		print(f"  - {hf.name}")

	output_path = (script_dir / args.output).resolve()

	with tempfile.TemporaryDirectory() as tmpdir:
		tmpdir_path = Path(tmpdir)
		try:
			print("Playwright を使って HTML を PDF にレンダリングしています...")
			pdf_files = render_pdfs_with_playwright(html_files, tmpdir_path)
		except RuntimeError as e:  # helpful message already included
			print(e)
			return 4

		print("PDF を結合しています...")
		merge_pdfs(pdf_files, output_path)

		if args.keep_temp:
			kept = [str(p) for p in pdf_files]
			print("一時PDFを保持しました:")
			for k in kept:
				print("  - ", k)
		else:
			# TemporaryDirectory のコンテキストが抜けると自動削除される
			print("一時ファイルは自動的に削除されます。"
				  f" 出力: {output_path}")

	print("完了しました。")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

