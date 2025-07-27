from .pdf_prep import PDFChunker
from .gemini import GeminiEmbedder, GeminiAnswerGenerator
from .chroma import ChromaDBWrapper
import os
from config import *
from utils.logger import log

class RAGPipeline:
    """
    A modular class for RAG (Retrieval-Augmented Generation) pipeline:
    - Index creation: from PDF → chunk → embed → store in vector DB
    - Question answering: embed query → retrieve relevant chunks → generate answer with Gemini LLM
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

    def create_index(self, pdf_path: str, word_limit: int = 500) -> int:
        log("create_index", type="func")  # Sadece fonksiyon adı
        chunker = PDFChunker(pdf_path)
        chunks = chunker.chunk_pdf(word_limit=word_limit)
        chunker.close()

        log(f"'{os.path.basename(pdf_path)}' dosyasından {len(chunks)} parça oluşturuldu.", type="info")
        embedded_chunks = self.embedder.embed_chunks(chunks)
        log(f"'{os.path.basename(pdf_path)}' için {len(embedded_chunks)} parça gömüldü.", type="info")

        ids = [str(i) for i in range(len(embedded_chunks))]
        documents = [item["text"] for item in embedded_chunks]
        embeddings = [item["embedding"] for item in embedded_chunks]

        log("Gömme işlemleri ChromaDB'ye ekleniyor...", type="info")
        self.db.add_vectors(ids=ids, documents=documents, embeddings=embeddings)
        log(f"'{os.path.basename(pdf_path)}' başarıyla dizine eklendi.", type="success")
        return len(embedded_chunks)

    def create_index_from_folder(self, folder_path: str, word_limit: int = 500) -> int:
        log("create_index_from_folder", type="func")
        total_chunks = 0
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
        if not pdf_files:
            log(f"'{folder_path}' klasöründe PDF dosyası bulunamadı.", type="error")
            return 0
        
        log(f"'{folder_path}' klasöründeki {len(pdf_files)} PDF dosyası dizine ekleniyor...", type="info")

        for file in pdf_files:
            pdf_path = os.path.join(folder_path, file)
            doc_name = os.path.splitext(file)[0]

            chunker = PDFChunker(pdf_path)
            chunks = chunker.chunk_pdf(word_limit=word_limit)
            chunker.close()
            log(f"'{file}' dosyasından {len(chunks)} parça oluşturuldu.", type="info")

            embedded = self.embedder.embed_chunks(chunks)
            log(f"'{file}' için {len(embedded)} parça gömüldü.", type="info")

            ids = [f"{doc_name}_chunk_{i}" for i in range(len(embedded))]
            docs = [item["text"] for item in embedded]
            vecs = [item["embedding"] for item in embedded]

            log(f"'{file}' gömme işlemleri ChromaDB'ye ekleniyor...", type="info")
            self.db.add_vectors(ids=ids, documents=docs, embeddings=vecs)
            log(f"'{file}' başarıyla dizine eklendi.", type="success")
            total_chunks += len(embedded)

        log(f"Tüm PDF dosyalarından toplam {total_chunks} parça dizine eklendi.", type="success")
        return total_chunks

    def answer_question(self, question: str, top_k: int = 3) -> str:
        log("answer_question", type="func")
        log(f"Sorgu '{question}' gömülüyor...", type="info")
        query_embedding = self.embedder.embed_chunks([question])[0]["embedding"]
        
        log(f"Veritabanından en alakalı {top_k} parça aranıyor...", type="info")
        results = self.db.query_vectors(query_embedding, n_results=top_k)
        
        relevant_texts = results.get("documents", [])

        if relevant_texts and isinstance(relevant_texts[0], list):
            flat_texts = [t for sublist in relevant_texts for t in sublist]
        else:
            flat_texts = relevant_texts
        
        if not flat_texts:
            log("İlgili metin parçaları bulunamadı. Cevap oluşturulamıyor.", type="warning")
            return "Üzgünüm, sorunuzla ilgili yeterli bilgi bulamadım."

        log(f"Bulunan {len(flat_texts)} ilgili metinle cevap oluşturuluyor.", type="info")
        answer = self.answer_generator.generate_answer_from_context(question, flat_texts)
        return answer 
    
    def chat(self, user_input: str) -> str:
        log("chat", type="func")
        log("Chat oturumu üzerinden yanıt üretiliyor...", type="info")
        return self.answer_generator.chat(user_input)
