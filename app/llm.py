import logging
import os
from typing import List

from .config import OPENAI_API_KEY, LLM_MODEL_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMClient:
    """
    LLM handler with multi-provider fallback.

    Priority order:
    1️⃣ OpenAI
    2️⃣ Mistral API
    3️⃣ Local HuggingFace model
    """

    def __init__(self):

        self.provider = None
        self.client = None
        self.local_model = None
        self.tokenizer = None

        mistral_key = os.getenv("MISTRAL_API_KEY")

        # --------------------------------------------------
        # 1️⃣ OpenAI Provider
        # --------------------------------------------------

        if OPENAI_API_KEY:
            try:
                from openai import OpenAI

                self.client = OpenAI(api_key=OPENAI_API_KEY)
                self.provider = "openai"

                logger.info("Using OpenAI provider.")
                return

            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")

        # --------------------------------------------------
        # 2️⃣ Mistral Provider
        # --------------------------------------------------

        if mistral_key:
            try:
                from mistralai.client import MistralClient

                self.client = MistralClient(api_key=mistral_key)
                self.provider = "mistral"

                logger.info("Using Mistral API provider.")
                return

            except Exception as e:
                logger.warning(f"Mistral initialization failed: {e}")

        # --------------------------------------------------
        # 3️⃣ Local Model Fallback
        # --------------------------------------------------

        try:
            logger.info("Falling back to local TinyLlama model.")

            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)

            # ensure pad token exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            device = "cuda" if torch.cuda.is_available() else "cpu"

            self.local_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            ).to(device)

            self.provider = "local"

            logger.info(f"Local TinyLlama loaded successfully on {device}.")

        except Exception as e:
            logger.error("Failed to load any LLM provider.")
            raise RuntimeError(f"No LLM available: {e}")

    # --------------------------------------------------

    def generate_answer(self, question: str, context_documents: List[str]) -> str:
        """
        Generate answer using retrieved context documents.
        """

        # ------------------------------
        # Validation
        # ------------------------------

        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must be a non-empty string.")

        if not context_documents:
            raise ValueError("Context documents cannot be empty.")

        context = "\n\n".join(context_documents)

        prompt = f"""
You are an AI bookkeeping assistant for a platform called Hellobooks.

Use the provided context to answer the user's question clearly and accurately.
If the answer is not found in the context, say you do not have enough information.

Context:
{context}

Question:
{question}

Answer:
"""

        # --------------------------------------------------
        # OpenAI
        # --------------------------------------------------

        if self.provider == "openai":

            try:

                response = self.client.chat.completions.create(
                    model=LLM_MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are a helpful accounting assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )

                answer = response.choices[0].message.content.strip()

                if not answer:
                    raise ValueError("LLM returned an empty response.")

                return answer

            except Exception as e:
                logger.error(f"OpenAI generation failed: {e}")
                raise RuntimeError(f"OpenAI generation failed: {e}")

        # --------------------------------------------------
        # Mistral API
        # --------------------------------------------------

        if self.provider == "mistral":

            try:

                response = self.client.chat(
                    model="mistral-medium",
                    messages=[{"role": "user", "content": prompt}]
                )

                answer = response.choices[0].message.content.strip()

                if not answer:
                    raise ValueError("Mistral returned an empty response.")

                return answer

            except Exception as e:
                logger.error(f"Mistral generation failed: {e}")
                raise RuntimeError(f"Mistral generation failed: {e}")

        # --------------------------------------------------
        # Local Model
        # --------------------------------------------------

        if self.provider == "local":

            try:

                inputs = self.tokenizer(prompt, return_tensors="pt")

                # move tensors safely to model device
                inputs = {k: v.to(self.local_model.device) for k, v in inputs.items()}

                outputs = self.local_model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.3,
                    pad_token_id=self.tokenizer.eos_token_id
                )

                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

                if "Answer:" in response:
                    return response.split("Answer:")[-1].strip()

                return response.strip()

            except Exception as e:
                logger.warning(f"OpenAI failed, switching to fallback provider: {e}")

                if os.getenv("MISTRAL_API_KEY"):
                    self.provider = "mistral"
                    return self.generate_answer(question, context_documents)

                raise RuntimeError(f"OpenAI generation failed: {e}")

        # --------------------------------------------------

        raise RuntimeError("No LLM provider available.")