import chromadb
from config import *
from utils.logger import log

from chromadb import PersistentClient, Client
from chromadb.config import Settings

class ChromaDBWrapper:
    def __init__(self, collection_name: str):
        log("ChromaDBWrapper", type="header")
        """
        Initialize the ChromaDB client and collection.
        Uses either in-memory or persistent client based on config.
        """
        if CHROMA_LOCAL:
            log("[ChromaDB] Persistent mode enabled.", type="info")
            self.client = PersistentClient(path=str(CHROMA_FOLDER))
        else:
            log("[ChromaDB] In-memory mode enabled.", type="info")
            self.client = chromadb.Client(Settings(
                persist_directory=str(CHROMA_FOLDER)  # 👈 STR YAPTIK
            ))

        self.collection = self.client.get_or_create_collection(name=collection_name)
        log(f"ChromaDB collection '{collection_name}' hazırlandı.", type="info")

    def add_vectors(self, ids: list[str], documents: list[str], embeddings: list[list[float]]) -> None:
        log("add_vectors", type="func")
        """
        Add documents and their embeddings to the collection.

        Params:
        - ids (list[str]): Unique IDs for each document.
        - documents (list[str]): Text documents.
        - embeddings (list[list[float]]): Corresponding embedding vectors.

        Returns:
        None
        """
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings
        )
        
        log(f"ChromaDB'ye {len(ids)} vektör eklendi.", type="success")

        if CHROMA_LOCAL and hasattr(self.client, "persist"):
            self.client.persist()
            log("ChromaDB persistent client ile veriler kalıcı hale getirildi.", type="info")

    def query_vectors(self, query_embedding: list[float], n_results: int = 3) -> dict:
        log("query_vectors", type="func")
        """
        Query the collection to find most similar vectors.

        Params:
        - query_embedding (list[float]): Embedding vector of the query.
        - n_results (int): Number of top similar results to return.

        Returns:
        dict: Result containing documents, ids, and distances.
        """
        log(f"ChromaDB'den en iyi {n_results} sonuç sorgulanıyor.", type="info")
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "distances"]
        )
        log(f"ChromaDB sorgusu tamamlandı, {len(results.get('documents', [[]])[0])} sonuç döndü.", type="success")
        return results
