cache = {}
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from pinecone import Pinecone
import os
import logging
logging.basicConfig(level=logging.INFO)
import fitz # PyMuPDF



pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("rag-index")

bm25 = None
tokenized_docs = []

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# In-memory storage
documents = []
embeddings = None
chat_history = []


# Step 1: Add documents
def add_documents(texts):
    for i, text in enumerate(texts):
        chunks = chunk_text(text)

        for j, chunk in enumerate(chunks):
            embedding = model.encode(chunk)

            index.upsert([
                (
                    f"{i}-{j}",
                    embedding.tolist(),
                    {"text": chunk}
                )
            ])



# Step 2: Retrieve relevant docs
def retrieve(query, k=3):
    try:
        logging.info(f"Retrieving for query: {query}")

        query_embedding = model.encode(query)

        results = index.query(
            vector=query_embedding.tolist(),
            top_k=k,
            include_metadata=True
        )

        if not results.get("matches"):
            logging.warning("No matches found in vector DB")
            return ["No relevant documents found."]

        docs = list(dict.fromkeys([match["metadata"]["text"] for match in results["matches"]]))

        logging.info(f"Retrieved docs: {docs}")

        return docs

    except Exception as e:
        logging.error(f"Retrieval error: {str(e)}")
        return ["Error during retrieval."]






def rerank(query, docs):
    scores = []

    for doc in docs:
        score = len(set(query.split()) & set(doc.split()))
        scores.append((doc, score))

    ranked = sorted(scores, key=lambda x: x[1], reverse=True)

    return [doc for doc, _ in ranked]




from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))




def generate_answer(query, context_docs):
    context = "\n".join(context_docs)

    prompt = f"""
    Answer the question based ONLY on the context below.

    Context:
    {context}

    Question:
    {query}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in response:
        if hasattr(chunk.choices[0].delta, "content"):
            token = chunk.choices[0].delta.content
            if token:
                yield token

    

def rewrite_query(query):
    prompt = f"Rewrite this query to be more specific:\n{query}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content






def chunk_text(text, chunk_size=200, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text()

    return text

def chunk_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def add_pdf_document(file_path):
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)

    add_documents(chunks)