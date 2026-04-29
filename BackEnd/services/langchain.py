from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
import json

from BackEnd.prompts import LEVEL2_PROMPT, LEVEL1_PROMPT
from BackEnd.services.llm_manager import LLMManager


# ----------------------
# ✅ Models
# ----------------------
class Section(BaseModel):
    subtitle: str = Field(description="The subtitle of the section")
    content: str = Field(description="The content of the section")


class AnalysisResult(BaseModel):
    title: str = Field(description="The overall title of the summary")
    sections: List[Section] = Field(description="List of sections")


# ----------------------
# ✅ Internal helper
# ----------------------
def _get_prompt(disability: str):
    return LEVEL2_PROMPT if "level2" in disability.lower() else LEVEL1_PROMPT


# ----------------------
# ✅ Main non-streaming (replacement for old process)
# ----------------------
async def process(content: str, disability: str):
    """
    Keeps compatibility with old scrapper-init design
    """
    return await process_url_for_disability(content, disability)


# ----------------------
# ✅ Structured processing
# ----------------------
async def process_url_for_disability(content: str, disability: str):
    prompt_text = _get_prompt(disability)

    try:
        llm = LLMManager().get_llm()
        parser = JsonOutputParser(pydantic_object=AnalysisResult)

        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | llm | parser

        result = await chain.ainvoke({"content": content})
        return result

    except Exception as e:
        return {
            "title": "Error Processing Content",
            "sections": [
                {
                    "subtitle": "Error",
                    "content": str(e)
                }
            ]
        }


# ----------------------
# ✅ Streaming version (used by FastAPI)
# ----------------------
async def stream_url_for_disability(summary: str, disability: str):
    prompt_text = _get_prompt(disability)

    try:
        llm = LLMManager().get_llm()
        parser = JsonOutputParser(pydantic_object=AnalysisResult)

        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | llm | parser

        async for chunk in chain.astream({"content": summary}):
            if chunk:
                yield chunk

    except Exception as e:
        yield {
            "title": "Error",
            "sections": [
                {"subtitle": "Error", "content": str(e)}
            ]
        }