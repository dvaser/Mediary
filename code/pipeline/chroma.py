import chromadb
from config import *
from utils.logger import log

from chromadb import PersistentClient
from chromadb.config import Settings


class ChromaDBWrapper:
    def __init__(self, collection_name: str):
        log("ChromaDBWrapper", type="header")
        """
        Initializes the ChromaDB client and prepares the collection.
        Uses persistent mode if CHROMA_LOCAL is True, otherwise uses in-memory mode.
        """
        if CHROMA_LOCAL:
            log("[ChromaDB] Persistent mode enabled.", type="info")
            self.client = PersistentClient(path=str(CHROMA_FOLDER))
        else:
            log("[ChromaDB] In-memory mode enabled.", type="info")
            self.client = chromadb.Client(Settings(
                persist_directory=str(CHROMA_FOLDER)
            ))

        self.collection = self.client.get_or_create_collection(name=collection_name)
        log(f"ChromaDB collection '{collection_name}' is ready.", type="info")

    def add_vectors(self, ids: list[str], documents: list[str], embeddings: list[list[float]], metadatas: list[dict] = None) -> None:
        """
        Adds documents and their corresponding embedding vectors to the ChromaDB collection.

        Parameters:
        - ids (list[str]): Unique identifiers for each document.
        - documents (list[str]): Raw text content of each document.
        - embeddings (list[list[float]]): List of float vectors for each document.
        - metadatas (list[dict], optional): Optional metadata for each document.

        Returns:
        - None
        """
        if metadatas is None or any(not md for md in metadatas):
            metadatas = [{"source": "unknown"} for _ in ids]

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        log(f"{len(ids)} vectors added to ChromaDB.", type="success")

        if CHROMA_LOCAL and hasattr(self.client, "persist"):
            self.client.persist()
            log("ChromaDB data persisted to disk.", type="info")

    def query_vectors(self, query_embedding: list[float], n_results: int = 3) -> dict:
        log("query_vectors", type="func")
        """
        Queries the ChromaDB collection to find the most similar vectors to the input embedding.

        Parameters:
        - query_embedding (list[float]): Embedding of the query text.
        - n_results (int): Number of top matches to return.

        Returns:
        - dict: Query result with matching documents and distances.
        """
        log(f"Querying ChromaDB for top {n_results} results.", type="info")
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "distances"]
        )
        log(f"ChromaDB query completed, returned {len(results.get('documents', [[]])[0])} results.", type="success")
        return results

    def delete_by_prefix(self, prefix: str) -> None:
        log("delete_by_prefix", type="func")
        """
        Deletes all vectors from the collection whose IDs start with the given prefix.

        Parameters:
        - prefix (str): The prefix to match against document IDs.

        Returns:
        - None
        """
        all_ids = self.collection.get()["ids"]
        ids_to_delete = [id_ for id_ in all_ids if id_.startswith(prefix)]

        if not ids_to_delete:
            log(f"No vectors found with prefix '{prefix}' to delete.", type="warning")
            return

        self.collection.delete(ids=ids_to_delete)
        log(f"{len(ids_to_delete)} vectors deleted from ChromaDB with prefix '{prefix}'.", type="info")

        if CHROMA_LOCAL and hasattr(self.client, "persist"):
            self.client.persist()
            log("ChromaDB changes persisted after deletion.", type="info")
