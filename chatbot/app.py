import streamlit as st
from rag import rag_query, build_vectorstore, general_chat

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("🤖 AI Chatbot")

# Sidebar
with st.sidebar:
    st.header("Settings")
    mode = st.radio("Mode", ["💬 General Chat", "📄 Chat with Documents"])

    if mode == "📄 Chat with Documents":
        st.divider()
        st.markdown("**Documents**")
        st.info("Drop your PDFs into the `docs/` folder, then click Rebuild.")
        if st.button("🔄 Rebuild Knowledge Base"):
            with st.spinner("Building knowledge base..."):
                build_vectorstore()
            st.success("Knowledge base ready!")

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Ask something..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if mode == "📄 Chat with Documents":
                response = rag_query(prompt)
            else:
                # Pass full history for context
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                response = general_chat(history)

        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
