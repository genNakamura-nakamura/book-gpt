import re
import pandas as pd
import settings


if __name__ == "__main__":
    # tmp/index.csvを読み込む
    df = pd.read_csv("tmp/index.csv")

    # split_point.csvから章ごとの本のページ範囲を計算する
    split = pd.read_csv("tmp/split_point.csv")
    page_ajust = settings.first_page - settings.first_page_in_book
    starts = [p - page_ajust for p in split["page_no"]]
    ends = [s - 1 for s in starts[1:]] + [settings.last_page - page_ajust]
    title_to_range = dict(zip(split["char"], zip(starts, ends)))

    with open("tmp/summary.md", "w", encoding="utf-8") as out:
        for _, row in df.iterrows():
            # summaryから呼び込むためのファイルパスに変更する
            summary_path = row["file_name"].replace("prompt", "summary")

            # summaryを読み込む
            with open(summary_path, encoding="utf-8") as f:
                summary = f.read()

            # モデルが応答に含めがちな「# 要約」「# 出力」ヘッダー行を除去
            summary = re.sub(r"^#\s*(要約|出力)\s*\n+", "", summary, flags=re.MULTILINE)

            # titleがある行は章の開始 → 見出しを書く
            if not pd.isna(row["title"]):
                title = row["title"]
                if title in title_to_range:
                    s, e = title_to_range[title]
                    out.write(f"# {title} (p.{s}-{e})\n\n")
                else:
                    out.write(f"# {title}\n\n")

            out.write(summary.rstrip() + "\n\n")
