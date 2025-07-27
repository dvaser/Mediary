from pipeline.rag_pipeline import RAGPipeline
from config import *
from utils.logger import log

log("Soru-Cevap Sistemi Başlatıldı", type="banner")

pipeline = RAGPipeline(api_key=API_KEY)

if CHAT:
    log("Sistem Chat (LLM + Contextual Memory) modunda çalışıyor.", type="info")
else:
    log("Sistem RAG (Retrieve and Generate) modunda çalışıyor.", type="info")

try:
    while True:
        user_q = input("Ask a question (or 'exit' to quit): ")

        if user_q.lower() == "exit":
            log("Kullanıcı oturumu 'exit' ile sonlandırdı.", type="info")
            break

        log(f"Kullanıcı sorusu: {user_q}", type="debug")

        if CHAT:
            answer = pipeline.chat(user_q)
        else:
            answer = pipeline.answer_question(user_q)

        log(f"Oluşturulan cevap: {answer}", type="debug")

        print(f"Answer:\n{answer}\n")

except Exception as e:
    log(f"Soru-cevap oturumu sırasında hata oluştu: {e}", type="error")
