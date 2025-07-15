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

# CHROMA Local Save
CHROMA_LOCAL = config.getboolean("BOOL", "CHROMA_LOCAL", fallback=True)

# Gemini API
API_KEY = config.get("API", "API_KEY")

# Gemini Models
GEMINI_EMBEDDER_MODEL = config.get("MODEL", "GEMINI_EMBEDDER_MODEL")
GEMINI_ANSWER_MODEL = config.get("MODEL", "GEMINI_ANSWER_MODEL")

# Project Member Num
MEMBER = config.getint("INT", "MEMBER")

# Source for Test 
PDF_FILE = config.get("FILE", "PDF_FILE")

# Folder 
SOURCE_FOLDER = Path(config.get("FOLDER", "SOURCE_FOLDER"))
OTHER_FOLDER = Path(config.get("FOLDER", "OTHER_FOLDER"))
CHROMA_FOLDER = Path(config.get("FOLDER", "CHROMA_FOLDER"))