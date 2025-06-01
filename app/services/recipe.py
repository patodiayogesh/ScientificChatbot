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

class PdfContentDataRecipe(BaseModel):
    references: list[ReferenceRecipe]
    sections: list[SectionRecipe]

class TablesAndFiguresRecipe(BaseModel):
    tables: list[TableRecipe]
    figures: list[FigureRecipe]

class PdfMetaDataRecipe(BaseModel):
    title: str
    authors: list[str]
    publication_date: str
    abstract: str

class PdfInformationRecipe(BaseModel):
    title: str
    authors: list[str]
    publication_date: str
    abstract: str
    content_data: PdfContentDataRecipe
    tables_and_figures: TablesAndFiguresRecipe


