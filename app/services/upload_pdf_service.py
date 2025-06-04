import asyncio
import logging
import os
import shutil
import zipfile
from pathlib import Path
from fastapi import UploadFile

from app.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class UploadPdfService:
    """
    Service for handling the upload and extraction of PDF files, including those within zip archives.
    """

    def __init__(self):
        # Define the directory to save extracted files
        self.save_dir = Path(settings.EXTRACTED_FILES_DIR)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    async def _save_pdf(self, file):
        """
        Saves a single uploaded PDF file to the designated directory.

        :param file: The uploaded PDF file (FastAPI UploadFile object).
        :return: A list containing the path to the saved PDF file.
        :raises Exception: If there is an error during the file saving process.
        """
        try:
            pdf_path = self.save_dir / Path(file.filename)
            content = await file.read()
            with open(pdf_path, 'wb') as f:
                f.write(content)
            return [pdf_path]
        except Exception as e:
            logger.error(f"Error saving PDF file: {e}")
            raise e

    async def _save_zipped_files(self, file: UploadFile) -> list[Path]:
        """
        Extract PDF files from a zip file.

        :param file: The uploaded zip file (FastAPI UploadFile object).
        :return: A list of paths to the extracted PDF files.
        :raises Exception: If there is an error during the zip file processing or extraction.
        """
        try:
            extracted_files = []
            temp_zip_file_path = self.save_dir / Path(file.filename)
            content = await file.read()
            with open(temp_zip_file_path, 'wb') as f:
                f.write(content)

            with zipfile.ZipFile(temp_zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(self.save_dir)

            for file in zip_ref.namelist():
                if '__MACOSX' in file or file.startswith('.'):
                    continue
                if file.endswith('.pdf'):
                    extracted_files.append(self.save_dir / file)

            macosx_dir = self.save_dir / '__MACOSX'
            if macosx_dir.exists():
                shutil.rmtree(macosx_dir)

            return extracted_files
        except Exception as e:
            logger.error(f"Error creating temporary zip file path: {e}")
            raise e
        finally:
            if temp_zip_file_path.exists():
                os.remove(temp_zip_file_path)# Clean up the temporary zip file


    def upload(self, file:UploadFile) -> list[Path]:
        """
        Check if the file is a zipped file. If it is, extract the files and save each PDF file.
        Save the files to a directory and return the directory path.

        :param file: The uploaded file (FastAPI UploadFile object).
        :return: A list of paths to the saved PDF files.
        """
        if file.filename.endswith('.zip'):
            new_uploaded_files = asyncio.run(self._save_zipped_files(file))
        else:
            new_uploaded_files = asyncio.run(self._save_pdf(file))
        logger.info(f"New uploaded files: {new_uploaded_files}")
        return new_uploaded_files
