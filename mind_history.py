# 会話履歴を残す
import streamlit as st
import ollama

MODEL = "qwen2.5:7b"
#MODEL ="gemma4:e4b-it-qat"

st.title("ローカルLLMチャット"+ MODEL)

# 会話の履歴を保存する場所（ブラウザを開いている間だけ残る）
if "messages" not in st.session_state:
    st.session_state.messages = []

# これまでの会話を表示
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# 入力欄
if prompt := st.chat_input("メッセージを入力"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 履歴をまとめてOllamaに送る
    response = ollama.chat(model=MODEL, messages=st.session_state.messages)
    answer = response["message"]["content"]

    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)

