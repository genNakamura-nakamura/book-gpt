# 作業手順

## 初回セットアップ
1. 依存パッケージをインストール
   ```bash
   poetry install
   ```
2. `.env.example` をコピーして `.env` を作成し、AWS の認証情報を記入
   ```bash
   cp .env.example .env
   ```

## 要約実行
1. pdfをローカルで開く
2. 本の目次、構成を確認する
3. 要約する最初のページを確認する
4. `settings.py`の`first_page`①に要約する最初のページのpdfのviewerでのページ番号を設定する
5. `settings.py`の`first_page_in_book`②に要約する最初のページの画像にあるページ番号を設定する
6. `settings.py`の`last_page`③に要約する最後のページのpdfのviewerでのページ番号を設定する
7. 本のpdfをアップロードし、`book.pdf`に名前を変更する
8. `read_pdf.py`を実行する
```bash
python read_pdf.py
```
9. `search_split_point_candidate.py`を実行する
```bash
python search_split_point_candidate.py
```
10. `tmp/split_point_candidate.csv`が生成されるので、確認し、過不足があれば修正する
11. 10を新規作成した`tmp/split_point.csv`にコピーする
12. `create_prompt.py`を実行する
```bash
python create_prompt.py
```
13. `prompt/XXXX.txt`が生成されるので、確認し、異常があれば修正する
14. `.env` に AWS のアクセスキー、シークレットキーが設定されていることを確認する（初回セットアップで設定済み）
14. `summary_all.py`を実行する
```bash
python summary_all.py
```
15. `summary/XXXX.txt`が生成されるので、確認し、異常があれば、パラメータの調整などを行い、`summary_all.py`や`summary_at_once.py`を実行する
16. 15を繰り返し、すべてのsummaryが正常になったら、`join_summary.py`を実行する
```bash
python join_summary.py
```
17. `tmp/summary.docx`が生成されるので、確認し、異常があれば修正する


## ディレクトリとファイル
### prompt
- 要約処理のための入力テキストが格納されているテキストファイルがあるディレクトリ
### summary
- prompt ディレクトリの対応するファイルから生成された要約テキストファイルが格納されているディレクトリ
### tmp
- 中間処理ステップで使用されるデータファイルが一時的に保存されています:

`df.pickle`: pdfのpandasデータフレームを一時保存するためのファイル  
`index.csv`, `split_point.csv`, `split_point_candidate.csv`: 要約処理のための分割ポイント情報
summary.docx: すべての要約を含む最終的なドキュメント

### Python スクリプト
- check.py: 特定のページの中身を確認するスクリプト。
- create_prompt.py: prompt ディレクトリに保存されている入力テキストを生成するスクリプト。
- join_summary.py: 複数の要約ファイルを単一のドキュメントにまとめるスクリプト。
- read_pdf.py: PDFファイル (`book.pdf`) からテキストを抽出するスクリプト。
- search_split_point_candidate.py: 要約プロセスで使用されるテキストの分割ポイントを見つけるスクリプト。
- settings.py: プロジェクトの設定を定義するファイル。
- summary_all.py: すべての入力テキストを一度に要約するスクリプト。
- summary_at_once.py: 指定したプロンプトのみを要約するスクリプト。

### 設定ファイル
- pyproject.toml: Pythonパッケージ管理のためのツールの設定ファイル。

### その他のファイル
- README.md: このプロジェクトの概要を説明するマークダウンファイル。
- book.pdf: テキストが抽出され処理されるソースPDFドキュメント。