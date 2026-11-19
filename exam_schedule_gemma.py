# ============================================================
# exam_schedule_gemma.py
# 試験日程の通知文を、英語・ドイツ語・韓国語に翻訳するエージェント
#
# 起動方法（VS Codeのターミナルで実行）:
#   python -m streamlit run exam_schedule_gemma.py
# ============================================================

import re
import unicodedata

import requests
import streamlit as st

# ------------------------------------------------------------
# 1. 画面の基本設定（ブラウザのタブ名）
#    ※ st.set_page_config は、ほかの st. より先に書く
# ------------------------------------------------------------
st.set_page_config(page_title="ローカルLLM Chat", page_icon="🌐")

# ------------------------------------------------------------
# 2. 設定値（変更するときは、ここだけ直せばよい）
# ------------------------------------------------------------
MODEL = "gemma4:e2b-it-qat"
OLLAMA_URL = "http://localhost:11434/api/chat"

# 翻訳先の言語（言語を増やすときは、ここに1行追加する）
# 左：画面に表示する名前、右：AIに伝える言語名
LANGUAGES = {
    "英語": "English",
    "ドイツ語": "German",
    "韓国語": "Korean",
}

# 翻訳エージェントへの指示（システムプロンプト）
# {language} の部分に、翻訳先の言語名が入る
SYSTEM_PROMPT = """あなたは大学の事務室で、学生向けの重要な通知を翻訳する担当者です。
次のルールを必ず守ってください。
- 日本語の通知文を{language}に翻訳する。
- 日付・時刻・曜日・教室・科目名などの情報は、変更・追加・省略をしない。
- 日付と時刻は、月名などの単語に置き換えず、原文と同じ数字で書く。
- 原文に書かれていない情報を付け加えない。
- 翻訳文だけを出力し、説明や前置きは書かない。"""


# ------------------------------------------------------------
# 3. 翻訳エージェント：1つの言語に翻訳する
#    会話の履歴は送らず、毎回「指示」と「通知文」だけを送る
# ------------------------------------------------------------
def translate(text, language):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(language=language)},
        {"role": "user", "content": text},
    ]
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False,                   # 回答をまとめて受け取る
            "think": False,                    # 考える過程を省いて速くする
            "options": {"temperature": 0},     # 毎回同じ訳になるようにする
        },
    )
    response.raise_for_status()                # エラーがあればここで止める
    return response.json()["message"]["content"]


# ------------------------------------------------------------
# 4. 確認係：原文の数字（日付・時刻など）が翻訳文に残っているか調べる
#    見つからない数字があれば、そのリストを返す
# ------------------------------------------------------------
def find_missing_numbers(original, translation):
    # 全角の数字（１２）を半角（12）にそろえる
    original = unicodedata.normalize("NFKC", original)
    translation = unicodedata.normalize("NFKC", translation)

    original_numbers = re.findall(r"\d+", original)
    translated_numbers = re.findall(r"\d+", translation)

    missing = []
    for number in original_numbers:
        if number not in translated_numbers and number not in missing:
            missing.append(number)
    return missing


# ------------------------------------------------------------
# 5. 画面の見出し
# ------------------------------------------------------------
st.title("試験日程 翻訳エージェント")
st.caption(
    "通知文を入力すると、" + "・".join(LANGUAGES) + "に翻訳します。"
    "会話は続けず、毎回入力した通知文だけを翻訳します。"
)

# ------------------------------------------------------------
# 6. 履歴の準備
#    st.session_state に入れておくと、ブラウザを開いている間は消えない
#    ※ この履歴は画面に表示するためだけに使い、AIには送らない
# ------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------------------------------------------------
# 7. これまでの履歴を画面に表示する
#    （改行をそのまま表示するため、"\n" を "  \n" に置き換えている）
# ------------------------------------------------------------
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace("\n", "  \n"))

# ------------------------------------------------------------
# 8. 画面下の入力欄に通知文が入力されたときの処理
# ------------------------------------------------------------
notice = st.chat_input("通知文を入力してください（Shift+Enterで改行）")

if notice:
    # 8-1. 入力された通知文を表示して、履歴に残す
    with st.chat_message("user"):
        st.markdown(notice.replace("\n", "  \n"))
    st.session_state.history.append({"role": "user", "content": notice})

    # 8-2. 言語ごとに翻訳エージェントを呼び出し、確認係でチェックする
    result = ""
    try:
        for name, language in LANGUAGES.items():
            with st.spinner(f"{name}に翻訳しています..."):
                translation = translate(notice, language)

            result += f"### {name}\n\n{translation}\n\n"

            missing = find_missing_numbers(notice, translation)
            if missing:
                result += (
                    f"⚠️ **確認してください**：原文の数字 {', '.join(missing)} "
                    "が翻訳文に見つかりません。\n\n"
                )
    except requests.exceptions.RequestException as error:
        st.error(
            "Ollamaから回答を受け取れませんでした。\n\n"
            "・Ollamaが起動しているか確認してください。\n"
            f"・モデルがない場合は、ターミナルで `ollama pull {MODEL}` を実行してください。\n\n"
            f"（詳細：{error}）"
        )
        st.stop()

    # 8-3. 翻訳結果を表示して、履歴に残す
    with st.chat_message("assistant"):
        st.markdown(result.replace("\n", "  \n"))
    st.session_state.history.append({"role": "assistant", "content": result})
