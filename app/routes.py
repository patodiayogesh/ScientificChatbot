import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)

from app.services.upload_pdf_service import UploadPdfService
from app.services.pdf_information_extraction_service import PdfInformationExtractionService
from app.services.db_service import get_firebase_db, DatabaseService

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
def pdf_upload(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF file or Zipped Pdf files.
    """
    try:
        logger.info("Received file upload request.")
        if not file:
            logger.error("No file uploaded.")
            raise HTTPException(status_code=400, detail="No file uploaded.")
        if not (file.filename.endswith('.pdf') or file.filename.endswith('.zip')):
            logger.error("Invalid file type uploaded.")
            raise HTTPException(status_code=400, detail="Only .pdf or .zip files are allowed.")

        new_uploaded_files = UploadPdfService().upload(file)
        if new_uploaded_files is None or len(new_uploaded_files) == 0:
            logger.error("No valid PDF files found in the uploaded file.")
            raise ValueError("No valid PDF files found in the uploaded file.")
        logger.info(f"Successfully uploaded {len(new_uploaded_files)} file(s).")

        # Process the uploaded files
        pdf_information_extraction_service = PdfInformationExtractionService()
        extracted_data = pdf_information_extraction_service.run(new_uploaded_files)

        # Add the extracted data to the database
        db_service = DatabaseService()
        db_service.add_documents(extracted_data)

        return extracted_data
    except Exception as e:
        logger.error(f"Error while uploading/processing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")