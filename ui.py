import streamlit as st
import requests

st.set_page_config(page_title="AI Assistant", layout="wide")

st.title("🤖 AI Knowledge Assistant")

API_URL = "http://54.156.120.43/api"  # update this

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
user_input = st.chat_input("Ask something...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.get(
                    f"{API_URL}/ask-rag",
                    params={"query": user_input}
                )

                data = response.json()
                answer = data.get("answer", "No response")

                st.markdown(answer)

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                st.error(f"Error: {e}")


