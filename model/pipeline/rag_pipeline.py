import os
from ..config import *
from ..utils.logger import log
from .pdf_prep import PDFChunker
from .gemini import GeminiEmbedder, GeminiAnswerGenerator
from .chroma import ChromaDBWrapper

def safe_add_to_chroma(db, prefix, ids, docs, embeddings, metadatas=None):
    """
    Safely adds vectors to ChromaDB by first deleting existing vectors with the same prefix.

    Parameters:
    - db (ChromaDBWrapper): The ChromaDB wrapper instance.
    - prefix (str): Prefix used to identify document vectors.
    - ids (list[str]): List of document IDs.
    - docs (list[str]): List of document texts.
    - embeddings (list[list[float]]): List of embedding vectors.
    - metadatas (list[dict] | None): Optional metadata for each document.

    Returns:
    - None
    """
    if metadatas is None or len(metadatas) != len(ids):
        metadatas = [{"source": prefix} for _ in range(len(ids))]
    else:
        # Eğer varsa, boş dict'leri de dolduralım
        metadatas = [
            md if md and isinstance(md, dict) and len(md) > 0 else {"source": prefix} 
            for md in metadatas
        ]

    db.delete_by_prefix(prefix)
    db.add_vectors(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)

class RAGPipeline:
    """
    A modular Retrieval-Augmented Generation (RAG) pipeline class.

    Attributes:
    - api_key (str): API key for accessing the embedding and answer generation services.
    - collection_name (str): Name of the ChromaDB collection.
    - embedder (GeminiEmbedder): Embedding generator instance.
    - answer_generator (GeminiAnswerGenerator): Answer generation model instance.
    - db (ChromaDBWrapper): Database wrapper for vector storage.
    """

    def __init__(self, api_key: str, collection_name: str = CHROMA_COLLECTION_NAME):
        log("RAGPipeline", type="header")
        self.api_key = api_key
        self.collection_name = collection_name

        self.embedder = GeminiEmbedder(
            api_key=api_key,
            batch_size=EMBEDDING_BATCH_SIZE,
            max_concurrent_batches=EMBEDDING_MAX_CONCURRENT,
            max_retry_delay=EMBEDDING_MAX_RETRY_DELAY
        )

        self.answer_generator = GeminiAnswerGenerator(api_key)
        self.db = ChromaDBWrapper(collection_name=collection_name)

    def create_index(self, pdf_path: str, word_limit: int = 500, custom_prefix: str = "", metadata: dict = None) -> int:
        """
        Creates an index from a single PDF file by chunking, embedding, and storing in ChromaDB.

        Parameters:
        - pdf_path (str): Path to the PDF file.
        - word_limit (int): Maximum number of words per chunk.
        - custom_prefix (str): Prefix for document IDs.
        - metadata (dict | None): Optional metadata for each chunk.

        Returns:
        - int: Number of chunks indexed.
        """
        log("create_index", type="func")

        chunker = PDFChunker(pdf_path)
        chunks = chunker.chunk_pdf(word_limit=word_limit)
        chunker.close()

        log(f"'{os.path.basename(pdf_path)}' split into {len(chunks)} chunks.", type="info")

        embedded_chunks = self.embedder.embed_chunks(chunks)
        log(f"{len(embedded_chunks)} chunks embedded for '{os.path.basename(pdf_path)}'.", type="info")

        ids = [f"{custom_prefix}_chunk_{i}" for i in range(len(embedded_chunks))]
        documents = [item["text"] for item in embedded_chunks]
        embeddings = [item["embedding"] for item in embedded_chunks]
        metadatas = [metadata or {} for _ in range(len(embedded_chunks))]

        log("Adding embeddings to ChromaDB...", type="info")
        safe_add_to_chroma(self.db, custom_prefix, ids, documents, embeddings, metadatas)
        log(f"'{os.path.basename(pdf_path)}' successfully indexed.", type="success")

        return len(embedded_chunks)

    def create_index_from_folder(self, folder_path: str, word_limit: int = 500) -> int:
        """
        Creates an index from all PDF files in a specified folder.

        Parameters:
        - folder_path (str): Path to the folder containing PDF files.
        - word_limit (int): Maximum number of words per chunk.

        Returns:
        - int: Total number of chunks indexed from all PDFs.
        """
        log("create_index_from_folder", type="func")

        total_chunks = 0
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
        if not pdf_files:
            log(f"No PDF files found in '{folder_path}'.", type="error")
            return 0

        log(f"Indexing {len(pdf_files)} PDFs from folder '{folder_path}'...", type="info")

        for file in pdf_files:
            pdf_path = os.path.join(folder_path, file)
            doc_name = os.path.splitext(file)[0]

            chunker = PDFChunker(pdf_path)
            chunks = chunker.chunk_pdf(word_limit=word_limit)
            chunker.close()
            log(f"{len(chunks)} chunks generated from '{file}'.", type="info")

            embedded = self.embedder.embed_chunks(chunks)
            log(f"{len(embedded)} chunks embedded for '{file}'.", type="info")

            ids = [f"{doc_name}_chunk_{i}" for i in range(len(embedded))]
            docs = [item["text"] for item in embedded]
            vecs = [item["embedding"] for item in embedded]
            metadatas = [{} for _ in range(len(embedded))]

            log(f"Adding embeddings of '{file}' to ChromaDB...", type="info")
            safe_add_to_chroma(self.db, doc_name, ids, docs, vecs, metadatas)
            log(f"'{file}' indexed successfully.", type="success")
            total_chunks += len(embedded)

        log(f"{total_chunks} chunks indexed from all PDFs.", type="success")
        return total_chunks

    def answer_question(self, question: str, top_k: int = 3, promt_stage: int = 1) -> str:
        """
        Answers a user question using the indexed documents.

        Parameters:
        - question (str): The input question (anamnez ya da anamnez+tetkik).
        - top_k (int): Number of top similar chunks to retrieve.

        Returns:
        - str: The generated answer.
        """
        log("answer_question", type="func")
        
        if not question.strip():
            log("Empty question received in answer_question.", type="warning")
            return "Lütfen geçerli bir soru giriniz."

        
        log(f"Embedding query: '{question}'...", type="info")

        query_embedding = self.embedder.embed_chunks([question])[0]["embedding"]

        log(f"Retrieving top {top_k} relevant chunks...", type="info")
        results = self.db.query_vectors(query_embedding, n_results=top_k)
        relevant_texts = results.get("documents", [])

        if relevant_texts and isinstance(relevant_texts[0], list):
            flat_texts = [t for sublist in relevant_texts for t in sublist]
        else:
            flat_texts = relevant_texts

        if not flat_texts:
            log("No relevant chunks found. Cannot generate answer.", type="warning")
            return "Mediary kapsamında bu bilgiyi bilmiyorum. En yakın zamanda bir doktora başvurun."

        log(f"Generating answer using {len(flat_texts)} relevant chunks.", type="info")
        answer = self.answer_generator.generate_answer_from_context(
            query=question,
            context_chunks=flat_texts,
            stage=promt_stage
        )
        return answer

    def chat(self, user_input: str) -> str:
        """
        Chat method for conversational interaction.

        Parameters:
        - user_input (str): The user input message.

        Returns:
        - str: Model-generated response.
        """
        log("chat", type="func")
        log("Generating response via Gemini chat mode...", type="info")
        return self.answer_generator.chat(user_input)
