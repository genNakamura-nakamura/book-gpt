import argparse
import concurrent.futures
import os
import re
from time import sleep

import boto3
import pandas as pd
from dotenv import load_dotenv

import settings

load_dotenv()

bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"


def compute_chapter_ranges() -> dict:
    """split_point.csv から各章タイトル → (start_page, end_page) を返す。"""
    split = pd.read_csv("tmp/split_point.csv")
    page_ajust = settings.first_page - settings.first_page_in_book
    starts = [p - page_ajust for p in split["page_no"]]
    ends = [s - 1 for s in starts[1:]] + [settings.last_page - page_ajust]
    return dict(zip(split["char"], zip(starts, ends)))


def group_files_by_chapter() -> list:
    """index.csv を章単位にまとめる。返り値: [(title, [prompt_file_paths])]"""
    df = pd.read_csv("tmp/index.csv")
    chapters = []
    current_title = None
    current_files = []
    for _, row in df.iterrows():
        if not pd.isna(row["title"]) and row["title"] != "":
            if current_title is not None:
                chapters.append((current_title, current_files))
            current_title = row["title"]
            current_files = [row["file_name"]]
        else:
            current_files.append(row["file_name"])
    if current_title is not None:
        chapters.append((current_title, current_files))
    return chapters


def extract_source_from_prompt(prompt_text: str) -> str:
    """settings.order テンプレートで包まれた prompt ファイルから本文だけを抜き出す。"""
    m = re.search(
        r"^# 入力\n(.+?)\n+あなたはプロの編集者です",
        prompt_text,
        re.DOTALL | re.MULTILINE,
    )
    if m:
        return m.group(1).strip()
    return prompt_text


def load_chapter_source(prompt_files: list) -> str:
    parts = []
    for fn in prompt_files:
        with open(fn, encoding="utf-8") as f:
            text = f.read()
        parts.append(extract_source_from_prompt(text))
    return "\n\n".join(parts)


def load_chapter_before(prompt_files: list) -> str:
    parts = []
    for fn in prompt_files:
        summary_path = fn.replace("prompt/", "summary/")
        with open(summary_path, encoding="utf-8") as f:
            text = f.read()
        text = re.sub(r"^#\s*(要約|出力)\s*\n+", "", text, flags=re.MULTILINE)
        parts.append(text.strip())
    return "\n".join(parts)


def call_llm(prompt: str) -> str:
    messages = [{"role": "user", "content": [{"text": prompt}]}]
    inference_config = {
        "temperature": settings.temperature,
        "maxTokens": settings.refine_max_tokens,
        "stopSequences": [],
    }
    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        inferenceConfig=inference_config,
    )
    return response["output"]["message"]["content"][0]["text"]


def normalize_format(refined_body: str) -> str:
    """行頭全角スペース、行末半角スペース2個（最終行除く）の体裁に整える。"""
    lines = [ln for ln in refined_body.splitlines() if ln.strip()]
    cleaned = []
    for ln in lines:
        if ln.lstrip().startswith("#"):
            continue
        ln = re.sub(r"^[\s　]*[-・*]?\s*", "", ln)
        ln = ln.rstrip()
        if not ln:
            continue
        ln = "　" + ln
        cleaned.append(ln)
    out = []
    for i, ln in enumerate(cleaned):
        if i < len(cleaned) - 1:
            out.append(ln + "  ")
        else:
            out.append(ln)
    return "\n".join(out)


def make_heading(title: str, page_range: tuple) -> str:
    s, e = page_range
    title_full = f"{title} (p.{s}-{e})"
    anchor = title_full.replace(" ", "-")
    return f"# {title_full} {{#{anchor}}}"


def refine_chapter(args):
    title, prompt_files, page_range = args
    print(f"refining: {title}")
    source = load_chapter_source(prompt_files)
    before = load_chapter_before(prompt_files)
    prompt = settings.refine_order.format(
        chapter_source=source,
        chapter_before=before,
    )
    try:
        refined = call_llm(prompt)
        sleep(settings.sleep_time)
    except Exception as e:
        print(f"{title}: error - {e}")
        refined = before
    body = normalize_format(refined)
    heading = make_heading(title, page_range)
    return f"{heading}\n\n{body}"


def main():
    parser = argparse.ArgumentParser(description="章ごとに要約をリファインする")
    parser.add_argument("--out", default="tmp/summary_refined.md", help="出力ファイル")
    parser.add_argument(
        "--only",
        default=None,
        help="特定の章タイトルだけ処理する（部分一致）。例: '第1章'",
    )
    args = parser.parse_args()

    chapter_ranges = compute_chapter_ranges()
    chapters = group_files_by_chapter()

    tasks = []
    for title, files in chapters:
        if args.only and args.only not in title:
            continue
        if title not in chapter_ranges:
            print(f"warn: no page range for {title}")
            page_range = (0, 0)
        else:
            page_range = chapter_ranges[title]
        tasks.append((title, files, page_range))

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=settings.worker_count
    ) as executor:
        results = list(executor.map(refine_chapter, tasks))

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n\n".join(results) + "\n")

    print(f"written: {args.out}")


if __name__ == "__main__":
    main()
