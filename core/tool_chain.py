class ToolChain:
    def __init__(self, doc_tool, executor, memory, llm):
        self.doc_tool = doc_tool
        self.executor = executor
        self.memory = memory
        self.llm = llm

    def run(self, steps, file_path=None):
        from utils.file_handler import chunk_text, clean_text

        data = None

        for step in steps:
            if not isinstance(step, dict):
                continue

            tool = step.get("tool")

            # -------- READ + STORE PDF --------
            if tool == "read_pdf" and file_path:
                try:
                    text = self.doc_tool.read_pdf(file_path)

                    text = clean_text(text)
                    chunks = chunk_text(text, chunk_size=500, overlap=100)

                    # 🔥 store chunks in vector DB
                    self.memory.add_chunks(chunks)

                    data = f"Document processed into {len(chunks)} chunks."

                except Exception as e:
                    return f"PDF error: {str(e)}"

            # -------- EXECUTE CODE --------
            elif tool == "execute_code" and data:
                try:
                    result = self.executor.execute(data)
                    data = result.get("stdout", "") or result.get("stderr", "")
                except Exception as e:
                    return f"Execution error: {str(e)}"

        return data or ""