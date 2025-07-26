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

    def __init__(self, api_key: str, collection_name: str = CHROMA_COLLECTION_NAME):
        """
        Initialize the pipeline with API key and DB collection name.

        Params:
        - api_key (str): Gemini API key for embeddings and answer generation.
        - collection_name (str): Name of the ChromaDB collection for storing embeddings.
        """
        self.api_key = api_key
        self.collection_name = collection_name
        
        self.embedder = GeminiEmbedder(
            api_key=api_key,
            batch_size=EMBEDDING_BATCH_SIZE,         # config.py'den veya sabit bir değer
            max_concurrent_batches=EMBEDDING_MAX_CONCURRENT, # config.py'den veya sabit bir değer
            max_retry_delay=EMBEDDING_MAX_RETRY_DELAY # config.py'den veya sabit bir değer
        )

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

        print(f"[i] '{os.path.basename(pdf_path)}' dosyasından {len(chunks)} parça oluşturuldu.")
        embedded_chunks = self.embedder.embed_chunks(chunks)
        print(f"[i] '{os.path.basename(pdf_path)}' için {len(embedded_chunks)} parça gömüldü.")

        ids = [str(i) for i in range(len(embedded_chunks))]
        documents = [item["text"] for item in embedded_chunks]
        embeddings = [item["embedding"] for item in embedded_chunks]

        print(f"[i] Gömme işlemleri ChromaDB'ye ekleniyor...")
        self.db.add_vectors(ids=ids, documents=documents, embeddings=embeddings)
        print(f"[i] '{os.path.basename(pdf_path)}' başarıyla dizine eklendi.")
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
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
        if not pdf_files:
            print(f"[!] '{folder_path}' klasöründe PDF dosyası bulunamadı.")
            return 0
        
        print(f"[i] '{folder_path}' klasöründeki {len(pdf_files)} PDF dosyası dizine ekleniyor...")

        for file in pdf_files:
            pdf_path = os.path.join(folder_path, file)
            doc_name = os.path.splitext(file)[0] # "report1.pdf" → "report1"

            chunker = PDFChunker(pdf_path)
            chunks = chunker.chunk_pdf(word_limit=word_limit)
            chunker.close()
            print(f"[i] '{file}' dosyasından {len(chunks)} parça oluşturuldu.")

            embedded = self.embedder.embed_chunks(chunks)
            print(f"[i] '{file}' için {len(embedded)} parça gömüldü.")

            # Her belge için benzersiz ID'ler oluşturun
            # Mevcut ChromaDB'deki ID'lerle çakışmamak için belge adını öne eklemek iyi bir stratejidir.
            ids = [f"{doc_name}_chunk_{i}" for i in range(len(embedded))]
            docs = [item["text"] for item in embedded]
            vecs = [item["embedding"] for item in embedded]

            print(f"[i] '{file}' gömme işlemleri ChromaDB'ye ekleniyor...")
            self.db.add_vectors(ids=ids, documents=docs, embeddings=vecs)
            print(f"[i] '{file}' başarıyla dizine eklendi.")
            total_chunks += len(embedded)

        print(f"[i] Tüm PDF dosyalarından toplam {total_chunks} parça dizine eklendi.")
        return total_chunks

    def answer_question(self, question: str, top_k: int = 3) -> str:
        # Sorgu gömmesi için de toplu işlemden faydalanılabilir, ancak tek bir sorgu olduğu için
        # buradaki embed_chunks çağrısı zaten tek elemanlı bir liste ile çalışacaktır.
        print(f"[i] Sorgu '{question}' gömülüyor...")
        query_embedding = self.embedder.embed_chunks([question])[0]["embedding"]
        
        print(f"[i] Veritabanından en alakalı {top_k} parça aranıyor...")
        results = self.db.query_vectors(query_embedding, n_results=top_k)
        
        relevant_texts = results.get("documents", [])

        if relevant_texts and isinstance(relevant_texts[0], list):
            flat_texts = [t for sublist in relevant_texts for t in sublist]
        else:
            flat_texts = relevant_texts
        
        if not flat_texts:
            print("[!] İlgili metin parçaları bulunamadı. Cevap oluşturulamıyor.")
            return "Üzgünüm, sorunuzla ilgili yeterli bilgi bulamadım."

        print(f"[i] Bulunan {len(flat_texts)} ilgili metinle cevap oluşturuluyor.")
        answer = self.answer_generator.generate_answer_from_context(question, flat_texts)
        return answer 
    
    def chat(self, user_input: str) -> str:
        # Chat özelliği bağlamı kullanmadığı için direkt olarak GeminiAnswerGenerator'a yönlendirilir.
        print(f"[i] Chat oturumu üzerinden yanıt üretiliyor...")
        return self.answer_generator.chat(user_input)
