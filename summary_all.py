from time import sleep
import settings
import os
import concurrent.futures
import boto3


bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
model_id = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"


# prompt/以下のファイル名をすべて取得する関数
def get_prompt_file_names():
    prompt_file_names = []
    for file_name in os.listdir("prompt"):
        prompt_file_names.append(file_name)

    # ファイル名を昇順に並び替える
    prompt_file_names.sort()

    return prompt_file_names


# 1threadで処理する関数
def one_thread(file_name: str):
    prompt = read_file(file_name)
    print(file_name)

    try:
        summary = generate_summary(prompt)
        sleep(settings.sleep_time)
        write_file(file_name, summary)
    except Exception as e:
        print(file_name + ": error\n" + str(e))


# ファイル名に基づいて読み込みを行う関数
def read_file(file_name: str) -> str:
    with open("prompt/" + file_name, "r") as f:
        prompt = f.read()
    return prompt


# GPTを使用してテキストを生成する関数
def generate_summary(prompt: str) -> str:
    # メッセージの構成
    messages = [
        {
            "role": "user",
            "content": [{"text": prompt}],
        }
    ]

    # 推論設定
    inference_config = {
        "temperature": settings.temperature,
        "maxTokens": settings.max_tokens,
        "stopSequences": [],
    }

    # モデルの呼び出し
    response = bedrock_client.converse(
        modelId=model_id, messages=messages, inferenceConfig=inference_config
    )

    # レスポンスの解析
    response_text = response["output"]["message"]["content"][0]["text"]

    return response_text


# ファイル名に基づいて書き込みを行う関数
def write_file(file_name: str, summary: str):
    with open("summary/" + file_name, "w") as f:
        f.write(summary)


if __name__ == "__main__":
    # summaryディレクトリを作成する
    os.makedirs("summary", exist_ok=True)

    flies = get_prompt_file_names()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=settings.worker_count
    ) as executor:
        results = executor.map(one_thread, flies)
