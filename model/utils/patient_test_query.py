from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from .logger import log

load_dotenv()

class MedicalQueryProcessor:
    """
    Handles the retrieval and analysis of medical test-related queries
    using vector search and generative AI.
    """

    def __init__(self, db_path: str = "./chromaDB_medical_v2"):
        """
        Initialize the query processor with the embedding model, vector store, and LLM.

        Args:
            db_path (str): Path to the Chroma vector database directory.
        """
        log("Initializing MedicalQueryProcessor", type="info")
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectordb = Chroma(
            embedding_function=self.embeddings,
            persist_directory=db_path
        )
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
        self.retriever = self.vectordb.as_retriever(search_kwargs={"k": 15})
        self.prompt = self._get_prompt()
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            chain_type_kwargs={"prompt": self.prompt}
        )
        log("MedicalQueryProcessor Initialized", type="success")

    def _get_prompt(self):
        """
        Returns a medical-specific prompt template.
        """
        return PromptTemplate(
            template="""You are an expert medical lab doctor. Use the information below to explain the results clearly and accurately.

📋 Test Info:
{context}

❓ Patient Question: {question}

📝 Response Format:
1. 🎯 MAIN ASSESSMENT: Overall interpretation of the results
2. 📊 NORMAL RANGES: Normal values for the tests
3. ⚠️ ABNORMALITIES: Possible causes if abnormal
4. 🏥 CLINICAL SIGNIFICANCE: Importance in medical context
5. 💡 SUGGESTIONS: Recommendations (consult a doctor, follow-up tests)

⚠️ IMPORTANT:
- Do not make a definitive diagnosis
- Always recommend seeing a doctor
- Use simple, non-alarming language

Answer:""",
            input_variables=["context", "question"]
        )

    def process_query(self, query: str) -> dict:
        """
        Process a medical query by retrieving relevant documents and generating an AI response.

        Args:
            query (str): The medical question to be processed.

        Returns:
            dict: Contains success status, relevant documents, AI response, and error (if any).
        """
        log("Processing query", type="func")
        try:
            relevant_docs = self.retriever.invoke(query)
            result = self.qa_chain.invoke(query)
            return {
                "success": True,
                "relevant_docs": relevant_docs,
                "ai_response": result["result"],
                "error": None
            }
        except Exception as e:
            log(f"Query processing error: {str(e)}", type="error")
            return {
                "success": False,
                "relevant_docs": None,
                "ai_response": None,
                "error": str(e)
            }

    def get_answer(self, query: str) -> str:
        """
        Wrapper to return only the AI response or error message.

        Args:
            query (str): The user input question.

        Returns:
            str: AI-generated medical response or error message.
        """
        result = self.process_query(query)
        if result["success"]:
            return result["ai_response"]
        return f"Error: {result['error']}"

# Singleton processor instance
processor = MedicalQueryProcessor()

def get_answer(query: str) -> str:
    """
    Module-level helper function to get a medical answer directly.

    Args:
        query (str): The user input question.

    Returns:
        str: AI-generated medical response or error message.
    """
    return processor.get_answer(query)

if __name__ == "__main__":
    log("MedicalQueryProcessor module loaded.", type="banner")
