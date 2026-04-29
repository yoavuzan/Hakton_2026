from pydantic import BaseModel, Field, HttpUrl
from typing import List

class Section(BaseModel):
    subtitle: str = Field(description="The subtitle of the section")
    content: str = Field(description="The content of the section")


class AnalysisResult(BaseModel):
    title: str = Field(description="The overall title of the summary")
    sections: List[Section] = Field(description="List of sections containing summary details")

class AnalyzeRequest(BaseModel):
    url: HttpUrl
    level: str

