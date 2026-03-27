import streamlit as st
import requests

st.set_page_config(page_title="AI Knowledge Assistant", layout="centered")

st.title("🤖 AI Knowledge Assistant")

API_URL = "http://<YOUR-EC2-IP>"  # replace later

query = st.text_input("Ask a question:")

if st.button("Ask"):
    if query:
        with st.spinner("Thinking..."):
            try:
                response = requests.get(f"{API_URL}/ask-rag", params={"query": query})
                data = response.json()

                st.subheader("Answer:")
                st.write(data.get("answer", "No answer"))

                st.subheader("Context:")
                for doc in data.get("context", []):
                    st.write(f"- {doc}")

            except Exception as e:
                st.error(f"Error: {e}")


