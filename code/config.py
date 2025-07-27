from configparser import ConfigParser
from pathlib import Path

# Config Path
CONFIG_FILE_PATH = "./config.ini"

# Upload Config
config = ConfigParser()
config.read(CONFIG_FILE_PATH, encoding="utf-8")

# Test (True: Training with 1 source | False: Training with all source)
TEST = config.getboolean("BOOL", "TEST", fallback=True)

# Chat (True: If you want to chat with Gemini | False: Query trained data using the RAG model)
CHAT = config.getboolean("BOOL", "CHAT", fallback=True)

# CHROMA
CHROMA_LOCAL = config.getboolean("BOOL", "CHROMA_LOCAL", fallback=True)
CHROMA_COLLECTION_NAME = config.get("CHROMA", "COLLECTION_NAME", fallback="pdf_collection")

# Gemini API
API_KEY = config.get("API", "API_KEY")

# Gemini Models
GEMINI_EMBEDDER_MODEL = config.get("MODEL", "GEMINI_EMBEDDER_MODEL")
GEMINI_ANSWER_MODEL = config.get("MODEL", "GEMINI_ANSWER_MODEL")

# Gemini Embedded
EMBEDDING_BATCH_SIZE = config.getint("GEMINI", "EMBEDDING_BATCH_SIZE")
EMBEDDING_MAX_CONCURRENT = config.getint("GEMINI", "EMBEDDING_MAX_CONCURRENT")
EMBEDDING_MAX_RETRY_DELAY = config.getint("GEMINI", "EMBEDDING_MAX_RETRY_DELAY")
EMBEDDING_DELAY_TIME = config.getfloat("GEMINI", "EMBEDDING_DELAY_TIME")
# "RETRIEVAL_DOCUMENT", "SEMANTIC_SIMILARITY", "CLASSIFICATION" vs.
EMBEDDING_TASK_TYPE = config.get("GEMINI", "EMBEDDING_TASK_TYPE")
# Output Vector Size: 768, 1536 or 3072 (Usually 768)
EMBEDDING_OUTPUT_DIMENSIONALITY = config.getint("GEMINI", "EMBEDDING_OUTPUT_DIMENSIONALITY")
EMBEDDING_ASYNC = config.getboolean("GEMINI", "EMBEDDING_ASYNC", fallback=True)
# Buffer
BUFFER_ACTIVE_SECONDS = config.getint("BUFFER", "ACTIVE_SECONDS")
BUFFER_REST_SECONDS = config.getint("BUFFER", "REST_SECONDS")

# Source for Test 
PDF_FILE = config.get("FILE", "PDF_FILE")

# Folder 
SOURCE_FOLDER = Path(config.get("FOLDER", "SOURCE_FOLDER"))
OTHER_FOLDER = Path(config.get("FOLDER", "OTHER_FOLDER"))
CHROMA_FOLDER = Path(config.get("FOLDER", "CHROMA_FOLDER"))
LOG_FOLDER = Path(config.get("FOLDER", "LOG_FOLDER"))
FAILED_SOURCE_FOLDER = Path(config.get("FOLDER", "FAILED_SOURCE_FOLDER"))
PROCESSED_SOURCE_FOLDER = Path(config.get("FOLDER", "PROCESSED_SOURCE_FOLDER"))