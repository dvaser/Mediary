from .pdf_prep import PDFChunker
from .gemini import GeminiEmbedder, GeminiAnswerGenerator
from .chroma import ChromaDBWrapper
import os
from config import *

class RAGPipeline:
    """
    A modular class for RAG (Retrieval-Augmented Generation) pipeline:
    - Index creation: from PDF → chunk → embed → store in vector DB
    - Question answering: embed query → retrieve relevant chunks → generate answer with Gemini LLM
    """

    def __init__(self, api_key: str, collection_name: str = "pdf_collection"):
        """
        Initialize the pipeline with API key and DB collection name.

        Params:
        - api_key (str): Gemini API key for embeddings and answer generation.
        - collection_name (str): Name of the ChromaDB collection for storing embeddings.
        """
        self.api_key = api_key
        self.collection_name = collection_name
        self.embedder = GeminiEmbedder(api_key)
        self.answer_generator = GeminiAnswerGenerator(api_key)
        self.db = ChromaDBWrapper(collection_name=collection_name)

    def create_index(self, pdf_path: str, word_limit: int = 500) -> int:
        """
        Create or refresh the vector index from a PDF document.

        Params:
        - pdf_path (str): Path to the PDF file to process.
        - word_limit (int): Maximum words per chunk when splitting PDF.

        Returns:
        - int: Number of chunks indexed.
        """
        chunker = PDFChunker(pdf_path)
        chunks = chunker.chunk_pdf(word_limit=word_limit)
        chunker.close()

        embedded_chunks = self.embedder.embed_chunks(chunks)

        ids = [str(i) for i in range(len(embedded_chunks))]
        documents = [item["text"] for item in embedded_chunks]
        embeddings = [item["embedding"] for item in embedded_chunks]  # Burada dict değil sadece embedding listesini alıyoruz

        self.db.add_vectors(ids=ids, documents=documents, embeddings=embeddings)
        return len(embedded_chunks)

    def create_index_from_folder(self, folder_path: str, word_limit: int = 500) -> int:
        """
        Index all PDF files in a given folder into the same vector database.

        Params:
        - folder_path (str): Path to folder containing PDF files.
        - word_limit (int): Max words per chunk.

        Returns:
        - int: Total number of chunks indexed.
        """
        total_chunks = 0
        for file in os.listdir(folder_path):
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(folder_path, file)
                doc_name = os.path.splitext(file)[0]  # "report1.pdf" → "report1"

                chunker = PDFChunker(pdf_path)
                chunks = chunker.chunk_pdf(word_limit=word_limit)
                chunker.close()

                embedded = self.embedder.embed_chunks(chunks)

                ids = [f"{doc_name}_chunk{i}" for i in range(len(embedded))]
                docs = [item["text"] for item in embedded]
                vecs = [item["embedding"] for item in embedded]

                self.db.add_vectors(ids=ids, documents=docs, embeddings=vecs)
                total_chunks += len(embedded)

        return total_chunks

    def answer_question(self, question: str, top_k: int = 3) -> str:
        query_embedding = self.embedder.embed_chunks([question])[0]["embedding"]
        results = self.db.query_vectors(query_embedding, n_results=top_k)
        relevant_texts = results.get("documents", [])

        if relevant_texts and isinstance(relevant_texts[0], list):
            flat_texts = [t for sublist in relevant_texts for t in sublist]
        else:
            flat_texts = relevant_texts

        answer = self.answer_generator.generate_answer_from_context(question, flat_texts)
        return answer   
    
    def chat(self, user_input: str) -> str:
        return self.answer_generator.chat(user_input)
