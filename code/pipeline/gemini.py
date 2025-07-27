from utils.logger import log
import asyncio
import time
import random
import numpy as np
from typing import List, Dict, Any
from config import *
from google import generativeai as genai

class GeminiEmbedder:
    """
    GeminiEmbedder handles embedding text chunks using Google Gemini embedding models,
    with support for batching, rate limiting, retries, and both async and sync modes.
    """

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
        self.retry_delay = 1  # Initial retry delay for sync embedding

        self.buffer_active_time = BUFFER_ACTIVE_SECONDS
        self.buffer_rest_time = BUFFER_REST_SECONDS
        self.buffer_cycle_start = time.monotonic()

        # Limit batch size based on model capabilities
        if "gemini-embedding" in self.model_name.lower():
            self.api_max_batch_size = 1
        elif "text-embedding-004" in self.model_name.lower():
            self.api_max_batch_size = 250
        else:
            self.api_max_batch_size = 100

        if self.batch_size > self.api_max_batch_size:
            log(
                f"[!] batch_size {self.batch_size} > max allowed {self.api_max_batch_size} for model '{self.model_name}', limiting.",
                type="warning"
            )
            self.batch_size = self.api_max_batch_size
        
        if self.batch_size == 1 and self.max_concurrent_batches > 1:
            log(
                f"[!] When batch_size is 1, it is recommended to set max_concurrent_batches to 1 (currently {self.max_concurrent_batches}).",
                type="warning"
            )
            self.max_concurrent_batches = 1
        
        log("Gemini Embedder initialized", type="note")
        log(f"Model: {self.model_name}", type="note")
        log(f"Batch size: {self.batch_size}, Max concurrent: {self.max_concurrent_batches}", type="note")

    async def _embed_batch(self, batch: List[str], batch_index: int = 0) -> List[Dict[str, Any]]:
        """
        Embeds a batch of texts asynchronously with retry logic on rate limits and errors.

        Parameters:
        - batch: List of text strings to embed.
        - batch_index: Index of the batch (for logging).

        Returns:
        - List of dicts with keys 'text' and 'embedding' for each input.
        """
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

                # Normalize embeddings
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

                log(f"Batch {batch_index} embedding succeeded (attempt {attempt+1}).", type="success")
                return [{"text": t, "embedding": emb} for t, emb in zip(batch, embeddings_norm)]
            except Exception as e:
                msg = str(e)
                log(f"Batch {batch_index} (Attempt {attempt+1}/5) failed: {msg}", type="error")
                # Exponential backoff on rate limit errors
                if "429" in msg or "quota" in msg.lower():
                    retry_delay = min(retry_delay * 2, self.max_retry_delay)
                    wait = retry_delay + random.uniform(0.3, 1.0)
                    log(f"Rate limit hit, sleeping for {wait:.1f} seconds...", type="rate_limit")
                    await asyncio.sleep(wait)
                else:
                    log(f"Non-retryable error in batch {batch_index}, aborting: {msg}", type="critical")
                    break
        log(f"Batch {batch_index}: All attempts failed.", type="error")
        return []

    async def _embed_batches_async(self, batches: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Embeds multiple batches asynchronously with concurrency and buffering.

        Parameters:
        - batches: List of batches (list of text lists).

        Returns:
        - Flattened list of embedding dicts.
        """
        log("_embed_batches_async", type="func")
        semaphore = asyncio.Semaphore(self.max_concurrent_batches)
        success_counter = 0

        async def process_batch(batch_data, idx):
            nonlocal success_counter
            async with semaphore:
                now = time.monotonic()
                elapsed = now - self.buffer_cycle_start
                if elapsed > self.buffer_active_time:
                    log(f"Buffer active time ({self.buffer_active_time}s) reached. Resting for {self.buffer_rest_time}s...", type="performance")
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
        """
        Determines dynamic delay between batch requests based on success count.

        Parameters:
        - success_count: Number of successful batch embeddings so far.

        Returns:
        - Delay time in seconds.
        """
        log("_smart_delay", type="func")
        if success_count < 3:
            return random.uniform(1.0, 2.0)
        elif success_count < 10:
            return random.uniform(0.5, 1.0)
        else:
            return random.uniform(0.2, 0.5)

    def _embed_single_chunk_sync(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """
        Synchronously embed chunks one by one with retry and delay logic.

        Parameters:
        - chunks: List of text strings.

        Returns:
        - List of embedding dicts.
        """
        log("_embed_single_chunk_sync", type="func")
        results = []
        start_time = time.monotonic()
        retry_limit = 5

        for i, text in enumerate(chunks):
            retry_count = 0
            success = False

            while retry_count < retry_limit and not success:
                try:
                    time.sleep(self.retry_delay)

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
                    success = True
                except Exception as e:
                    log(f"Chunk {i} failed attempt {retry_count+1}: {e}", type="error")
                    if "429" in str(e):
                        self.retry_delay = min(self.retry_delay * 2, self.max_retry_delay)
                        log(f"Increased delay to: {self.retry_delay} seconds.", type="rate_limit")
                        retry_count += 1
                    else:
                        log(f"Non-retryable error on chunk {i}, stopping retries: {e}", type="critical")
                        break

            if not success:
                log(f"Chunk {i} embedding failed after {retry_limit} attempts, skipping.", type="error")

            elapsed = time.monotonic() - start_time
            if elapsed > self.buffer_active_time:
                log(f"Buffer active time ({self.buffer_active_time}s) reached, resting for {self.buffer_rest_time}s...", type="performance")
                time.sleep(self.buffer_rest_time)
                start_time = time.monotonic()

        return results

    def embed_chunks(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """
        Main method to embed a list of text chunks using either async batching or sync embedding.

        Parameters:
        - chunks: List of text chunks to embed.

        Returns:
        - List of embedding dicts with 'text' and 'embedding' keys.
        """
        log("embed_chunks", type="func")
        if not chunks:
            log("No text chunks provided for embedding.", type="note")
            return []

        if EMBEDDING_ASYNC:
            log(
                f"Embedding {len(chunks)} chunks asynchronously with batch size {self.batch_size} and max concurrency {self.max_concurrent_batches}.",
                type="performance"
            )
            batches = [chunks[i:i + self.batch_size] for i in range(0, len(chunks), self.batch_size)]
            return asyncio.run(self._embed_batches_async(batches))
        else:
            log(f"Embedding {len(chunks)} chunks synchronously with initial delay {self.retry_delay}.", type="performance")
            return self._embed_single_chunk_sync(chunks)


class GeminiAnswerGenerator:
    """
    GeminiAnswerGenerator uses Gemini's text generation model to answer questions based on context or chat input.
    """

    def __init__(self, api_key: str = None, model_name: str = GEMINI_ANSWER_MODEL):
        log("GeminiAnswerGenerator", type="header")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat_session = self.model.start_chat(history=[
            {"role": "user", "parts": "You are a helpful and kind Turkish assistant."},
            {"role": "model", "parts": "Merhaba! Size nasıl yardımcı olabilirim?"}
        ])
        log("GeminiAnswerGenerator initialized", type="note")

    def generate_answer_from_context(self, query: str, context_chunks: List[str]) -> str:
        """
        Generates an answer using the given context chunks.

        Parameters:
        - query: The question string.
        - context_chunks: List of relevant context strings.

        Returns:
        - Generated answer text.
        """
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
            log(f"Question processed: {query}", type="info")
            return response.text.strip()
        except Exception as e:
            log(f"Error generating answer: {e}", type="error")
            return "Sorry, an error occurred while generating the answer."

    def chat(self, user_input: str) -> str:
        """
        Continues a chat conversation with the user.

        Parameters:
        - user_input: The input message from the user.

        Returns:
        - Model-generated response text.
        """
        log("chat", type="func")
        try:
            response = self.chat_session.send_message(
                user_input,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 512
                }
            )
            log(f"User message received: {user_input}", type="info")
            return response.text.strip()
        except Exception as e:
            log(f"Error during chat: {e}", type="error")
            return "Sorry, an error occurred during chat."
