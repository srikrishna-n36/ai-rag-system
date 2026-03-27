import streamlit as st
import requests

st.set_page_config(page_title="AI Assistant", layout="wide")

st.title("🤖 AI Knowledge Assistant")

API_URL = "http://54.156.120.43/api"

def stream_response(query):
    url = f"{API_URL}/ask-rag-stream"
    response = requests.get(url, params={"query": query}, stream=True)

    full_text = ""
    placeholder = st.empty()

    for chunk in response.iter_content(chunk_size=1):
        if chunk:
            text = chunk.decode("utf-8")
            full_text += text
            placeholder.markdown(full_text)

    return full_text



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
            answer = stream_response(user_input)

            st.session_state.messages.append({"role": "assistant", "content": answer})
            


uploaded_file = st.file_uploader("Upload a document (txt or pdf)", type=["txt", "pdf"])

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    files = {"file": open("temp.pdf", "rb")}

    res= requests.post(f"{API_URL}/upload-pdf", files=files)

    st.success("PDF uploaded and processed successfully!")