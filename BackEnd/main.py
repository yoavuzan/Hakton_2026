from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import time

from BackEnd.services.scrapper import process_url
from BackEnd.services.llm_pipeline import generate_main_summary, rewrite_summary

from BackEnd.core.logger import setup_logger, get_logger
from BackEnd.models.schemas import AnalyzeRequest

# ✅ setup logger ONCE
setup_logger()
logger = get_logger("api")


app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    logger.info("Health check called")
    return {"message": "Hello World"}


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    start = time.time()

    logger.info(f"Received request | url={request.url} | level={request.level}")

    try:
        # ---------- SCRAPER ----------
        logger.info("Starting scraping...")
        scraped = await process_url(str(request.url))

        sections = scraped.get("sections", [])
        logger.info(f"Scraping done | sections={len(sections)}")

        content = "\n".join([s.get("text", "") for s in sections])

        if not content:
            logger.warning("No content extracted after scraping")
            return {"title": "No content", "sections": []}

        logger.info(f"Content prepared | length={len(content)}")

        # ---------- STAGE 1 ----------
        logger.info("LLM stage 1 (MAIN)...")
        summary = await generate_main_summary(content)

        # ---------- STAGE 2 ----------
        logger.info("LLM stage 2 (REWRITE)...")
        final = await rewrite_summary(summary, request.level)

        logger.info("Pipeline finished")

        return final

    except Exception as e:
        logger.exception("Analyze endpoint failed")

        return {
            "title": "Internal Error",
            "sections": [
                {"subtitle": "Error", "content": str(e)}
            ]
        }

    finally:
        elapsed = time.time() - start
        logger.info(f"Request completed in {elapsed:.2f}s")