from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    message: str


class PDFChatPath(BaseModel):
    pdf_id: str = Field(..., min_length=1, description="The ID of the PDF")
