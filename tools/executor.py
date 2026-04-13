import subprocess
import tempfile


class CodeExecutor:
    def execute(self, code: str):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
                f.write(code.encode())
                file_path = f.name

            result = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True
            )

            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e)
            }