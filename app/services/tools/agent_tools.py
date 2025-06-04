import requests

from opik import track

from app.services.tool import Tool, ToolParameter



class UrlFetchTool(Tool):
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
    def execute(self, url: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text  # Limit output for safety
        except Exception as e:
            return f"Error fetching URL: {e}"

class UrlFetchFirebaseDBPythonExamplesTool(UrlFetchTool):
    def __init__(self):
        super().__init__()
        self.name = "fetch_firebase_db_python_examples"
        self.description = "Fetch examples to interact with Firebase DB using Python"
        self.parameters = None

    @track("firebase_db_python_api_examples_tool.execute")
    def execute(self, **args):
        # Placeholder for actual Firebase DB interaction logic
        return super().execute(
            "https://github.com/GoogleCloudPlatform/python-docs-samples/blob/b535a5f23cbc4d261547002db8f246eb388bd8e8/firestore/cloud-client/snippets.py#L457-L461"
        )

if __name__ == "__main__":

    tool = UrlFetchFirebaseDBPythonExamplesTool()
    print(tool.execute())