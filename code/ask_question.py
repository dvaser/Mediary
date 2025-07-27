from pipeline.rag_pipeline import RAGPipeline
from config import *
from utils.logger import log

log("Question-Answer System Started", type="banner")

# Initialize the RAG pipeline with your API key
pipeline = RAGPipeline(api_key=API_KEY)

# Inform the user about the mode of the system
if CHAT:
    log("System running in Chat mode (LLM + Contextual Memory).", type="info")
else:
    log("System running in RAG mode (Retrieve and Generate).", type="info")

try:
    # Continuous loop for user interaction
    while True:
        user_q = input("Ask a question (or 'exit' to quit): ")

        if user_q.lower() == "exit":
            log("User session ended by 'exit' command.", type="info")
            break

        log(f"User question: {user_q}", type="debug")

        # Use either chat mode or retrieval-augmented generation mode
        if CHAT:
            answer = pipeline.chat(user_q)
        else:
            answer = pipeline.answer_question(user_q)

        log(f"Generated answer: {answer}", type="debug")

        print(f"Answer:\n{answer}\n")

except Exception as e:
    log(f"Error occurred during Q&A session: {e}", type="error")
