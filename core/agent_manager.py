from concurrent.futures import ThreadPoolExecutor


class AgentManager:
    def __init__(self, llm):
        self.llm = llm

    def run_parallel(self, user_input):
        """
        Runs coder + critic in parallel
        """

        def coder():
            return self.llm.generate("qwen", user_input)

        def critic(code_output):
            prompt = f"""
Review and improve the following code:

{code_output}

Return improved version ONLY.
"""
            return self.llm.generate("deepseek", prompt)

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_code = executor.submit(coder)

            code_output = future_code.result()

            future_critic = executor.submit(critic, code_output)

            critic_output = future_critic.result()

        return {
            "code": code_output,
            "improved": critic_output
        }