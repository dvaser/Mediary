from pipeline.rag_pipeline import RAGPipeline
from config import *
from utils.logger import log

# Initialize the RAG pipeline with your API key (done once)
pipeline = RAGPipeline(api_key=API_KEY)

# Inform about the mode (done once at startup)
log("Question-Answer System Started", type="banner")
log(
    "System running in Chat mode (LLM + Contextual Memory)."
    if CHAT else
    "System running in RAG mode (Retrieve and Generate).",
    type="info"
)

def ask_question(user_q: str) -> str:
    """
    Handles a single user question and returns the generated answer.

    Parameters:
    - user_q (str): The user's question.

    Returns:
    - str: The generated answer.
    """
    try:
        user_q = user_q.strip()

        if not user_q:
            log("Empty question input, please enter a valid question.", type="warning")
            return "Please provide a valid question."

        log(f"User question: {user_q}", type="debug")

        if CHAT:
            answer = pipeline.chat(user_q)
        else:
            answer = pipeline.answer_question(user_q)

        log(f"Generated answer: {answer}", type="debug")
        return answer

    except Exception as e:
        log(f"Error occurred during Q&A: {e}", type="error")
        return "An error occurred while processing your question."
