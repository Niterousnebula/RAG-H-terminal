# RAG-H Terminal

RAG-H Terminal is a minimal, high-performance local AI coding assistant built around a single GGUF model using llama-cpp-python. It is designed to be fast, simple, and practical, avoiding unnecessary architectural complexity while providing a clean streaming interface for real-time interaction.

---

## Features

- Single-file style backend design  
- Local GGUF model support (Qwen, Mistral, etc.)  
- Streaming responses (token-by-token output and Tps)  
- File upload support  
- OCR support for images  
- Automatic continuation for long outputs  
- Large context support (up to 16K depending on hardware)  
- Modular structure for future multi-tool orchestration  

---

## Project Structure


api/
core/
interfaces/
memory/
tools/
utils/

launcher.py
requirements.txt
README.md
.gitignore


---

## Setup

### 1. Clone the repository


git clone https://github.com/Niterousnebula/RAG-H-terminal.git

cd RAG-H-terminal


---

### 2. Install dependencies


pip install -r requirements.txt


---

### 3. Download a model

Models are not included due to size constraints.

Recommended model:


Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf


Place the model in the root directory and rename it:


model.gguf


---

### 4. Optional: Install OCR

Install Tesseract OCR and add it to your system PATH.

---

### 5. Run the application


python launcher.py


Then open:


http://127.0.0.1:5000


---

## Recommended Models

- Qwen2.5 Coder 7B — best balance of speed and quality  
- Qwen 14B — higher quality, slower  
- DeepSeek Coder 6.7B — lightweight alternative  

---

## Architecture


Frontend (interfaces)
↓
Backend (FastAPI)
↓
llama.cpp (GGUF model)


---

## Design Philosophy

This project prioritizes simplicity and performance. Instead of complex multi-agent systems or heavy frameworks, it uses a single strong model with a minimal backend. Each instance is designed to run independently and can later be composed with other tools through an external orchestrator.

---

## Notes

- Performance depends on available RAM and CPU/GPU  
- GPU acceleration is partially supported via llama.cpp  



