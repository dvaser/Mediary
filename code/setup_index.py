
from pipeline.rag_pipeline import RAGPipeline
from config import *
from utils.logger import log
from pathlib import Path

try:
    log("Gemini RAG Sistemi", type="banner")
    pipeline = RAGPipeline(api_key=API_KEY)

    if TEST:
        log("Test modu aktif. PDF dosyası üzerinden indexleme yapılacak.", type="test")
        log(f"PDF: {PDF_FILE}", type="info")
        PDF_FILE_PATH = SOURCE_FOLDER / PDF_FILE
        n_chunks = pipeline.create_index(PDF_FILE_PATH)
        log(f"PDF dosyasından toplam {n_chunks} parça (chunk) oluşturuldu.", type="success")
    else:
        log("Test modu pasif.", type="test")
        log("Klasör üzerinden toplu indexleme başlıyor.", type="info")
        indexed = pipeline.create_index_from_folder(SOURCE_FOLDER)
        log(f"Toplam {indexed} chunk klasörden oluşturuldu.", type="success")

except Exception as e:
    log(f"Pipeline işlemi sırasında hata oluştu: {e}", type="error")
