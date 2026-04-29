import asyncio
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
import json
import logging

logger = logging.getLogger(__name__)

class Section(BaseModel):
    subtitle: str = Field(description="The subtitle of the section")
    content: str = Field(description="The content of the section")

class AnalysisResult(BaseModel):
    title: str = Field(description="The overall title of the summary")
    sections: List[Section] = Field(description="List of sections containing summary details")

ANXIETY_PROMPT = """
You are an assistant helping someone with anxiety. 
Please summarize the following webpage content in a calm, simple, and reassuring way. 
Avoid overwhelming details and focus on the most important information.
Format the output as a JSON object with 'title' and 'sections' (each section having 'subtitle' and 'content').

Content:
{content}
"""

PTSD_PROMPT = """
You are an assistant helping someone with PTSD. 
Please summarize the following webpage content. 
Be direct, use clear structure, and provide trigger warnings if any potentially distressing content is found. 
Ensure the summary is safe and supportive.
Format the output as a JSON object with 'title' and 'sections' (each section having 'subtitle' and 'content').

Content:
{content}
"""

async def process_url_for_disability(content: str, disability: str):

    logger.info("Starting LLM pipeline")

    if not content:
        logger.warning("Empty content received")
        return {
            "title": "Empty Content",
            "sections": []
        }

    logger.info(f"Content length: {len(content)}")

    if disability.lower() == "anxiety":
        prompt_text = ANXIETY_PROMPT
        logger.info("Selected ANXIETY prompt")
    else:
        prompt_text = PTSD_PROMPT
        logger.info("Selected PTSD prompt")

    try:
        logger.info("Initializing LLM...")
        llm = ChatOllama(model="qwen2.5:3b", temperature=0)

        logger.info("Creating parser...")
        parser = JsonOutputParser(pydantic_object=AnalysisResult)

        logger.info("Building prompt template...")
        prompt = ChatPromptTemplate.from_template(prompt_text)

        logger.info("Building chain...")
        chain = prompt | llm | parser

        logger.info("Calling LLM...")
        result = await chain.ainvoke({"content": content[:10000]})

        logger.info("LLM response received")

        if isinstance(result, dict) and "sections" in result:
            logger.info(f"Generated {len(result['sections'])} sections")
        else:
            logger.warning("Unexpected response format")

        return result

    except Exception as e:
        logger.error(f"LLM failed: {str(e)}")

        return {
            "title": "Error Processing Content",
            "sections": [
                {
                    "subtitle": "Error",
                    "content": str(e)
                }
            ]
        }
