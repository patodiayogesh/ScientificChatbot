import yaml
from abc import ABC
from google import genai
from pydantic import BaseModel
from opik import track


from app.settings import get_settings

settings = get_settings()


class ModelService(ABC):

    def __init__(self):
        pass

class InformationExtractionModelService(ModelService):
    """
    Service for interacting with the information extraction model.
    """
    def __init__(self):
        super().__init__()
        self.client = genai.Client(api_key=settings.API_KEY)
        self.model_name = settings.INFORMATION_EXTRACTION_MODEL
        self._load_prompt()

    def _load_prompt(self):
        with open(settings.INFORMATION_EXTRACTION_PROMPT_FILE_PATH, 'r') as file:
            prompt = yaml.safe_load(file)
        self.system_prompt = "System: " + prompt["system"]
        self.user_prompt = "User: " + prompt["user"]

    def upload_file(self, file_path: str):
        """
        Uploads a file to the model service.

        :param file_path: Path to the file to be uploaded.
        :return: The uploaded file object.
        """
        return self.client.files.upload(file=file_path)

    @track(name="information_extraction_model_service.execute")
    def execute(self, content: str, recipe: BaseModel) -> str:
        """
        Extract information using the model.

        :param prompt: The prompt to send to the model.
        :return: The model's response.
        """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[self.system_prompt, self.user_prompt, content],
            config = {
                "response_mime_type": "application/json",
                "response_schema": list[recipe],
                'max_output_tokens': 8192,
            }
        )
        return response