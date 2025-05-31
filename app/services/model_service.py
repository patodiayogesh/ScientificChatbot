from google import genai


class ModelSerice:

    def __init__(self):
        self.client = genai.Client()