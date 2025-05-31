from app.services.model_service import InformationExtractionModelService
from app.services.recipe import ExtractedInformationRecipe

class PdfInformationExtractionService:
    """
    Service for extracting information from PDF files.
    """

    def __init__(self):
        """
        Initializes the service with a PDF reader.

        :param pdf_reader: An instance of a PDF reader class that can read and extract text from PDFs.
        """
        self.load_pipeline()

    def load_pipeline(self):
        """
        Loads the PDF reader pipeline for extracting text from PDF files.
        This method should initialize the PDF reader instance.
        """
        # self.pdf_reader = PdfReader()  # Assuming PdfReader is a class that handles PDF reading to extract text, images, etc.
        self.extracted_information_recipe = ExtractedInformationRecipe()  # Using the recipe for structured information extraction
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
        extracted_information = self.pdf_reader.execute(
            cloud_uploaded_file,
            recipe = self.extracted_information_recipe
        )
        return extracted_information