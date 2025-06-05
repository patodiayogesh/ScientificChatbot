# ScientificChatBot

A modular, agent-based scientific chatbot system that leverages LLMs and tool-augmented agents to extract, validate, and retrieve information from scientific PDFs.

## Features
- **PDF Information Extraction:** Extracts structured data from scientific PDFs.
- **Database Integration:** Stores and retrieves documents in Firestore, supporting nested schema queries.
- **Agent Architecture:** Modular agents (database agent, validation agent, super agent) orchestrate tool use and LLM reasoning.
- **Tool-Augmented Reasoning:** LLMs can decide when to invoke tools/functions for advanced queries.
- **Prompt Engineering:** Customizable YAML prompts for each agent.
- **LLM Monitoring:** Allows to view prompts, response, response metadata, execution sequence, etc on UI for easy analysis.

## Cloud services used for the project (You will need to set up the following accounts):
- **Firebase Realtime Database** Stores information in nosql format allowing easy retrieval of data at any level
- **Gemini Model API** LLM Model Service
- **Opik** LLM monitoring solution to analyze and debug LLM inputs and response


## Project Structure
```
app/
  main.py                  # FastAPI app entrypoint
  routes.py                # API routes
  settings.py              # Configuration and environment variables
  services/
    agent_service/
      agent.py             # Agent base classes and orchestration logic
      agent_tools.py       # Tool definitions for agents
      tool.py              # Tool interface
    chatbot_service.py     # Main chatbot orchestration and agent loading
    db_service.py          # Firestore database service (add documents)
    pdf_information_extraction_service.py # PDF parsing and extraction
    recipe.py              # Data models for extracted information
    upload_pdf_service.py  # PDF upload handling
prompts/
  db_agent.yaml            # Prompt for database agent
  information_validation_agent.yaml # Prompt for validation agent
  super_agent.yaml         # Prompt for super agent
  information_extraction.yaml # Prompt for extraction agent
example_pdfs/              # Example PDFs for testing
extracted_files/           # Output of PDF extraction
```

## Setup
1. **Install dependencies:**
   - Ensure you have uv installed in your system
   ```bash
   uv venv
   source .venv/bin/activate
   uv sync
   ```
2. **Set up Firebase database and other settings in `app/settings.py`:**
   - Place your Google service account key as `google_service_key.json` in the project root.
   - Set up the below in `.env` file
     - API_KEY 
     - GOOGLE_APPLICATION_CREDENTIALS 
     - FIREBASE_COLLECTION_NAME 
     - OPIK_API_KEY 
     - OPIK_WORKSPACE

3. **Run the API:**
   ```bash
   python app/main.py
   ```

## API Endpoints:

