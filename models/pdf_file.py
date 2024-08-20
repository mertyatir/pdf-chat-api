from sqlalchemy import Column, String, LargeBinary, Integer
from config import Base


class PDFFile(Base):
    __tablename__ = "pdf_files"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, index=True)
    content = Column(LargeBinary)
    page_count = Column(Integer)
    file_hash = Column(String, unique=True)
