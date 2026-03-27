import os
from services.rag_service import add_documents

UPLOAD_DIR = "data"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_document(file):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        
    return text

def process_uploaded_file(file):
    text = save_document(file)
    add_documents([text])
    return {"message": f"{file.filename} processed"}