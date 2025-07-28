from chromadb import PersistentClient
from ..config import *

client = PersistentClient(path=CHROMA_FOLDER)
collection = client.get_collection(name=CHROMA_COLLECTION_NAME)  

all_data = collection.get()

pdf_names = set()
for metadata in all_data.get("metadatas", []):
    if metadata and "source" in metadata:
        pdf_names.add(metadata["source"])

print("ChromaDB'ye eklenen PDF'ler:")
for name in sorted(pdf_names):
    print(f"- {name}")
