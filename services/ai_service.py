import os
from groq import Groq
import logging
logging.basicConfig(level=logging.INFO)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def ask_llm(question: str):
    try:
        logging.info(f"User question: {question}")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # fast + good
            messages=[
              {
                    "role": "system",
                    "content": "You are a senior AI engineer. Give concise, technical answers with examples."
            },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"LLM Error: {str(e)}")