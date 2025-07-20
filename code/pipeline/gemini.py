from google import generativeai as genai
from google.genai import types
import asyncio
import time
import random
import numpy as np
from typing import List, Dict, Any
from config import *

class GeminiEmbedder:
    def __init__(
        self,
        api_key: str = None,
        model_name: str = GEMINI_EMBEDDER_MODEL,
        batch_size: int = EMBEDDING_BATCH_SIZE,
        max_concurrent_batches: int = EMBEDDING_MAX_CONCURRENT,
        max_retry_delay: int = EMBEDDING_MAX_RETRY_DELAY,
        output_dimensionality: int = EMBEDDING_OUTPUT_DIMENSIONALITY,
        task_type: str = EMBEDDING_TASK_TYPE
    ):
        if api_key:
            genai.configure(api_key=api_key)

        self.model_name = model_name
        self.output_dimensionality = output_dimensionality
        self.task_type = task_type
        self.initial_batch_size = batch_size
        self.initial_max_concurrent_batches = max_concurrent_batches
        
        self.batch_size = batch_size
        self.max_concurrent_batches = max_concurrent_batches
        self.max_retry_delay = max_retry_delay
        self.retry_delay = 1  # Initial retry delay for sync mode

        # Model-specific max batch size control
        if "gemini-embedding" in self.model_name.lower():
            self.api_max_batch_size = 1  # Gemini embedding modelleri tek giriş destekler
        elif "text-embedding-004" in self.model_name.lower(): # Örneğin text-embedding-004
            self.api_max_batch_size = 250
        else:
            self.api_max_batch_size = 100 # Diğer veya bilinmeyen modeller için varsayılan

        if self.batch_size > self.api_max_batch_size:
            print(f"[!] batch_size {self.batch_size} > max allowed {self.api_max_batch_size} for model '{self.model_name}', sınırlandı.")
            self.batch_size = self.api_max_batch_size
        
        # Eğer batch_size 1 ise, concurrent batch sayısını da 1'e sabitlemek daha mantıklı olabilir
        # Çünkü her bir batch zaten tek bir chunk içerir.
        if self.batch_size == 1:
            if self.max_concurrent_batches > 1:
                 print(f"[!] batch_size 1 iken max_concurrent_batches'ı {self.max_concurrent_batches} yerine 1 olarak sınırlama önerilir.")
                 self.max_concurrent_batches = 1 # Başlangıçta en temkinli değeri ayarla


    async def _embed_batch(self, batch: List[str], batch_index: int = 0) -> List[Dict[str, Any]]:
        """
        Asynchronously embed a batch of texts with retries and exponential backoff.
        """
        retry_delay = 1
        for attempt in range(5):
            try:
                # EMBEDDING_DELAY_TIME config'de 0 olarak ayarlandığında bu kısım çalışmayacak
                if EMBEDDING_DELAY_TIME > 0:
                    await asyncio.sleep(EMBEDDING_DELAY_TIME)

                response = genai.embed_content(
                    model=self.model_name,
                    content=batch,
                    task_type=self.task_type,
                    output_dimensionality=self.output_dimensionality # Correct way to pass output_dimensionality
                )
                embeddings_raw = response["embedding"]

                embeddings_norm = []
                for emb_values in embeddings_raw:
                    emb_array = np.array(emb_values)
                    norm = np.linalg.norm(emb_array)
                    if norm == 0:
                        # Handle the rare case of a zero vector to prevent ZeroDivisionError
                        norm_emb = emb_array
                        print(f"[!] Warning: Zero vector embedding for a chunk in batch {batch_index}.")
                    else:
                        norm_emb = emb_array / norm
                    embeddings_norm.append(norm_emb.tolist())

                return [{"text": t, "embedding": emb} for t, emb in zip(batch, embeddings_norm)]
            except Exception as e:
                msg = str(e)
                print(f"[!] Batch {batch_index} (Attempt {attempt+1}/5) failed: {msg}")
                if "429" in msg or "quota" in msg.lower():
                    retry_delay = min(retry_delay * 2, self.max_retry_delay)
                    wait = retry_delay + random.uniform(0.3, 1.0)
                    print(f"    Waiting {wait:.1f} seconds before retry...")
                    await asyncio.sleep(wait)
                else:
                    print(f"    Non-retryable error for batch {batch_index}, aborting batch. Error: {msg}")
                    break
        print(f"[!] Batch {batch_index}: Permanently failed after all retries.")
        return []

    async def _embed_batches_async(self, batches: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Embed multiple batches asynchronously with concurrency control and adaptive delay.
        """
        semaphore = asyncio.Semaphore(self.max_concurrent_batches)
        success_counter = 0

        async def process_batch(batch_data, idx):
            nonlocal success_counter
            async with semaphore:
                result = await self._embed_batch(batch_data, batch_index=idx)
                if result:
                    success_counter += 1
                
                # Dinamik gecikme, sadece başarılı istekten sonra
                # Eğer hatalıysa ve retry_delay zaten bekleme sağladıysa burada tekrar beklemeye gerek kalmaz.
                # Ancak batchler arası hız ayarlamasını sağlamak için başarılı olsa da olmasa da
                # bir bekleme eklemek API'yi boğmamak adına önemlidir.
                # Bu yüzden her batch işlemi (başarılı ya da başarısız ilk deneme sonrası) sonrası bir delay olmalı.
                await asyncio.sleep(self._smart_delay(success_counter))
                return result

        tasks = [asyncio.create_task(process_batch(batch, idx)) for idx, batch in enumerate(batches)]
        results = await asyncio.gather(*tasks)

        final_results = []
        for r in results:
            final_results.extend(r)
        return final_results

    def _smart_delay(self, success_count: int) -> float:
        """
        Adaptive delay based on successful batch count to optimize rate limits.
        Adjust these values based on actual API performance and quota.
        """
        # Başlangıçta daha uzun bekle, sonra yavaşça düşür
        if success_count < 3:
            return random.uniform(1.0, 2.0) # 1.0 - 2.0 saniye
        elif success_count < 10:
            return random.uniform(0.5, 1.0) # 0.5 - 1.0 saniye
        else:
            return random.uniform(0.2, 0.5) # 0.2 - 0.5 saniye

    def _embed_single_chunk_sync(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """
        Synchronously embed a list of text chunks one by one with retry delays.
        """
        results = []
        for i, text in enumerate(chunks):
            time.sleep(self.retry_delay)
            try:
                response = genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type=self.task_type,
                    output_dimensionality=self.output_dimensionality # Correct way to pass output_dimensionality
                )
                emb_values = response["embedding"]
                emb_array = np.array(emb_values)
                norm = np.linalg.norm(emb_array)
                if norm == 0:
                    norm_emb = emb_array
                    print(f"[!] Warning: Zero vector embedding for chunk {i}.")
                else:
                    norm_emb = emb_array / norm

                results.append({"text": text, "embedding": norm_emb.tolist()})
                self.retry_delay = 1
            except Exception as e:
                print(f"[!] Chunk {i} failed: {e}")
                if "429" in str(e):
                    self.retry_delay = min(self.retry_delay * 2, self.max_retry_delay)
                    print(f"    Increased delay to {self.retry_delay} seconds.")
                else:
                    print(f"    Non-retryable error for chunk {i}, aborting. Error: {e}")
                    self.retry_delay = 1 # Non-retryable error, reset delay
                    break # Stop processing further chunks if a non-retryable error occurs
        return results

    def embed_chunks(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """
        Main entry point to embed a list of text chunks synchronously or asynchronously.
        """
        if not chunks:
            print("[i] No texts to embed.")
            return []

        if EMBEDDING_ASYNC:
            print(f"[i] Embedding {len(chunks)} chunks asynchronously with batch size {self.batch_size} and max concurrent batches {self.max_concurrent_batches}.")
            batches = [chunks[i:i + self.batch_size] for i in range(0, len(chunks), self.batch_size)]
            return asyncio.run(self._embed_batches_async(batches))
        else:
            print(f"[i] Embedding {len(chunks)} chunks synchronously one-by-one with initial delay {self.retry_delay}.")
            return self._embed_single_chunk_sync(chunks)

class GeminiAnswerGenerator:
    # ... (Aynı kalabilir)
    def __init__(self, api_key: str = None, model_name: str = GEMINI_ANSWER_MODEL):
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat_session = self.model.start_chat(history=[
            {"role": "user", "parts": "You are a helpful and kind Turkish assistant."},
            {"role": "model", "parts": "Merhaba! Size nasıl yardımcı olabilirim?"}
        ])

    def generate_answer_from_context(self, query: str, context_chunks: List[str]) -> str:
        context = "\n\n".join(context_chunks)
        prompt = (
            f"Using the following context, answer the question:\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{query}\n\n"
            f"Answer:"
        )
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 512
                }
            )
            return response.text.strip()
        except Exception as e:
            print(f"[!] Error generating answer: {e}")
            return "Sorry, an error occurred."

    def chat(self, user_input: str) -> str:
        try:
            response = self.chat_session.send_message(
                user_input,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 512
                }
            )
            return response.text.strip()
        except Exception as e:
            print(f"[!] Error during chat: {e}")
            return "Sorry, an error occurred."




