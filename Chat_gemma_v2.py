# ============================================================
# ローカルLLM Chat（練習1〜3を追加した完成版）
#   起動方法：python -m streamlit run chat_gemma_v2.py
# ============================================================

import streamlit as st
import ollama


# ------------------------------------------------------------
# 設定：使うモデルと、キャラクターごとの指示（システムプロンプト）
# ------------------------------------------------------------
MODEL_NAME = "gemma3:4b"
CHARACTERS = {
    "怖い先生": "あなたはこわい先生です。叱ってばかり、日本語で100字以内で答えてください。",
    "元気な友達": "あなたは元気な友達です。くだけた明るい日本語で、短めに100字以内答えてください。",
    "悪い友達": "あなたは悪いことばかりする友達です。いじわるな言葉を100字以内で答えてください",
}

# ------------------------------------------------------------
# ページの設定：ブラウザのタブ名と、画面の見出し
# ------------------------------------------------------------
st.set_page_config(page_title="ローカルLLM Chat")
st.title("ローカルLLM Chat "+MODEL_NAME)


# ------------------------------------------------------------
# 会話履歴の準備（初回だけ空のリストを作る）
# ------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# ------------------------------------------------------------
# サイドバー：設定の部品を並べる
# ------------------------------------------------------------
with st.sidebar:
    st.header("設定")

    # ステップ1：キャラクターを選ぶ
    character = st.selectbox("キャラクター", list(CHARACTERS.keys()))
    system_prompt = CHARACTERS[character]

    # ステップ2：回答の自由度（temperature）を選ぶ
    temperature = st.slider("回答の自由度", 0.0, 1.0, 0.7)

    # 練習1：会話の履歴を消す
    if st.button("会話を消す"):
        st.session_state.messages = []


# ------------------------------------------------------------
# これまでの会話を画面に表示する
# ------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ------------------------------------------------------------
# 画面下の入力欄と、LLMとのやりとり
# ------------------------------------------------------------
user_input = st.chat_input("メッセージを入力してください")

if user_input:
    # ユーザーのメッセージを表示し、履歴に追加する
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # LLMに渡すメッセージ（選んだキャラクターの指示 ＋ これまでの会話）
    messages_for_llm = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    with st.chat_message("assistant"):
        try:
            with st.spinner("回答を考えています…"):
                response = ollama.chat(
                    model=MODEL_NAME,
                    messages=messages_for_llm,
                    options={"temperature": temperature},  # 練習3：自由度を渡す
                )
            answer = response["message"]["content"]
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as error:
            st.error(
                "LLMから回答を受け取れませんでした。"
                f"Ollamaが起動しているか、モデル「{MODEL_NAME}」が入っているかを確認してください。\n\n"
                f"詳細：{error}"
            )
            st.session_state.messages.pop()
