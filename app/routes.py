import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)

from app.services.file_processor import PdfFileProcessor
from app.services.pdf_information_extraction_service import PdfInformationExtractionService

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


        if not (file.filename.endswith('.pdf') or file.filename.endswith('.zip')):
            logger.error("Invalid file type uploaded.")
            raise HTTPException(status_code=400, detail="Only .pdf or .zip files are allowed.")
        # Process the file using PdfFileProcessor
        logger.info(f"Processing file: {file}")
        new_uploaded_files = await PdfFileProcessor().process(file)

        # Extract information using InformationExtractionModelService
        logger.info("Extracting information from the uploaded file(s).")
        extraction_model_service = PdfInformationExtractionService()
        logger.info(new_uploaded_files)
        response = extraction_model_service.execute(new_uploaded_files[0])

        return {"File(s) saved successfully. Extraction running in background": response}
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")