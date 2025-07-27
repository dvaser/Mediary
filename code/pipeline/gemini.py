from utils.logger import log
import asyncio
import time
import random
import numpy as np
from typing import List, Dict, Any
from config import *
from google import generativeai as genai

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
        log("GeminiEmbedder", type="header")
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
        self.retry_delay = 1
        
        self.buffer_active_time = BUFFER_ACTIVE_SECONDS
        self.buffer_rest_time = BUFFER_REST_SECONDS
        self.buffer_cycle_start = time.monotonic()

        if "gemini-embedding" in self.model_name.lower():
            self.api_max_batch_size = 1
        elif "text-embedding-004" in self.model_name.lower():
            self.api_max_batch_size = 250
        else:
            self.api_max_batch_size = 100

        if self.batch_size > self.api_max_batch_size:
            log(f"[!] batch_size {self.batch_size} > max allowed {self.api_max_batch_size} for model '{self.model_name}', sınırlandı.", type="warning")
            self.batch_size = self.api_max_batch_size
        
        if self.batch_size == 1:
            if self.max_concurrent_batches > 1:
                log(f"[!] batch_size 1 iken max_concurrent_batches'ı {self.max_concurrent_batches} yerine 1 olarak sınırlama önerilir.", type="warning")
                self.max_concurrent_batches = 1
        
        log("Gemini Embedder başlatıldı", type="note")
        log(f"Model: {self.model_name}", type="note")
        log(f"Batch size: {self.batch_size}, Max concurrent: {self.max_concurrent_batches}", type="note")

    async def _embed_batch(self, batch: List[str], batch_index: int = 0) -> List[Dict[str, Any]]:
        log("_embed_batch", type="func")
        retry_delay = 1
        for attempt in range(5):
            try:
                if EMBEDDING_DELAY_TIME > 0:
                    await asyncio.sleep(EMBEDDING_DELAY_TIME)

                response = genai.embed_content(
                    model=self.model_name,
                    content=batch,
                    task_type=self.task_type,
                    output_dimensionality=self.output_dimensionality
                )
                embeddings_raw = response["embedding"]

                embeddings_norm = []
                for emb_values in embeddings_raw:
                    emb_array = np.array(emb_values)
                    norm = np.linalg.norm(emb_array)
                    if norm == 0:
                        log(f"Zero vector embedding for a chunk in batch {batch_index}.", type="warning")
                        norm_emb = emb_array
                    else:
                        norm_emb = emb_array / norm
                    embeddings_norm.append(norm_emb.tolist())

                log(f"Batch {batch_index} embedding başarılı (deneme {attempt+1}).", type="success")
                return [{"text": t, "embedding": emb} for t, emb in zip(batch, embeddings_norm)]
            except Exception as e:
                msg = str(e)
                log(f"Batch {batch_index} (Attempt {attempt+1}/5) failed: {msg}", type="error")
                if "429" in msg or "quota" in msg.lower():
                    retry_delay = min(retry_delay * 2, self.max_retry_delay)
                    wait = retry_delay + random.uniform(0.3, 1.0)
                    log(f"Rate limit geldi, {wait:.1f} saniye bekleniyor...", type="rate_limit")
                    await asyncio.sleep(wait)
                else:
                    log(f"Retry yapılamayan hata, batch {batch_index} iptal edildi: {msg}", type="critical")
                    break
        log(f"Batch {batch_index}: Tüm denemeler başarısız oldu.", type="error")
        return []

    async def _embed_batches_async(self, batches: List[List[str]]) -> List[Dict[str, Any]]:
        log("_embed_batches_async", type="func")
        semaphore = asyncio.Semaphore(self.max_concurrent_batches)
        success_counter = 0

        async def process_batch(batch_data, idx):
            nonlocal success_counter
            async with semaphore:
                now = time.monotonic()
                elapsed = now - self.buffer_cycle_start
                if elapsed > self.buffer_active_time:
                    log(f"Buffer aktif süresi ({self.buffer_active_time}s) doldu. {self.buffer_rest_time}s dinleniliyor...", type="performance")
                    await asyncio.sleep(self.buffer_rest_time)
                    self.buffer_cycle_start = time.monotonic()

                result = await self._embed_batch(batch_data, batch_index=idx)
                if result:
                    success_counter += 1
                await asyncio.sleep(self._smart_delay(success_counter))
                return result

        tasks = [asyncio.create_task(process_batch(batch, idx)) for idx, batch in enumerate(batches)]
        results = await asyncio.gather(*tasks)

        final_results = []
        for r in results:
            final_results.extend(r)
        return final_results

    def _smart_delay(self, success_count: int) -> float:
        log("_smart_delay", type="func")
        if success_count < 3:
            return random.uniform(1.0, 2.0)
        elif success_count < 10:
            return random.uniform(0.5, 1.0)
        else:
            return random.uniform(0.2, 0.5)

    def _embed_single_chunk_sync(self, chunks: List[str]) -> List[Dict[str, Any]]:
        log("_embed_single_chunk_sync", type="func")
        results = []
        for i, text in enumerate(chunks):
            time.sleep(self.retry_delay)
            try:
                response = genai.embed_content(
                    model=self.model_name,
                    content=text,
                    task_type=self.task_type,
                    output_dimensionality=self.output_dimensionality
                )
                emb_values = response["embedding"]
                emb_array = np.array(emb_values)
                norm = np.linalg.norm(emb_array)
                if norm == 0:
                    log(f"Zero vector embedding for chunk {i}.", type="warning")
                    norm_emb = emb_array
                else:
                    norm_emb = emb_array / norm

                results.append({"text": text, "embedding": norm_emb.tolist()})
                self.retry_delay = 1
            except Exception as e:
                log(f"Chunk {i} failed: {e}", type="error")
                if "429" in str(e):
                    self.retry_delay = min(self.retry_delay * 2, self.max_retry_delay)
                    log(f"Delay artırıldı: {self.retry_delay} saniye.", type="rate_limit")
                else:
                    log(f"Retry yapılamayan hata chunk {i}, işlem durduruldu: {e}", type="critical")
                    self.retry_delay = 1
                    break
        return results

    def embed_chunks(self, chunks: List[str]) -> List[Dict[str, Any]]:
        log("embed_chunks", type="func")
        if not chunks:
            log("Embed için metin yok.", type="note")
            return []

        if EMBEDDING_ASYNC:
            log(f"{len(chunks)} chunk async batch ile embed ediliyor. Batch size: {self.batch_size}, max concurrency: {self.max_concurrent_batches}", type="performance")
            batches = [chunks[i:i + self.batch_size] for i in range(0, len(chunks), self.batch_size)]
            return asyncio.run(self._embed_batches_async(batches))
        else:
            log(f"{len(chunks)} chunk sync tek tek embed ediliyor. Başlangıç gecikmesi: {self.retry_delay}", type="performance")
            return self._embed_single_chunk_sync(chunks)


class GeminiAnswerGenerator:
    def __init__(self, api_key: str = None, model_name: str = GEMINI_ANSWER_MODEL):
        log("GeminiAnswerGenerator", type="header")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat_session = self.model.start_chat(history=[
            {"role": "user", "parts": "You are a helpful and kind Turkish assistant."},
            {"role": "model", "parts": "Merhaba! Size nasıl yardımcı olabilirim?"}
        ])
        log("GeminiAnswerGenerator başlatıldı", type="note")

    def generate_answer_from_context(self, query: str, context_chunks: List[str]) -> str:
        log("generate_answer_from_context", type="func")
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
            log(f"Soru işlendi: {query}", type="info")
            return response.text.strip()
        except Exception as e:
            log(f"Yanıt oluşturulurken hata: {e}", type="error")
            return "Üzgünüm, bir hata oluştu."

    def chat(self, user_input: str) -> str:
        log("chat", type="func")
        try:
            response = self.chat_session.send_message(
                user_input,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 512
                }
            )
            log(f"Kullanıcı mesajı alındı: {user_input}", type="info")
            return response.text.strip()
        except Exception as e:
            log(f"Sohbet sırasında hata: {e}", type="error")
            return "Üzgünüm, bir hata oluştu."
