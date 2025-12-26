from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import predict, auth, ws_detection, stream

app = FastAPI(title="Phase 3 AI Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/api/auth")
app.include_router(predict.router, prefix="/api")
app.include_router(stream.router, prefix="/api")
app.include_router(ws_detection.router)

@app.get("/")
async def root():
    return {"message": "AI Monitoring Backend Phase 3 Active"}
