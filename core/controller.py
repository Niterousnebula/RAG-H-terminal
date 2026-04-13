from core.state_manager import StateManager
from tools.document_tool import DocumentTool
from tools.executor import CodeExecutor
from core.local_llm import LocalLLM
from memory.vector_store import VectorStore
from core.tool_selector import ToolSelector
from core.json_guard import extract_json, validate_decision, repair_decision
from core.agent_manager import AgentManager
from core.tool_chain import ToolChain
import time


class Controller:
    def __init__(self):
        self.state = StateManager()
        self.doc_tool = DocumentTool()
        self.executor = CodeExecutor()
        self.llm = LocalLLM()
        self.memory = VectorStore()
        self.tool_selector = ToolSelector()

        self.agents = AgentManager(self.llm)

        self.tool_chain = ToolChain(
            self.doc_tool,
            self.executor,
            self.memory,
            self.llm
        )

    # ---------------- SMART MEMORY ----------------

    def retrieve_context(self, query):
        results = self.memory.search(query, k=5)

        if not results:
            return ""

        selected = []
        total_len = 0
        max_len = 500   # 🔥 strict budget

        for chunk in results:
            if total_len + len(chunk) > max_len:
                break

            selected.append(chunk)
            total_len += len(chunk)

        return "\n".join(selected)

    # ---------------- DECISION ----------------

    def decide(self, user_input):
        prompt = f"""
Return ONLY JSON:

{{
    "type": "chat | code | reasoning | tool_chain",
    "model": "mistral | qwen | deepseek",
    "tools": [{{"tool": "read_pdf"}}]
}}

User:
{user_input}
"""

        raw = self.llm.generate("deepseek", prompt)

        parsed = extract_json(raw)
        valid = validate_decision(parsed)

        if valid:
            return valid

        return repair_decision(user_input)

    # ---------------- CORE ----------------

    def process(self, user_input: str, file_path=None):

        clean = user_input.lower().strip()

        if clean in ["hi", "hello", "hey"]:
            return {"type": "text", "content": "Hello! How can I help you?"}

        if clean in ["how are you", "how are you?", "what's up", "whats up"]:
            return {"type": "text", "content": "I'm doing well! How about you?"}

        self.state.update("task", user_input)

        context = self.retrieve_context(user_input)
        enriched_input = f"{user_input}\n\nContext:\n{context}"

        decision = self.decide(enriched_input)

        return {
            "type": decision.get("type", "chat"),
            "model": decision.get("model", "mistral"),
            "prompt": enriched_input,
            "tools": decision.get("tools", [])
        }

    # ---------------- NON-STREAM (AUTO CONTINUE) ----------------
    
    def run(self, user_input: str, file_path=None):
        result = self.process(user_input, file_path)

        if result["type"] == "text":
            return f"[SYSTEM]\n{result['content']}"

        model_name = result["model"]
        prompt = result["prompt"]

        full_response = ""
        max_loops = 5   # 🔥 allow longer outputs

        for i in range(max_loops):

            response = self.llm.generate(model_name, prompt)
            full_response += response

            # 🔥 SMART STOP CONDITIONS

            # 1. Natural ending
            if full_response.strip().endswith((".", "}", "]", "```")):
                break

            # 2. Short response → likely finished
            if len(response.strip()) < 100:
                break

            # 🔥 FORCE CONTINUATION
            prompt = f"""
Continue EXACTLY from where you stopped.
DO NOT restart.
DO NOT repeat anything.

{full_response}
"""

        return f"[{model_name.upper()}]\n{full_response}"

    # ---------------- STREAM (CONTINUATION ENABLED) ----------------
    def run_stream(self, user_input: str, file_path=None):
        import time

        start_time = time.time()

        result = self.process(user_input, file_path)

        if result["type"] == "text":
            yield f"[SYSTEM]\n{result['content']}"
            return

        model_name = result["model"]
        prompt = result["prompt"]

        yield f"[{model_name.upper()}]\n"

        max_loops = 5
        full_output = ""
        token_count = 0

        model = self.llm.load_model(model_name)

        # 🔥 ADAPTIVE TOKENS (STREAM)
        if model_name == "qwen":
            max_tokens = 512
        elif model_name == "deepseek":
            max_tokens = 128
        else:
            max_tokens = 256

        for _ in range(max_loops):

            stream = model(
                prompt,
                max_tokens=max_tokens,
                stop=["User:", "\nUser:"],
                stream=True
            )

            partial = ""

            for chunk in stream:
                if "choices" not in chunk:
                    continue
                if "text" not in chunk["choices"][0]:
                    continue

                token = chunk["choices"][0]["text"]

                partial += token
                full_output += token
                token_count += 1

                yield token

            # 🔥 STOP CONDITIONS

            if full_output.strip().endswith(("}", "```", "]", ".")):
                break

            if len(partial.strip()) < 100:
                break

            # 🔥 CONTINUE
        prompt = f"""
Continue EXACTLY from where you stopped.
Do not repeat anything.

{full_output}
 """

        end_time = time.time()

        duration = end_time - start_time
        tps = round(token_count / duration, 2) if duration > 0 else 0

        print(f"⏱️ STREAM [{model_name.upper()}] {round(duration,2)}s | ⚡ {tps} tok/s")