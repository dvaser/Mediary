from pipeline.rag_pipeline import RAGPipeline
from config import *

pipeline = RAGPipeline(api_key=API_KEY)

while True:
    user_q = input("Ask a question (or 'exit' to quit): ")
    if user_q.lower() == "exit":
        break
    if CHAT:
        answer = pipeline.chat(user_q)
    else:
        answer = pipeline.answer_question(user_q)
    print(f"Answer:\n{answer}\n")



