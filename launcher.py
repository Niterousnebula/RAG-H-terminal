import uvicorn
import os
import threading
import webbrowser
import sys

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    internal_path = os.path.join(base_path, "_internal", relative_path)
    normal_path = os.path.join(base_path, relative_path)

    if os.path.exists(internal_path):
        return internal_path

    return normal_path

def check_models():
    required = [
        "models/deepseek.gguf",
        "models/qwen-coder.gguf",
        "models/mistral.gguf"
    ]

    missing = []

    for m in required:
        full_path = resource_path(m)   # 🔥 correct placement

        if not os.path.exists(full_path):   # 🔥 correct check
            missing.append(m)

    if missing:
        print("\n❌ Missing models:")
        for m in missing:
            print(f"   - {m}")
        return False

    print("✅ All models present")
    return True


def open_browser():
    import time

    print("⏳ Waiting 15 seconds before opening browser...")
    time.sleep(15)

    print("🌐 Opening browser at http://127.0.0.1:5000\n")
    webbrowser.open("http://127.0.0.1:5000")


def print_banner():
    print("=" * 50)
    print("🚀 MCP LOCAL AI SYSTEM")
    print("=" * 50)
    print(f"📍 URL: http://127.0.0.1:5000")
    print("🧠 Models: DeepSeek | Qwen | Mistral")
    print("⚙️ Mode: CPU")
    print("=" * 50 + "\n")


def start():
    print_banner()

    if not check_models():
        print("\n⚠️ Please download required models before running.\n")
        input("Press Enter to exit...")
        return

    # 🔥 open browser in background
    threading.Thread(target=open_browser, daemon=True).start()

    print("⚡ Starting server...\n")

    try:
        uvicorn.run(
            "api.server:app",
            host="127.0.0.1",
            port=5000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    start()