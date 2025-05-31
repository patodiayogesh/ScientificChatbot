from pydantic import BaseModel

class ReferenceRecipe(BaseModel):
    title: str
    authors: list[str]
    publication_date: str
    source: str
    link: str

class SectionRecipe(BaseModel):
    section_title: str
    section_content: str

class TableRecipe(BaseModel):
    table_caption: str
    table_content: str

class FigureRecipe(BaseModel):
    caption_of_figure: str
    figure_description: str

class ExtractedInformationRecipe(BaseModel):
    title: str
    authors: list[str]
    publication_date: str
    abstract: str
    references: list[ReferenceRecipe]
    sections: list[SectionRecipe]
    tables: list[TableRecipe]
    figures: list[FigureRecipe]
    other_information: str
