import asyncio
import logging
import json
from pathlib import Path
from opik import track

from app.services.model_service import InformationExtractionModelService
from app.services.recipe import (
    PdfInformationRecipe,
    PdfMetaDataRecipe,
    PdfContentDataRecipe,
    TablesAndFiguresRecipe,
)

logger = logging.getLogger(__name__)

class PdfInformationExtractionService:
    """
    Service for extracting information from PDF files.
    This service orchestrates the extraction of metadata, content, and tables/figures
    from PDF documents using different recipes and a model service.
    """

    def __init__(self):
        # self.pdf_reader = PdfReader()  # Assuming PdfReader is a class that handles PDF reading to extract text, images, etc.
        # Initialize the recipes to be used for information extraction.
        # Each recipe defines the structure of the data to be extracted.
        self.recipes = {
            "metadata": PdfMetaDataRecipe,
            #"content_data": PdfContentDataRecipe,
            "tables_and_figures": TablesAndFiguresRecipe
        }
        self.pdf_information_recipe = PdfInformationRecipe  # Using the recipe for structured information extraction
        self.pdf_reader = InformationExtractionModelService()  # Using the model service for extraction

    def modify_recipe_format(self, recipe_data: dict) -> dict:
        """
        Modifies the recipe data format to match the expected structure.
        :param recipe_data: The raw recipe data extracted from the PDF.
        :return: Modified recipe data in the expected format.
        """
        # This function can be customized based on how the raw data needs to be transformed.
        # For now, we assume that the data is already in the correct format.
        try:
            new_recipe_format = {}
            for key, value in recipe_data.items():
                if key == "metadata":
                    for metadata_key, metadata_value in value.model_dump().items():
                            new_recipe_format[metadata_key] = metadata_value
                else:
                    new_recipe_format[key] = value
            return new_recipe_format
        except Exception as e:
            logger.error(f"Error modifying recipe format: {e}")
            raise ValueError("Invalid recipe data format. Please check the extracted data format.")

    @track(name="pdf_information_extraction_service.execute")
    async def execute(self, file_path: Path) -> PdfInformationRecipe:
        """
        Extracts text/information from the specified PDF file.
        Can be modified to include multiple APIs/Services to extract information.
        :param file_path: The path to the PDF file.
        :return PdfInformationRecipe: Extracted information.
        """

        # For simplicity, we are using one model for all information extraction.
        # In a real-world scenario, you might want to use different pre-processing steps, models, or configurations based on the type of PDF or the specific information you want to extract.
        # You can define your workflow here, such as pre-processing the PDF, extracting text, and then using the model to extract information.
        logger.info(f"Starting extraction for file: {file_path}")
        cloud_uploaded_file = self.pdf_reader.upload_file(file_path)
        # TODO: The below call can be made in parallel, but due to API restrictions, we are making it sequentially.
        recipe_data = {}
        try:
            for recipe_name, recipe in self.recipes.items():
                recipe_info = self.pdf_reader.execute(cloud_uploaded_file,recipe = recipe).text
                recipe_data[recipe_name] = recipe(**json.loads(recipe_info)[0])  # Convert the JSON string to the appropriate recipe model
                logger.info(f"Extracted information using recipe {recipe.__name__} for file: {file_path}")
        except Exception as e:
            logger.error(f"Error extracting complete information from PDF: {e}")
        finally:
            if not recipe_data:
                raise Exception("No information extracted from the PDF file.")
            if "metadata" not in recipe_data:
                raise Exception("Metadata extraction failed. Please check the PDF file format or content.")
            new_recipe_data = self.modify_recipe_format(recipe_data)
            extracted_pdf_information = PdfInformationRecipe.model_construct(**new_recipe_data)
            return extracted_pdf_information

    async def aexecute(self, file_path: Path):
        """
        Asynchronously extracts information from the specified PDF file.
        Wrapper around the execute method to allow for asynchronous execution.

        :param file_path: The path to the PDF file.
        """
        return await self.execute(file_path)

    @track(name="pdf_information_extraction_service.arun")
    async def arun(self, uploadedFiles: list[Path]) -> list[PdfInformationRecipe]:
        """
        Runs the extraction process asynchronously and in parallel for a list of uploaded files.
        :param uploadedFiles: A list of paths to the uploaded PDF files.
        :return list[PdfInformationRecipe]: A list of extracted information from the PDF files.
        """
        logger.info(f"Starting asynchronous extraction for {uploadedFiles}")
        tasks = [asyncio.create_task(self.aexecute(file)) for file in uploadedFiles]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Completed parallel execution for all files.")
        return results

    @track(name="pdf_information_extraction_service.run")
    def run(self, uploadedFiles: list[Path])-> list[PdfInformationRecipe]:
        """
        Function to call asynchronous function to process all files parallely.
        Entry point for running the information extraction process synchronously.
        :param uploadedFiles: A list of paths to the uploaded PDF files.
        :return list[PdfInformationRecipe]: A list of extracted information from the PDF files.
        """
        return asyncio.run(self.arun(uploadedFiles))

