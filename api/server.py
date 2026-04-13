from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes.chat import router as chat_router
from api.routes.upload import router as upload_router

app = FastAPI()

# 🔥 GLOBAL STATE
app_state = {
    "ready": False
}

# 🔥 ROUTES
app.include_router(chat_router)
app.include_router(upload_router)

# 🔥 STATIC FILES
app.mount("/static", StaticFiles(directory="interfaces/web"), name="static")


# 🔥 ROOT (UI)
@app.get("/")
def serve_ui():
    return FileResponse("interfaces/web/index.html")


# 🔥 HEALTH CHECK
@app.get("/health")
def health():
    return {"ready": app_state["ready"]}


# 🔥 STARTUP EVENT
@app.on_event("startup")
async def startup_event():
    print("🚀 Server starting...")

    # simulate loading (replace with actual warmup if needed)
    # you can preload models here if you want

    app_state["ready"] = True
    print("✅ Server ready")