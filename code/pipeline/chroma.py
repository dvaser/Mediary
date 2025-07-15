import chromadb
from config import *

from chromadb import PersistentClient, Client
from chromadb.config import Settings

class ChromaDBWrapper:
    def __init__(self, collection_name: str):
        """
        Initialize the ChromaDB client and collection.
        Uses either in-memory or persistent client based on config.
        """
        if CHROMA_LOCAL:
            print("[ChromaDB] Persistent mode enabled.")
            self.client = PersistentClient(path=str(CHROMA_FOLDER))
        else:
            print("[ChromaDB] In-memory mode enabled.")
            self.client = chromadb.Client(Settings(
                persist_directory=str(CHROMA_FOLDER)  # 👈 STR YAPTIK
            ))

        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_vectors(self, ids: list[str], documents: list[str], embeddings: list[list[float]]) -> None:
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
        
        if CHROMA_LOCAL and hasattr(self.client, "persist"):
            self.client.persist()

    def query_vectors(self, query_embedding: list[float], n_results: int = 3) -> dict:
        """
        Query the collection to find most similar vectors.

        Params:
        - query_embedding (list[float]): Embedding vector of the query.
        - n_results (int): Number of top similar results to return.

        Returns:
        dict: Result containing documents, ids, and distances.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "distances"]
        )
        return results
