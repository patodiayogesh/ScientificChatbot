import json

class ToolParameter:
    def __init__(self, description: str, type: str, required: bool = True, allowed_values: list = None):
        self.description = description
        self.type = type
        self.required = required
        self.allowed_values = allowed_values if allowed_values is not None else []

class Tool:
    def __init__(self, name: str, description: str, function: callable,
                 parameters: dict[str: ToolParameter] = None):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {k: v.__dict__ for k, v in self.parameters.items()} if self.parameters else {},
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def execute(self, *args, **kwargs):
        """
        Execute the tool's function with the provided arguments.
        """
        try:
            return self.function(*args, **kwargs)
        except Exception as e:
            return f"Error executing tool '{self.name}': {e}"

if __name__ == "__main__":
    too1l = Tool("Test tool", description="Test tool",
                function=lambda x: x * 2,
                parameters={"x":ToolParameter(description="Input number", type="integer")})
    tool2 = Tool("Test tool", description="Test tool",
                function=lambda x: x * 2,
                parameters={"x":ToolParameter(description="Input number", type="integer")})

    print("Tools: " + json.dumps([tool.to_dict() for tool in (too1l, tool2)], indent=2, ensure_ascii=False))

