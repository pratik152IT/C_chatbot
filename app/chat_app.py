import streamlit as st
from src.ragpipline import generate_answer

st.set_page_config(page_title="C-Copilot", layout="centered")

st.title("C-Copilot")
st.caption(
    "Ask about your C codebase — code generation, debugging, explanation, and"
    " Q&A."
)

if "messages" not in st.session_state:
  st.session_state.messages = []

for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])

question = st.chat_input("Ask a question about the codebase...")

if question:
  st.session_state.messages.append({"role": "user", "content": question})
  with st.chat_message("user"):
    st.markdown(question)

  with st.chat_message("assistant"):
    with st.spinner("Thinking..."):
      answer = generate_answer(question)
    st.markdown(answer)
  st.session_state.messages.append({"role": "assistant", "content": answer})