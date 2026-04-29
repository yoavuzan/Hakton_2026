from BackEnd.core.logger import get_logger
from BackEnd.models.schemas import AnalysisResult
from BackEnd.core.config import client
from BackEnd.prompts.prompts import MAIN_PROMPT, LEVEL1_PROMPT, LEVEL2_PROMPT
import json
import time
import re
import ast

logger = get_logger(__name__)


# ---------- STAGE 1 ----------

async def generate_main_summary(content: str) -> AnalysisResult:
    logger.info("LLM stage 1 (MAIN)")
    start = time.time()

    try:
        prompt = MAIN_PROMPT.format(content=content[:8000])

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        text = response.output[0].content[0].text.strip()
        print("RAW STAGE1:\n", text)

        # clean markdown
        text = re.sub(r"```json|```", "", text).strip()

        # extract JSON
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in Stage 1")

        json_str = match.group(0)

        try:
            data = json.loads(json_str)
        except:
            data = ast.literal_eval(json_str)
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
        summary_str = json.dumps(summary.model_dump(), ensure_ascii=False)
        summary_str = summary_str.replace("{", "{{").replace("}", "}}")

        level = (level or "").lower()

        if level == "level1":
            prompt_template = LEVEL1_PROMPT
        else:
            prompt_template = LEVEL2_PROMPT

        prompt = prompt_template.replace("{content}", summary_str)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        text = response.output[0].content[0].text.strip()
        print("RAW STAGE2:\n", text)

        # clean markdown
        text = re.sub(r"```json|```", "", text).strip()

        # extract JSON
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            raise ValueError("No JSON found in Stage 2")

        data = json.loads(match.group(0))

        result = AnalysisResult(**data)

        logger.info(f"Stage 2 done in {time.time() - start:.2f}s")
        return result

    except Exception:
        logger.exception("Stage 2 failed")

        return summary