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
        self.save_dir = Path(settings.EXTRACTED_FILES_DIR)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    async def _save_pdf(self, file: UploadFile) -> list[Path]:
        """
        Saves a single uploaded PDF file to disk.
        """
        try:
            pdf_path = self.save_dir / Path(file.filename)
            content = await file.read()
            await asyncio.to_thread(self._write_file, pdf_path, content)
            return [pdf_path]
        except Exception as e:
            logger.error(f"Error saving PDF file: {e}")
            raise

    async def _save_zipped_files(self, file: UploadFile) -> list[Path]:
        """
        Extracts PDF files from a zip and saves them in parallel.
        """
        temp_zip_file_path = self.save_dir / Path(file.filename)
        try:
            content = await file.read()
            await asyncio.to_thread(self._write_file, temp_zip_file_path, content)

            extracted_pdf_names = []

            # Extract the zip file
            with zipfile.ZipFile(temp_zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(self.save_dir)
                for name in zip_ref.namelist():
                    if name.endswith('.pdf') and '__MACOSX' not in name and not name.startswith('.'):
                        extracted_pdf_names.append(name)

            # Create tasks to get file paths in parallel
            tasks = [
                asyncio.to_thread(lambda name=name: self.save_dir / name)
                for name in extracted_pdf_names
            ]
            pdf_paths = await asyncio.gather(*tasks)

            # Remove __MACOSX directory if present
            macosx_dir = self.save_dir / '__MACOSX'
            if macosx_dir.exists():
                shutil.rmtree(macosx_dir)

            return pdf_paths
        except Exception as e:
            logger.error(f"Error processing ZIP file: {e}")
            raise
        finally:
            if temp_zip_file_path.exists():
                os.remove(temp_zip_file_path)

    @staticmethod
    def _write_file(path: Path, content: bytes):
        """
        Helper to write file content to disk.
        """
        with open(path, 'wb') as f:
            f.write(content)

    def upload(self, file: UploadFile) -> list[Path]:
        """
        Synchronous wrapper for async file processing logic.
        """
        if file.filename.endswith('.zip'):
            return asyncio.run(self._save_zipped_files(file))
        else:
            return asyncio.run(self._save_pdf(file))
