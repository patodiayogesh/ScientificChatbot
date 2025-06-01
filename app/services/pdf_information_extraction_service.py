import logging
import json
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
    """

    def __init__(self):
        """
        Initializes the service with a PDF reader.
        """
        # self.pdf_reader = PdfReader()  # Assuming PdfReader is a class that handles PDF reading to extract text, images, etc.
        self.recipes = {
            "metadata": PdfMetaDataRecipe,
            # "content_data": PdfContentDataRecipe,
            # "tables_and_figures": TablesAndFiguresRecipe
        }
        self.pdf_information_recipe = PdfInformationRecipe  # Using the recipe for structured information extraction
        self.pdf_reader = InformationExtractionModelService()  # Using the model service for extraction


    def execute(self, pdf_path):
        """
        Extracts text from the specified PDF file.

        :param pdf_path: The path to the PDF file.
        :return: Extracted text as a string.
        """

        # For simplicity, we are using one model for all information extraction.
        # In a real-world scenario, you might want to use different pre-processing steps, models, or configurations based on the type of PDF or the specific information you want to extract.
        # You can define your workflow here, such as pre-processing the PDF, extracting text, and then using the model to extract information.
        cloud_uploaded_file = self.pdf_reader.upload_file(pdf_path)
        # TODO: The below call can be made in parallel, but due to API restrictions, we are making it sequentially.
        recipe_data = {}
        try:
            for recipe_name, recipe in self.recipes.items():
                recipe_info = self.pdf_reader.execute(cloud_uploaded_file,recipe = recipe).text
                recipe_data[recipe_name] = recipe(**json.loads(recipe_info)[0])  # Convert the JSON string to the appropriate recipe model
                logger.info(f"Extracted information using recipe {recipe.__name__}")
        except Exception as e:
            logger.error(f"Error extracting complete information from PDF: {e}")
        finally:
            if recipe_data:
                extracted_pdf_information = PdfInformationRecipe.model_construct(**recipe_data)
                return extracted_pdf_information
            else:
                raise Exception("No information extracted from the PDF file.")