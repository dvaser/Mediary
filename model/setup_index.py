from pipeline.rag_pipeline import RAGPipeline
from .config import *
from .utils.logger import log
from pathlib import Path
import shutil
import uuid

def move_pdf(source_path: Path, destination_folder: Path):
    """
    Move a processed or failed PDF to the specified folder.
    """
    destination_folder.mkdir(parents=True, exist_ok=True)
    destination_path = destination_folder / source_path.name
    shutil.move(str(source_path), str(destination_path))
    log(f"'{source_path.name}' moved to '{destination_folder.name}' folder.", type="info")

def main():
    log("Gemini RAG System Initialized", type="banner")

    if CLEAR_COLLECTION:
        log("Clearing Chroma collection (CLEAR_COLLECTION = true)...", type="warning")
        shutil.rmtree(CHROMA_FOLDER, ignore_errors=True)

    pipeline = RAGPipeline(api_key=API_KEY)

    source_folder = SOURCE_FOLDER
    processed_folder = PROCESSED_SOURCE_FOLDER
    failed_folder = FAILED_SOURCE_FOLDER

    pdf_files = list(source_folder.glob("*.pdf"))
    if not pdf_files:
        log("No PDFs found to process.", type="warning")
        return

    for pdf_path in pdf_files:
        try:
            doc_uuid = uuid.uuid4().hex
            log(f"Processing PDF: {pdf_path.name} (UUID: {doc_uuid})", type="info")

            n_chunks = pipeline.create_index(
                pdf_path=pdf_path,
                custom_prefix=doc_uuid
            )
            move_pdf(pdf_path, processed_folder)
            log(f"{pdf_path.name} successfully processed. {n_chunks} chunks created.", type="success")
        except Exception as e:
            log(f"Error occurred, moving file to failed folder: {e}", type="error")
            move_pdf(pdf_path, failed_folder)

if __name__ == "__main__":
    main()
