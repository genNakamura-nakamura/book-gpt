# 作業手順

## 初回セットアップ
```bash
poetry shell
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
14. AWSのアクセスキー、シークレットキーを設定する
```bash
export AWS_ACCESS_KEY_ID="Axxxxxxxxxxxxxxxxxxxxxxx"
export AWS_SECRET_ACCESS_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```
14. `summary_all.py`を実行する
```bash
python summary_all.py
```
15. `summary/XXXX.txt`が生成されるので、確認し、異常があれば、パラメータの調整などを行い、`summary_all.py`や`summary_at_once.py`を実行する
16. 15を繰り返し、すべてのsummaryが正常になったら、`join_summary.py`を実行する
```bash
python join_summary.py
```
17. `tmp/summary.md`が生成されるので、確認し、異常があれば修正する

## 要約のリファイン（任意）
プログラムで生成した素の要約を、手作業で行っていた仕上げ（脱線項目の削除、関連項目の統合、人物の肩書き補足、原文に照らした誤字・誤訳修正、Markdownフォーマット整形）にLLMで近づける後処理。

`tmp/summary.md`（マージ済み）をベースに、章単位で原文と現在の要約をLLMに渡し直し、`tmp/summary_refined.md`を出力する。

18. `refine_summary.py`を実行する
```bash
python refine_summary.py
```
- 特定の章だけリファインしたい場合:
  ```bash
  python refine_summary.py --only "第1章"
  ```
- 出力ファイル名を変えたい場合:
  ```bash
  python refine_summary.py --out tmp/summary_refined_test.md
  ```
19. `tmp/summary_refined.md`が生成されるので、内容を確認する
20. 出力の傾向を変えたい場合は`settings.py`の`refine_order`（リファイン用プロンプト）や`refine_max_tokens`を編集して再実行する
    - 項目を多く残したい→ルール1の「6～8割を残す」を「8～9割を残す」に
    - 圧縮を強めたい→「4～6割に圧縮」に
    - 章が長くて出力が途切れる→`refine_max_tokens`を増やす


## ディレクトリとファイル
### prompt
- 要約処理のための入力テキストが格納されているテキストファイルがあるディレクトリ
### summary
- prompt ディレクトリの対応するファイルから生成された要約テキストファイルが格納されているディレクトリ
### tmp
- 中間処理ステップで使用されるデータファイルが一時的に保存されています:

`df.pickle`: pdfのpandasデータフレームを一時保存するためのファイル  
`index.csv`, `split_point.csv`, `split_point_candidate.csv`: 要約処理のための分割ポイント情報  
`summary.md`: `join_summary.py`によって生成される、すべての章の要約をまとめた最終ドキュメント  
`summary_refined.md`: `refine_summary.py`によって生成される、LLMで仕上げを行った完成形に近いドキュメント

### Python スクリプト
- check.py: 特定のページの中身を確認するスクリプト。
- create_prompt.py: prompt ディレクトリに保存されている入力テキストを生成するスクリプト。
- join_summary.py: 複数の要約ファイルを単一のドキュメントにまとめるスクリプト。
- read_pdf.py: PDFファイル (`book.pdf`) からテキストを抽出するスクリプト。
- search_split_point_candidate.py: 要約プロセスで使用されるテキストの分割ポイントを見つけるスクリプト。
- settings.py: プロジェクトの設定を定義するファイル。
- summary_all.py: すべての入力テキストを一度に要約するスクリプト。
- summary_at_once.py: 指定したプロンプトのみを要約するスクリプト。
- refine_summary.py: 生成された要約を章単位でLLMに再投入し、手仕上げに近い形へリファインするスクリプト。`tmp/summary_refined.md`を出力する。

### 設定ファイル
- pyproject.toml: Pythonパッケージ管理のためのツールの設定ファイル。

### その他のファイル
- README.md: このプロジェクトの概要を説明するマークダウンファイル。
- book.pdf: テキストが抽出され処理されるソースPDFドキュメント。