Interactive API Documentation
Once the server is running, access the interactive Swagger UI at:
All endpoints and details are available in Swagger UI [http://localhost:8000/docs](http://localhost:8000/docs)
This provides detailed documentation, parameter descriptions, and allows you to try out the endpoints directly from your browser.

### `GET /health`
- **Description:** Health check endpoint to verify if the service is running.
- **Response Example:**
  ```json
  {
    "status": "ok"
  }

### `POST /pdf_upload`
- **Description:**  Upload a single PDF or a ZIP file containing multiple PDFs. Extracts and stores data from the PDFs.
- **Request:**
  - Content-Type: multipart/form-data 
  - Form field: file (PDF or ZIP)
  - Example using curl:
  ```
  curl -X POST "http://localhost:8000/pdf_upload" \
  -H "accept: application/json" \
  -H 'Content-Type: multipart/form-data' \
  -F "file=@example.pdf;type=application/pdf"
  ```
  - Response Example:
      [
        {
          "metadata": {
            "title": "Example Title",
            "author": "John Doe"
          },
          "content": "Extracted content from the PDF."
        }
      ]

### `POST /chatbot`
- **Description:**: Send a query to the chatbot and receive a response.
- **Request:**
  - Content-Type: application/x-www-form-urlencoded 
  - Form field: query (string)
  - Example using curl:
  ```
  curl -X POST "http://localhost:8000/chatbot" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=Compare paper X and Y?"
  ```
  - Response Example:
      {
        "response": "Paper X and Paper Y talk about LLMs"
      }

## Usage
- Upload PDFs.
- Query the chatbot with natural language; the system will extract, validate, and retrieve information as needed.
- The LLM agents will decide when to use tools (e.g., database queries) and return results accordingly.

## PDF Upload and Information Extraction System Overview

The PDF upload and extraction system is designed to handle individual PDFs or ZIP archives containing multiple PDFs. It performs structured information extraction using LLMs guided by predefined recipes.

### Upload Workflow
- Users can upload either:
  - A single `.pdf` file.
  - A `.zip` file containing multiple `.pdf` files.
- The uploaded file is saved to a predefined directory.
- If the file is a ZIP archive, it is extracted and all PDFs are processed.

**Relevant Module:** `upload_pdf_service.py`  
Handles file saving, ZIP extraction, and cleaning up unwanted system artifacts (e.g., `__MACOSX`).

### Information Extraction Workflow
- Each uploaded PDF undergoes structured extraction via the `PdfInformationExtractionService`.
- The `PdfInformationExtractionService` extracts information from each pdf asynchronously in parallel to reduce computation time.
- The file is first uploaded to the Gemini model service using the `InformationExtractionModelService`.
- Multiple extraction "recipes" (defined using Pydantic models) guide the model to extract specific types of information.

#### Recipes Used
- `PdfMetaDataRecipe` – for extracting metadata such as title, authors, etc.
- `TablesAndFiguresRecipe` – for identifying tables and figures.
- `PdfContentDataRecipe` - for identifying the section content

**Relevant Module:** `pdf_information_extraction_service.py`

### Model Service Integration
- The system uses Google’s Gemini LLM via the `genai` SDK.
- Prompts for extraction are defined in a YAML file (`INFORMATION_EXTRACTION_PROMPT_FILE_PATH`).
- The `InformationExtractionModelService` sends prompt + file to the Gemini API, expecting a structured JSON output that conforms to the specified recipe schema.

**Relevant Module:** `model_service.py`

### Extraction Logic Summary
1. The system uploads the PDF to the Gemini model.
2. For each recipe:
   - The system sends a prompt + file to the LLM.
   - The response is parsed and validated into the appropriate schema.
3. All extracted components are combined into a unified `PdfInformationRecipe` model.
4. Final structured output includes extracted metadata, figures, tables, and any additional information recipes defined.

## Chatbot Agent System Overview
This chatbot system is designed around a modular agent architecture leveraging language models (LLMs) to provide intelligent, multi-step query handling with tool and code execution capabilities.

### Agent Class
- **AbstractAgent**: An abstract base class defining the interface and structure for any agent.
- **Agent**: A concrete implementation that interacts with the language model, processes prompts, manages tools, and can execute code snippets returned by the model.
- **SuperAgent**: A higher-level agent that manages multiple agents and orchestrates their interactions based on model responses.

### Agents
- **db_agent:** `Agent` that generates code (refers internet if necessary), executes code and retrieves documents from Firestore based on schema fields (supports nested fields).
- **information_validation_agent:**  `Agent` that validates and refines extracted or retrieved information.
- **super_agent:** `SuperAgent` that orchestrates the above agents, deciding which to invoke for a given query.

### Tools
The chatbot supports a flexible tool framework allowing dynamic execution of external utilities to enhance the agent's capabilities.
- **ToolParameter**: Defines metadata for each tool's input parameters, including description, type, whether required, and allowed values.
- **Tool**: Represents a tool with a name, description, callable function, and parameters. Tools can be executed dynamically with input validation and error handling.

### Agent Tools
Specialized tools extend the base Tool class:
- **UrlFetchTool**: A generic tool to fetch text content from any given URL. It handles HTTP requests, errors, and returns the fetched content or an error message.
- **UrlFetchFirebaseDBPythonExamplesTool**: Inherits from UrlFetchTool and fetches specific Python code examples for interacting with Firebase Firestore DB from a GitHub URL. This tool demonstrates how agents can access external code snippets or data to inform responses.

### ChatbotService
This is the main service layer which initializes and manages agents:
- Loads prompts from YAML files.
- Creates individual agents like the db_agent for database queries and information_validation_agent for validating generated information.
- Creates a SuperAgent that orchestrates these agents, deciding which agent to invoke based on the conversation context and LLM instructions.

## How It Works

1. **Initialization**  
   When the chatbot service starts, it loads configuration prompts and initializes agents with their respective prompts, tools, and models.
2. **Handling Queries**  
   When a user sends a query:
   - The query is passed to the SuperAgent.
   - The SuperAgent sends the query and current conversation context to the language model.
   - The model’s response is parsed to check if any sub-agent should be invoked or if any tool/code execution is required.
   - If a sub-agent invocation is detected, the SuperAgent routes the query to the corresponding agent, waits for its response, and integrates it back into the conversation.
   - If tools or code snippets are included in the response, they are executed dynamically and their output is added to the context.
   - This multi-turn execution continues until the language model signals no further operations or a maximum iteration count is reached.
   - The response from each agent is passed to the subsequent agent to improve/act upon.
3. **Response Generation**  
   Finally, the chatbot returns the aggregated response generated from the model, including any outputs from tools or code executions, ensuring rich and context-aware answers.
4. **Prompt Approach**
   - The model is prompted to generate Thought and Action following the paper [ReAct](https://arxiv.org/abs/2210.03629)
   - The thought process allows model to select the tools/agents appropriately and reduces chances of errors.


## Features
- **Multi-Agent Orchestration**: The SuperAgent delegates tasks to specialized agents for database querying, validation, or other domain-specific operations.
- **Extensible Tool Framework**: Supports dynamic execution of tools with well-defined parameter schemas and robust error handling.
- **Web Data Fetching**: Tools like UrlFetchTool allow agents to fetch and incorporate real-time external web content.
- **Code Example Retrieval**: Specialized tools can fetch domain-specific code snippets (e.g., Firebase DB Python examples) to assist with programming-related queries.
- **Context Management**: Maintains conversation history and execution context for coherent and stateful interactions.
- **Configurable Prompts**: Uses YAML-based prompt templates for easy customization of agent behaviors.
- **Error Handling and Logging**: Provides detailed logging and error capture to ensure robustness.

### Example Query
"Compare papers X and Y"

The system will:
1. Use the super agent to interpret the query.
2. The super_agent will identify that it needs to call db_agent
3. The db_agent will generate code given the schema. If code execution fails, it will take exception error and try to generate code again.
4. The generated code will be executed and if output is sufficient db_agent will terminate.
5. The super_agent will identify whether validator agent needs to be called or if response can be returned.
6. If validator agent is called, the agent will check for completeness.
7. If validator identifies information is incomplete, super agent will automatically orchestrate the usage of db_agent again if necessary.
8. If no further operations/improvements can be performed, the response will be sent back to the user.

## Customization
- Add new or specialized services to extract information from pdf in `PdfInformationExtractionService`
- Add new tools in `app/services/agent_service/agent_tools.py` and register them with agents.
- Modify prompts in the `prompts/` directory to change agent behavior.
- Add new agents in `app/services/chatbot_service.py`

## Current limitations and Future Work
Due to the constraint of time, the above solution has been built to allow addition of multiple components for future updates.
**PDF Information Extraction**
  - Currently, the service depends entirely on Generative LLM for extraction which is costly. 
  - Specialized python packages (PyPDF) can be used for reading pdf to extract all the sections. 
  - Specialized algorithms (Tabula, DL Based) can be used for table data extraction. 
  - Some solutions while reading pdfs can jumble the pdf content format 
  - An OCR tool/LLM can be used if pdf is an image to convert it to text.
  - Because a Generative LLM is being used to extract text, it will fail if information length is above input context length. 
  - Chunking and iterative or hierarchical solution should be built if LLMs are to be used.
  - As Generative LLMs are being used for extraction, if the output length is above max_tokens, an incomplete response is obtained.
  - To resolve the above: a solution can be built to input context and previous response, requesting model to generate the remaining text and then join those texts.
**Chatbot Agent System**
  - DB Agent is being used to generate code. 
  - A repository of functions can be created as tools, and passed as input to model (as tools) for function selection along with parameters, reducing chances of error.
  - A repository of functions can be embedded, and a solution can be built to select the best function based on user query. This would reduce input token length.
  - The Agent fails to perform complicated queries and the above solution will help execute complex queries.
  - We can also build more specialized agents that focus on only one task and enforce the same using guardrails.
  - The prompting approach can be improved. Prompt-chaining, Auto-COT, TALM etc can also be introduced for complex queries.
  - The issue of long input and output is also applicable here.
  - Having a multi-agent tool increases the latency. Optimization required via parallelism or smart task routing
  - Additional guardrails can be implemented to prevent db update or other out-of-scope requests/actions.
  - The system might not be able to handle multiple languages.

## License
The code or any excerpt from the code should not to be used for any commercial purpose.