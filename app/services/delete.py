import json
from pydantic import BaseModel
dummy = """
[
  {
    "title": "Automated Code Editing with Search-Generate-Modify",
    "authors": [
      "Changshu Liu",
      "Pelin Cetin*",
      "Yogesh Patodia*",
      "Baishakhi Ray",
      "Saikat Chakraborty",
      "Yangruibo Ding"
    ],
    "publication_date": "May, 2023",
    "abstract": "Code editing is essential in evolving software development. In literature, several automated code editing tools are proposed, which leverage Information Retrieval-based techniques and Machine Learning-based code generation and code editing models. Each technique comes with its own promises and perils, and for this reason, they are often used together to complement their strengths and compensate for their weaknesses. This paper proposes a hybrid approach to better synthesize code edits by leveraging the power of code search, generation, and modification."
  }
]
"""


class PdfMetaDataRecipe(BaseModel):
    title: str
    authors: list[str]
    publication_date: str
    abstract: str

class PdfMetaDataRecipe2(BaseModel):
    title: str
    authors: list[str]
    publication_date: str
    abstract: str

class Parent(BaseModel):
    title: str
    authors: list[str]
    publication_date: str
    abstract: str
    tables_and_figures: PdfMetaDataRecipe2

data = json.loads(dummy)
paper = PdfMetaDataRecipe(**data[0])
dummy2 = PdfMetaDataRecipe2(**data[0])

for key, value in dummy2.model_dump().items():
    print(f"{key}: {value}")

print(paper.title)