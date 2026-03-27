from http import client

from fastapi import FastAPI
from fastapi import HTTPException
from services.crypto_service import fetch_crypto_data as fetch_data
from utils.processor import process_crypto_data as process_data
from services.ai_service import ask_llm
from fastapi import HTTPException
from services.rag_service import add_documents, retrieve, generate_answer
from fastapi.responses import StreamingResponse
from services.rag_service import retrieve, generate_answer, rewrite_query
from fastapi import UploadFile, File
from services.document_service import process_uploaded_file


app = FastAPI()

@app.get("/")
def root():
	return {"message": "API is running "}

@app.get("/crypto")
async def get_crypto():
	raw_data = await fetch_data()
	
	if "error" in raw_data:
		raise HTTPException(status_code=500, detail="External API error")
	
	processed = process_data(raw_data)
	return {
		"message" : "async Crypto Prices",
		"data": processed
	}

@app.get("/top-currency")
async def top_currency():
    raw_data = await fetch_data()

    usd = raw_data["bpi"]["USD"]["rate_float"]
    gbp = raw_data["bpi"]["GBP"]["rate_float"]

    if usd > gbp:
        return {"top": "USD", "value": usd}
    else:
        return {"top": "GBP", "value": gbp}

@app.get("/insights")
async def insights():
    raw_data = await fetch_data()
    usd = raw_data["bpi"]["USD"]["rate_float"]

    if usd > 50000:
        insight = "Bitcoin is at a high price range."
    else:
        insight = "Bitcoin is relatively lower."

    return {"insight": insight}

@app.get("/status")
async def status():
    return {"service": "running", "version": "1.0"}

@app.get("/ask-ai")
async def ask_ai(question: str):
    try:
        answer = await ask_llm(question)
        return {"question": question, "answer": answer}
    except Exception:
        raise HTTPException(status_code=500, detail="LLM request failed")
    
@app.post("/add-docs")
def add_docs():
    print("ADD DOCS CALLED")  # DEBUG

    sample_docs = [
    "Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval with text generation.",
    "RAG retrieves relevant documents from a knowledge base and uses them to generate accurate responses.",
    "Transformers are deep learning models used in natural language processing tasks.",
    "Vector databases store embeddings and allow similarity search."
]

    add_documents(sample_docs)

    return {"message": "Documents added"}

@app.get("/ask-rag")
def ask_rag(query: str):
    context_docs = retrieve(query)

    if "No documents" in context_docs[0]:
        return {"error": context_docs[0]}

    answer = generate_answer(query, context_docs)

    return {
        "query": query,
        "context_used": context_docs,  # renamed
        "answer": answer
    }

@app.get("/ask-rag-stream")
def ask_rag_stream(query: str):

    rewritten_query = rewrite_query(query)

    context_docs = retrieve(rewritten_query)

    def stream_answer():
        context = "\n\n".join(context_docs)

        prompt = f"""
        Answer using the context below.

        Context:
        {context}

        Question:
        {rewritten_query}
        """

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in response:
            yield chunk.choices[0].delta.content or ""

    return StreamingResponse(stream_answer(), media_type="text/plain")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
	try:
		result = process_uploaded_file(file)
		return result
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@app.post("/chat")
def chat(query: str):
	context_docs = retrieve(query)

	if "No documents" in context_docs[0]:
		return {"error": context_docs[0]}

	answer = generate_answer(query, context_docs)

	return {
		"query": query,
		"context_used": context_docs,
		"answer": answer
	}

@app.get("/chat-stream")
def chat_stream(query: str):

	

	context_docs = retrieve(query)

	def stream():
		context = "\n\n".join(context_docs)

		prompt = f"""
		Answer using the context below.

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
			yield chunk.choices[0].delta.content or ""

	return StreamingResponse(stream(), media_type="text/plain")

@app.get("/health")
def health():
	return {"status": "ok"}