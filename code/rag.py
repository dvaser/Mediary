from PyPDF2 import PdfReader

reader = PdfReader("dosya.pdf")
all_text = ""
for page in reader.pages:
    all_text += page.extract_text()


def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i+chunk_size])
    return chunks


from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
vectors = model.encode(chunks)

index = faiss.IndexFlatL2(vectors.shape[1])
index.add(np.array(vectors))
