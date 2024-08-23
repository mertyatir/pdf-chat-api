from fastapi import UploadFile, HTTPException


MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


async def validate_pdf(file: UploadFile):
    # Validate file type
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are allowed.",
        )

    # Validate file content type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid content type. Only PDF files are allowed.",
        )

    # Validate file size
    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File size exceeds the limit of "
                f"{MAX_FILE_SIZE / (1024 * 1024)} MB."
            ),
        )
    # Reset the file pointer to the beginning
    file.file.seek(0)
