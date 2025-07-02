# read_pdf.pyの設定
# 処理を行う最初のページ（pdfviewerで確認した値）-①
first_page: int = 23

# 処理を行う最初のページに記載されているページ数（pdfの画像内にある値）-②
first_page_in_book: int = 15

# 処理を行う最後のページ（pdfviewerで確認した値）-③
last_page: int = 298

# pdfのパス
pdf_path: str = "deelbook.pdf"

# search_split_point_candidate.pyの設定
# 検索する文字サイズの最小値 -④
min_font_size: int = 10
# 検索する文字サイズの最大値 -⑤
max_font_size: int = 100


# create_prompt.pyの設定
# プロンプトに一度に入力するぺージ数 -⑥
page_count: int = 12
# 入力する命令 -⑦
order: str = '''# 入力
{text}

あなたはプロの編集者です。
以下の制約条件に従って、上記の文章を箇条書きで要約してください。
# 制約条件
・架空の表現や言葉を使用しない。
・文章中の数値には変更を加えない。
・各要素に対応する文章の頭のページ番号を箇条書きの末尾につける。
・「だ・である調」で要約する。
・体言止めをしない。
・全てのページについて、1ページにつき1つ以上は要素を書き出す。
・なるべく固有名詞を拾うようにする。

# 出力例
 - マスコミはこれらの本をまともなものとして扱っていた (p.25)
 - 1987年12月27日、テレビ東京は「国際ユダヤ資本家」のドキュメンタリーを全国放映 (p.25-26)

# 出力
以下に要約を箇条書きで作成した。:
 - 
'''

# summary.pyの設定
# temperatureの設定
temperature: float = 0.1
# top_pの設定
top_p: float = 0.99
# max_tokensの設定
max_tokens: int = 3900
# 実行時のsleep時間 -⑧
sleep_time: int = 1
# 実行時に同時に処理する数 -⑨
worker_count: int = 2

# summary_at_once.pyの設定 -⑩
file_name: str = "0003.txt"