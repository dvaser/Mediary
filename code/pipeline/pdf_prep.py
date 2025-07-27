import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize
from config import *
from utils.logger import log

def ensure_nltk_resources():
    for pkg in ["punkt", "stopwords"]:
        try:
            nltk.data.find(f"tokenizers/{pkg}")
        except LookupError:
            nltk.download(pkg)

ensure_nltk_resources()

class PDFChunker:
    """
    A utility class to load and chunk PDF files using different strategies:
    - heading-based chunking
    - sentence-safe word-limited chunking
    """

    def __init__(self, pdf_path: str):
        log("PDFChunker", type="header")  # Sınıf adı header log
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.heading_chunks = []
        log(f"PDFChunker başlatıldı: {pdf_path}", type="info")

    def chunk_pdf(self, word_limit: int = 500, heading_fontsize: float = 15.0) -> list[str]:
        log("chunk_pdf", type="func")
        log("PDF başlıklarına göre bölünmeye başlanıyor...", type="info")
        heading_sections = self.split_by_headings(min_heading_fontsize=heading_fontsize)
        log(f"Başlık bazlı bölüm sayısı: {len(heading_sections)}", type="info")

        final_chunks = []
        for section in heading_sections:
            word_chunks = self.split_by_word_limit(section, max_words=word_limit)
            final_chunks.extend(word_chunks)

        log(f"PDF'den toplam {len(final_chunks)} parça oluşturuldu.", type="success")
        return final_chunks

    def split_by_headings(self, min_heading_fontsize: float = 15.0) -> list[str]:
        log("split_by_headings", type="func")
        chunks = []
        current_chunk = ""

        for page in self.doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block['type'] == 0:  # text block
                    for line in block["lines"]:
                        fontsizes = [span["size"] for span in line["spans"]]
                        max_size = max(fontsizes) if fontsizes else 0
                        text_line = " ".join([span["text"] for span in line["spans"]]).strip()

                        if max_size >= min_heading_fontsize and len(text_line) > 3:
                            if current_chunk.strip():
                                chunks.append(current_chunk.strip())
                            current_chunk = text_line + "\n"
                        else:
                            current_chunk += text_line + "\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        self.heading_chunks = chunks
        log(f"PDF başlıklarına göre {len(chunks)} bölüm oluşturuldu.", type="info")
        return chunks

    def split_by_word_limit(self, text: str, max_words: int = 1000) -> list[str]:
        log("split_by_word_limit", type="func")
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        current_word_count = 0

        for sentence in sentences:
            sentence_word_count = len(sentence.split())
            if current_word_count + sentence_word_count <= max_words:
                current_chunk += sentence + " "
                current_word_count += sentence_word_count
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
                current_word_count = sentence_word_count

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        log(f"Kelime limiti bazlı bölmede {len(chunks)} parça oluşturuldu.", type="info")
        return chunks

    def close(self):
        log("close", type="func")
        if self.doc:
            self.doc.close()
            log("PDF dosyası kapatıldı.", type="info")
