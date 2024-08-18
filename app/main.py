import uvicorn
from fastapi import FastAPI
from routes import pdf_router, chat_router


app = FastAPI()


app.include_router(pdf_router, prefix="/v1/pdf")
app.include_router(chat_router, prefix="/v1/chat")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
