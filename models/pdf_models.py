from pydantic import BaseModel


class UploadPDFResponse(BaseModel):
    pdf_id: str
