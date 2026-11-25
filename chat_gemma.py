# ============================================================
# ローカルLLM Chat
#   Streamlit + Ollama + gemma3:4b で動くチャットアプリ
#
# 起動方法（VS Codeのターミナルで実行）:
#   python -m streamlit run chat_gemma.py
# ============================================================

import streamlit as st
import ollama


# ------------------------------------------------------------
# 設定：使うモデルと、LLMへの基本の指示（システムプロンプト）
# ------------------------------------------------------------
MODEL_NAME = "gemma3:4b"
SYSTEM_PROMPT = "あなたは親切なアシスタントです。どんな質問にも、必ず日本語で答えてください。"


# ------------------------------------------------------------
# ページの設定：ブラウザのタブ名と、画面の見出し
# ------------------------------------------------------------
st.set_page_config(page_title="ローカルLLM Chat")
st.title("ローカルLLM Chat "+MODEL_NAME)

# ------------------------------------------------------------
# 会話履歴の準備
#   st.session_state は、ブラウザを開いている間だけ値を保持する入れ物
#   初回だけ空のリストを作る
# ------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# ------------------------------------------------------------
# これまでの会話を画面に表示する
#   Streamlitは操作のたびにコードを上から実行し直すため、
#   毎回、履歴をすべて表示し直す
# ------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ------------------------------------------------------------
# 画面下の入力欄
#   メッセージが送信されると user_input に文字が入る
# ------------------------------------------------------------
user_input = st.chat_input("メッセージを入力してください")

if user_input:
    # --- ユーザーのメッセージを表示し、履歴に追加する ---
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # --- LLMに渡すメッセージを作る（システムプロンプト ＋ これまでの会話） ---
    messages_for_llm = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages

    # --- Ollama経由でLLMに送り、回答を表示する ---
    with st.chat_message("assistant"):
        try:
            with st.spinner("回答を考えています…"):
                response = ollama.chat(model=MODEL_NAME, messages=messages_for_llm)
            answer = response["message"]["content"]
            st.markdown(answer)

            # 回答も履歴に追加する（次の質問のときにLLMへ渡すため）
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as error:
            # Ollamaが起動していない、モデルが入っていない場合などはここに来る
            st.error(
                "LLMから回答を受け取れませんでした。\n\n"
                f"・Ollamaが起動しているか\n"
                f"・モデル「{MODEL_NAME}」が入っているか（ollama pull {MODEL_NAME}）\n\n"
                f"を確認してください。\n\n詳細：{error}"
            )
            # 回答のない質問が履歴に残らないよう、直前の質問を取り消す
            st.session_state.messages.pop()

# ------------------------------------------------------------
# 画面サイドに会話履歴の消去を入れる
#  今までの会話を消す
# ------------------------------------------------------------
with st.sidebar:
    st.header("設定")
 
    # 練習1：会話の履歴を消す
    if st.button("会話を消す"):
        st.session_state.messages = []