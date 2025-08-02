import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize
from ..config import *
from ..utils.logger import log

def ensure_nltk_resources():
    """
    Ensure necessary NLTK tokenizers and data are downloaded before usage.
    """
    for pkg in ["punkt", "stopwords"]:
        try:
            nltk.data.find(f"tokenizers/{pkg}")
        except LookupError:
            nltk.download(pkg)

# Make sure required NLTK resources are available
ensure_nltk_resources()

class PDFChunker:
    """
    A utility class for loading and chunking PDF documents.
    
    Supports:
    - Splitting text based on heading font size to get logical sections.
    - Further splitting sections into chunks with a maximum word count,
      respecting sentence boundaries.
    """

    def __init__(self, pdf_path: str):
        """
        Initialize the PDFChunker by loading the PDF document.

        Parameters:
        - pdf_path: Path to the PDF file.
        """
        log("PDFChunker", type="header")
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.heading_chunks = []
        log(f"PDFChunker initialized for: {pdf_path}", type="info")

    def chunk_pdf(self, word_limit: int = 500, heading_fontsize: float = 15.0) -> list[str]:
        """
        Creates chunks from the PDF by splitting first on headings,
        then splitting those sections into smaller chunks based on word limits.

        Parameters:
        - word_limit: Maximum number of words per chunk.
        - heading_fontsize: Minimum font size to consider text as a heading.

        Returns:
        - List of text chunks extracted from the PDF.
        """
        log("chunk_pdf", type="func")
        log("Starting to split PDF based on headings...", type="info")
        heading_sections = self.split_by_headings(min_heading_fontsize=heading_fontsize)
        log(f"Number of heading-based sections found: {len(heading_sections)}", type="info")

        final_chunks = []
        for section in heading_sections:
            word_chunks = self.split_by_word_limit(section, max_words=word_limit)
            final_chunks.extend(word_chunks)

        log(f"Total chunks created from PDF: {len(final_chunks)}", type="success")
        return final_chunks

    def split_by_headings(self, min_heading_fontsize: float = 15.0) -> list[str]:
        """
        Splits the PDF text into sections based on headings detected by font size.

        Parameters:
        - min_heading_fontsize: Font size threshold to identify headings.

        Returns:
        - List of text sections split at headings.
        """
        log("split_by_headings", type="func")
        chunks = []
        current_chunk = ""

        for page in self.doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block['type'] == 0:  # Only text blocks
                    for line in block["lines"]:
                        fontsizes = [span["size"] for span in line["spans"]]
                        max_size = max(fontsizes) if fontsizes else 0
                        text_line = " ".join([span["text"] for span in line["spans"]]).strip()

                        # If the line is a heading (font size above threshold and not empty)
                        if max_size >= min_heading_fontsize and len(text_line) > 3:
                            if current_chunk.strip():
                                chunks.append(current_chunk.strip())
                            current_chunk = text_line + "\n"
                        else:
                            current_chunk += text_line + "\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        self.heading_chunks = chunks
        log(f"Split into {len(chunks)} heading-based sections.", type="info")
        return chunks

    def split_by_word_limit(self, text: str, max_words: int = 1000) -> list[str]:
        """
        Splits a long text into smaller chunks each within the max_words limit,
        trying to keep sentence boundaries intact.

        Parameters:
        - text: The text to split.
        - max_words: Maximum words per chunk.

        Returns:
        - List of text chunks.
        """
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

        log(f"Created {len(chunks)} chunks based on word limit.", type="info")
        return chunks

    def close(self):
        """
        Closes the opened PDF document.
        """
        log("close", type="func")
        if self.doc:
            self.doc.close()
            log("PDF document closed.", type="info")
