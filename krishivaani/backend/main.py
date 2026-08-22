from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import assistant

app = FastAPI(title="KrishiVaani Backend API")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the assistant router
app.include_router(assistant.router, prefix="/assistant", tags=["Assistant"])

@app.get("/")
def read_root():
    return {"status": "KrishiVaani Backend is running!"}
