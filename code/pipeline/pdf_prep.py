import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize import TextTilingTokenizer
from config import *

def ensure_nltk_resources():
    for pkg in ["punkt", "stopwords", "punkt_tab"]:
        try:
            nltk.data.find(f"tokenizers/{pkg}")
        except LookupError:
            nltk.download(pkg)

ensure_nltk_resources()

class PDFChunker:
    """
    A utility class to load and chunk PDF files using different strategies:
    - heading-based chunking
    - word-limited chunking
    - topic segmentation
    """

    def __init__(self, pdf_path: str):
        """
        Initialize the chunker with a PDF file.

        Params:
        - pdf_path (str): Path to the PDF file.
        """
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.heading_chunks = []

    def chunk_pdf(self, word_limit: int = 500, heading_fontsize: float = 15.0) -> list[str]:
        """
        Full pipeline: Headings → NLP Topics → Word-limited chunks

        Params:
        - word_limit (int): Max words per final chunk
        - heading_fontsize (float): Font size threshold for headings

        Returns:
        - List[str]: All final processed chunks
        """
        final_chunks = []
        heading_sections = self.split_by_headings(min_heading_fontsize=heading_fontsize)

        for section in heading_sections:
            topic_chunks = self.split_by_topic_segments(section)
            for topic in topic_chunks:
                word_chunks = self.split_by_word_limit(topic, max_words=word_limit)
                final_chunks.extend(word_chunks)

        print(f"[PDFChunker] Generated {len(final_chunks)} chunks from PDF.")
        return final_chunks

    def split_by_headings(self, min_heading_fontsize: float = 15.0) -> list[str]:
        """
        Split PDF into sections based on large font-size headings.

        Params:
        - min_heading_fontsize (float): Font size threshold to treat a line as a heading.

        Returns:
        - List of text chunks (each section of the PDF).
        """
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
        return chunks

    def split_by_word_limit(self, text: str, max_words: int = 1000) -> list[str]:
        """
        Split a block of text into chunks, respecting sentence boundaries
        and limiting each chunk to approximately max_words.

        Params:
        - text (str): The input text to split.
        - max_words (int): Max words allowed per chunk.

        Returns:
        - List[str]: Sentence-safe chunks under the word limit.
        """
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

        return chunks

    def split_by_topic_segments(self, text: str) -> list[str]:
        """
        Use NLTK's TextTiling algorithm to segment a block of text into topic-based chunks.

        Params:
        - text (str): Input text to segment.

        Returns:
        - List[str]: Topic-based text segments.
        """
        try:
            tokenizer = TextTilingTokenizer()
            return tokenizer.tokenize(text)
        except Exception as e:
            print(f"[!] TextTiling failed: {e}")
            return [text]  # fallback to single chunk if tiling fails

    def close(self):
        if self.doc:
            self.doc.close()



