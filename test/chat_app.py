import streamlit as st
from ragpipline import generate_answer

st.set_page_config(page_title="C-Copilot", layout="centered")

st.title("C-Copilot")
st.caption("Ask about your C codebase — code generation, debugging, explanation, and Q&A.")

# Keep chat history across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input box at the bottom
question = st.chat_input("Ask a question about the codebase...")

if question:
    # Show the user's question immediately
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate and show the answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = generate_answer(question)
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})