import requests
from opik import track

from app.services.agent_service.tool import Tool, ToolParameter

class UrlFetchTool(Tool):
    """
    Generic tool to fetch data from any url
    """
    def __init__(self,):
        super().__init__(
            name="url_fetch",
            description="Fetch data from a provided URL",
            function=UrlFetchTool.execute,
            parameters={
                "url": ToolParameter(
                    description="The URL to fetch data from",
                    type="string",
                    required=True
                )
            }
        )

    @track("url_fetch_tool.execute")
    def execute(self, url: str) -> str:
        """
        Fetches content from the given URL.
        Returns the text content if successful, otherwise returns an error message.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text  # Limit output for safety
        except Exception as e:
            return f"Error fetching URL: {e}"

class UrlFetchFirebaseDBPythonExamplesTool(UrlFetchTool):
    """"
    Specialized tool that fetches Python code examples for Firebase Firestore DB
    from a hardcoded GitHub URL.
    """
    def __init__(self):
        super().__init__()
        self.name = "fetch_firebase_db_python_examples"
        self.description = "Fetch examples to interact with Firebase DB using Python"
        self.parameters = None

    @track("firebase_db_python_api_examples_tool.execute")
    def execute(self, **args) -> str:
        return super().execute(
            "https://github.com/GoogleCloudPlatform/python-docs-samples/blob/b535a5f23cbc4d261547002db8f246eb388bd8e8/firestore/cloud-client/snippets.py#L457-L461"
        )

if __name__ == "__main__":
    tool = UrlFetchFirebaseDBPythonExamplesTool()
    print(tool.execute())