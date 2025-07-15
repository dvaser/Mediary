from google import generativeai as genai
from google.generativeai import types
from config import * # Make sure config.py is in the same directory or accessible via PYTHONPATH
import time

class GeminiEmbedder:
    def __init__(self, api_key: str = None, model_name: str = GEMINI_EMBEDDER_MODEL):
        if api_key:
            genai.configure(api_key=api_key)
        self.model_name = model_name
        self.retry_delay = 1 # BAŞLANGIÇ GECİKME SÜRESİ EKLENDİ

    def embed_chunks(self, chunks: list[str]) -> list[dict]:
        results = []
        for i, text in enumerate(chunks):
            # Her bir parça için döngüyü yeniden başlatmadan önce bir gecikme ekleyin
            time.sleep(self.retry_delay) # HER İSTEK ARASINDA GECİKME UYGULANIR

            try:
                response = genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type="retrieval_document"
                )
                embedding = response["embedding"]
                results.append({"text": text, "embedding": embedding})
                # Başarılı olursa gecikmeyi sıfırlayabilirsiniz veya kademeli olarak azaltabilirsiniz (isteğe bağlı)
                self.retry_delay = 1 # BAŞARILI İSTEK SONRASI GECİKMEYİ SIFIRLAMA
            except Exception as e:
                print(f"[!] Embedding failed for chunk {i}: {e}")
                if "429 Resource has been exhausted" in str(e):
                    # 429 hatası durumunda gecikmeyi artırın (ÜSTEL GERİ ÇEKİLME)
                    print(f"    Increasing delay to {self.retry_delay * 2} seconds due to quota exhaustion.")
                    self.retry_delay *= 2
                else:
                    self.retry_delay = 1
        return results

class GeminiAnswerGenerator:
    def __init__(self, api_key: str = None, model_name: str = GEMINI_ANSWER_MODEL):
        """
        Initializes the GeminiAnswerGenerator for generating answers based on context.

        Args:
            api_key (str): Your Gemini API key. If None, it expects genai.configure() to be called globally.
            model_name (str): The name of the generative model to use (e.g., 'models/gemini-pro').
        """
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        # Initialize chat history. This will be used for multi-turn conversations.
        self.chat_session = self.model.start_chat(history=[
            {"role": "user", "parts": "You are a helpful and kind Turkish assistant."},
            {"role": "model", "parts": "Merhaba! Size nasıl yardımcı olabilirim?"} # Initial greeting from the model
        ])

    def generate_answer_from_context(self, query: str, context_chunks: list[str]) -> str:
        """
        Generates an answer to a query using provided context chunks.
        This method is for single-turn question answering with explicit context.

        Args:
            query (str): The user's question.
            context_chunks (list[str]): A list of relevant text chunks from which to draw the answer.

        Returns:
            str: The generated answer.
        """
        context = "\n\n".join(context_chunks)
        prompt = (
            f"Aşağıdaki bağlamı kullanarak soruyu yanıtla:\n\n"
            # f"Sen, yalnızca aşağıda sağlanan bağlamı kullanarak soruları yanıtlayan bir tıbbi uzmansın.Cevabını oluştururken bu bağlamın dışına çıkma.Eğer cevap aşağıdaki bağlamda yer almıyorsa, kesin bir dille 'Bu bilgi belgede bulunmamaktadır.' de. Cevaplarını oluştururken, hangi kaynaktan (sayfa numarası) yararlandığını belirt.Cevaplarını açık, anlaşılır ve tıbbi terminolojiyi uygun şekilde kullanarak ver.:\n\n"
            f"Bağlam:\n{context}\n\n"
            f"Soru:\n{query}\n\n"
            f"Cevap:"
        )
        
        try:
            # Use generate_content for a direct prompt without relying on chat history for this specific call
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 512
                }
            )
            answer = response.text.strip()
        except Exception as e:
            print(f"[!] Error generating answer: {e}")
            answer = "Üzgünüm, bir hata oluştu."
        return answer

    def chat(self, user_input: str) -> str:
        """
        Continues the multi-turn conversation with the model.
        The model automatically manages the chat history.

        Args:
            user_input (str): The user's input message.

        Returns:
            str: The model's response.
        """
        try:
            response = self.chat_session.send_message(
                user_input,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 512
                }
            )
            answer = response.text.strip()
        except Exception as e:
            print(f"[!] Error during chat: {e}")
            answer = "Üzgünüm, bir hata oluştu."
        return answer