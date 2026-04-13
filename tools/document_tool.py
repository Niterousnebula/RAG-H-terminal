import pdfplumber


class DocumentTool:
    def read_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF safely
        """
        text = ""

        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + " "
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

        # 🔥 HARD LIMIT (prevents crash)
        return text[:5000]