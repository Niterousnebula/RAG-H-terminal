from llama_cpp import Llama
from core.llm_rules import SYSTEM_RULES
import os
import sys
import time


def resource_path(relative_path):
    import sys
    import os

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    # 🔥 check _internal first
    internal_path = os.path.join(base_path, "_internal", relative_path)
    normal_path = os.path.join(base_path, relative_path)

    if os.path.exists(internal_path):
        return internal_path

    return normal_path


class LocalLLM:
    def __init__(self):
        self.models = {}

        self.model_paths = {
            "deepseek": resource_path("models/deepseek.gguf"),
            "qwen": resource_path("models/qwen-coder.gguf"),
            "mistral": resource_path("models/mistral.gguf")
        }

    # ---------------- LOAD MODEL ----------------

    def load_model(self, name):
        if name not in self.models:
            print(f"🧠 Loading model: {name}...")

            self.models[name] = Llama(
                model_path=self.model_paths[name],
                n_ctx=2048,
                n_threads=6,
                n_gpu_layers=0,
                n_batch=256,
                use_mmap=True,
                use_mlock=False
            )

            print(f"✅ Model loaded: {name}")

        return self.models[name]

    # ---------------- GENERATE ----------------

    def generate(self, model_name, prompt):
        model = self.load_model(model_name)

        print(f"\n⚡ [{model_name.upper()}] Generating...")

        start_time = time.time()

        prompt_len = len(prompt)

        # 🔥 ROLE + TOKEN LOGIC

        if model_name == "mistral":
            max_tokens = 128 if prompt_len < 300 else 256

            full_prompt = f"""
You are a human-like assistant.
Respond naturally and briefly.

User: {prompt}
Assistant:"""

        elif model_name == "qwen":
            max_tokens = 512 if prompt_len < 800 else 700

            role = "You output ONLY clean executable code."

            full_prompt = f"""
{SYSTEM_RULES}

{role}

User:
{prompt}

Assistant:
"""

        elif model_name == "deepseek":
            max_tokens = 128

            role = """
You are a strict controller.
Return ONLY JSON.
No explanations.
"""

            full_prompt = f"""
{SYSTEM_RULES}

{role}

User:
{prompt}

Assistant:
"""

        else:
            max_tokens = 256
            full_prompt = prompt

        # 🔥 ACTUAL MODEL CALL

        output = model(
            full_prompt,
            max_tokens=max_tokens,
            temperature=0.2,
            top_p=0.8,
            stop=["User:", "\nUser:"]
        )

        end_time = time.time()

        elapsed = end_time - start_time
        text = output["choices"][0]["text"].strip()

        token_count = len(text.split())
        tps = round(token_count / elapsed, 2) if elapsed > 0 else 0

        print(f"⏱️ [{model_name.upper()}] {round(elapsed,2)}s | ⚡ {tps} tok/s")

        return text
