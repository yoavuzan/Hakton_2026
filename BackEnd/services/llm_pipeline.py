from BackEnd.core.logger import get_logger
from BackEnd.models.schemas import AnalysisResult
from BackEnd.services.llm_manager import LLMManager
from BackEnd.prompts import MAIN_PROMPT, LEVEL1_PROMPT, LEVEL2_PROMPT
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
import time

logger = get_logger(__name__)


# ---------- STAGE 1 ----------

async def generate_main_summary(content: str) -> AnalysisResult:
    logger.info("LLM stage 1 (MAIN)")
    start = time.time()

    try:
        llm = LLMManager().get_llm()
        parser = JsonOutputParser(pydantic_object=AnalysisResult)

        prompt = ChatPromptTemplate.from_template(MAIN_PROMPT)
        chain = prompt | llm | parser

        data = await chain.ainvoke({"content": content[:8000]})
        result = AnalysisResult(**data)

        logger.info(f"Stage 1 done in {time.time() - start:.2f}s")
        return result

    except Exception:
        logger.exception("Stage 1 failed")

        return AnalysisResult(
            title="Error",
            sections=[{"subtitle": "Error", "content": "Failed to summarize content"}]
        )

# ---------- STAGE 2 ----------
async def rewrite_summary(summary: AnalysisResult, level: str) -> AnalysisResult:
    logger.info(f"LLM stage 2 ({level})")
    start = time.time()

    try:
        llm = LLMManager().get_llm()
        parser = JsonOutputParser(pydantic_object=AnalysisResult)

        level = (level or "").lower()
        prompt_text = LEVEL1_PROMPT if level == "level1" else LEVEL2_PROMPT

        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | llm | parser

        data = await chain.ainvoke({"content": summary.model_dump_json()})
        result = AnalysisResult(**data)

        logger.info(f"Stage 2 done in {time.time() - start:.2f}s")
        return result

    except Exception:
        logger.exception("Stage 2 failed")
        return summary
