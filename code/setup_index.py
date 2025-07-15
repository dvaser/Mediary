from pipeline.rag_pipeline import RAGPipeline
from config import *

pipeline = RAGPipeline(api_key=API_KEY)

if TEST:
    PDF_FILE_PATH = SOURCE_FOLDER / PDF_FILE
    n_chunks = pipeline.create_index(PDF_FILE_PATH)
    print(f"Indexed {n_chunks} chunks.")
else:
    indexed = pipeline.create_index_from_folder(SOURCE_FOLDER)
    print(f"Total {indexed} chunks.")
