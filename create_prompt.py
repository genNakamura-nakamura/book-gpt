import os
import pandas as pd
import pickle
import settings


# tmp/split_point.csvを読み込む関数
def read_split_point() -> pd.DataFrame:
    return pd.read_csv("tmp/split_point.csv")


# tmp/df.pickleを読み込む関数
def read_df_book() -> pd.DataFrame:
    with open("tmp/df.pickle", "rb") as f:
        return pickle.load(f)


# 最後のページのindexを取得する関数
def get_last_page_index(df: pd.DataFrame) -> pd.Index:
    return pd.Index([settings.last_page - 1])


if __name__ == "__main__":
    # promptディレクトリを削除する
    if os.path.exists("prompt"):
        for file in os.listdir("prompt"):
            os.remove(os.path.join("prompt", file))
        os.rmdir("prompt")

    # promptディレクトリを作成する
    os.makedirs("prompt", exist_ok=True)

    # split_point.csvを読み込む
    split_point = read_split_point()

    # df_bookを読み込む
    df_book = read_df_book()

    print("split_point")

    # split_pointのindexをpage_no  block_noに変更する
    split_point = split_point.set_index(["page_no", "block_no"])

    # split_pointのchar列をtitle列に変更する
    split_point = split_point.rename(columns={"char": "title"})

    df_book = df_book.groupby(["page_no", "block_no"])["char"].apply(
        lambda x: "".join(x)
    )

    # df_bookとsplit_pointを結合する
    df = pd.concat([split_point, df_book], axis=1)

    # dfのindexをsortする
    df = df.sort_index()

    # title列がNaNではない行を識別する列を追加する
    df["is_title"] = df["title"].notnull()

    # is_titleがTrueの行のindexを取得する
    start_split_point_index = df[df["is_title"]].index

    # is_title列を上にシフトする
    df["next_is_title"] = df["is_title"].shift(-1)

    # next_is_title列のNaNをFalseに置換する
    df["next_is_title"] = df["next_is_title"].fillna(False)

    # next_is_titleがTrueの行のindexを取得する
    end_split_point_index = df[df["next_is_title"]].index

    # end_split_point_indexの最初を削除する
    end_split_point_index = end_split_point_index[1:]

    last_index = get_last_page_index(df)

    # end_split_point_indexの最後にdfの最後のindexを追加する
    end_split_point_index = end_split_point_index.append(last_index)

    file_count = 0
    file_index = []
    for s, e in zip(start_split_point_index, end_split_point_index):
        # dfをstart_split_point_indexとend_split_point_indexで分割する
        print(s, e)
        df_sub = df.loc[s:e, ["title", "char"]]

        df_text = df_sub.groupby(["page_no"])[
            "char"].apply(lambda x: "\n".join(x))

        # page数を合わせる
        page_ajust = settings.first_page - settings.first_page_in_book
        page_num = df_text.index - page_ajust

        # df_textにindexの文字列とchar列を結合する
        df_text = "p." + page_num.astype(str) + "\n" + df_text

        # df_textをsettings.page_countで分割する
        grouped_df_text = [df_text[i:i+settings.page_count]
                           for i in range(0, len(df_text), settings.page_count)]
        
        title = df_sub["title"].iloc[0]

        for group in grouped_df_text:
            # グループ内のテキストを結合
            text = "\n".join(group)

            # promptと結合する
            text = settings.order.format(text=text)

            # promptを保存する 4桁で0埋めする
            file_name = f"prompt/{file_count:04}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(text)

            file_index.append([file_name, title])

            title = ""

            file_count += 1

    # index.csvを保存する
    pd.DataFrame(file_index, columns=["file_name", "title"]).to_csv(
        "tmp/index.csv", index=False
    )
