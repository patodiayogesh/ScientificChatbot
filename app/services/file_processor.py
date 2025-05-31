import asyncio
import logging
import os
import zipfile
from pathlib import Path
from fastapi import UploadFile

from app.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class PdfFileProcessor:

    def __init__(self):
        # Define the directory to save extracted files
        self.save_dir = Path(settings.EXTRACTED_FILES_DIR)
        self.save_dir.mkdir(parents=True, exist_ok=True)


    async def _extract_information_from_pdf(self, pdf_file_path: str) -> str:
        """
        Placeholder method to extract information from a PDF file.
        This should be implemented with actual PDF processing logic.

        :param pdf_file_path: Path to the PDF file.
        :return: Extracted information as a string.
        """
        # Implement PDF extraction logic here
        # Simulate a delay for processing
        await asyncio.sleep(1)
        return f"Extracted information from {pdf_file_path}"



    async def _save_pdf(self, file):
        try:
            pdf_path = self.save_dir / Path(file.filename)
            content = await file.read()
            with open(pdf_path, 'wb') as f:
                f.write(content)
            return [pdf_path]
        except Exception as e:
            logger.error(f"Error saving PDF file: {e}")
            raise e

    async def _extract_and_save_zipped_files(self, file: UploadFile) -> list[str]:
        """
        Extract PDF files from a zip file.

        :param zip_file_path: Path to the zip file.
        :return: List of paths to the extracted PDF files.
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
                if file.endswith('.pdf'):
                    extracted_files.append(self.save_dir / file)
                else:
                    raise ValueError(f"The zip file contains non-PDF files. Only PDF files are allowed. Filename: {file}")
            return extracted_files
        except Exception as e:
            logger.error(f"Error creating temporary zip file path: {e}")
            raise e
        finally:
            if temp_zip_file_path:
                os.remove(temp_zip_file_path)# Clean up the temporary zip file

    async def process(self, file:UploadFile) -> str:

        """
        Check if the file is a zipped file. If it is, extract the files and process each PDF file.
        Save the files to a directory and return the directory path.

        :param file:
        :return:
        """
        if file.filename.endswith('.zip'):
            new_uploaded_files = await self._extract_and_save_zipped_files(file)
        else:
            new_uploaded_files = await self._save_pdf(file)
        logger.info(f"New uploaded files: {new_uploaded_files}")
        if new_uploaded_files is None or len(new_uploaded_files) == 0:
            logger.error("No valid PDF files found in the uploaded file.")
            raise ValueError("No valid PDF files found in the uploaded file.")

        for file in new_uploaded_files:
            asyncio.create_task(self._extract_information_from_pdf(file))

        return new_uploaded_files

