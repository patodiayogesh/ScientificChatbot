import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)

from app.services.file_processor import PdfFileProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
def health_check():
    """
    Health check endpoint to verify if the service is running.
    """
    logger.info("Health check endpoint successfully accessed.")
    return {"status": "ok"}

@router.post("/pdf_upload")
async def pdf_upload(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF file or Zipped Pdf files.
    """
    try:
        # check if the file is provided
        logger.info("Received file upload request.", file)
        if not file:
            logger.error("No file uploaded.")
            raise HTTPException(status_code=400, detail="No file uploaded.")

        print(file, file.filename, file.content_type)

        if not (file.filename.endswith('.pdf') or file.filename.endswith('.zip')):
            logger.error("Invalid file type uploaded.")
            raise HTTPException(status_code=400, detail="Only .pdf or .zip files are allowed.")
        # Process the file using PdfFileProcessor
        logger.info(f"Processing file: {file}")
        response = await PdfFileProcessor().process(file)

        return {"File(s) saved successfully. Extraction running in background": response}
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")