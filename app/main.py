import uvicorn
from fastapi import FastAPI
from routes import pdf_router, chat_router
from config.chat_history import bootstrap_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bootstrap_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(pdf_router, prefix="/v1/pdf")
app.include_router(chat_router, prefix="/v1/chat")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
