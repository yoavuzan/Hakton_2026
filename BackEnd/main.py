from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from BackEnd.services.scrapper import process_url
from BackEnd.services.langchain import process_url_for_disability
import logging
import time

logger = logging.getLogger("api")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
class AnalyzeRequest(BaseModel):
    url: str
    disability: str

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    start = time.time()

    logger.info(f"Received request | url={request.url} | disability={request.disability}")

    try:
        # 1. scrape
        logger.info("Starting scraping...")
        scraped = await process_url(request.url)

        sections = scraped.get("sections", [])
        logger.info(f"Scraping done | sections={len(sections)}")

        # 2. convert sections → text
        content = "\n".join([s.get("text", "") for s in sections])

        if not content:
            logger.warning("No content extracted after scraping")
            return {"title": "No content", "sections": []}

        logger.info(f"Content prepared | length={len(content)}")

        # 3. LLM
        logger.info("Sending to LLM...")
        result = await process_url_for_disability(content, request.disability)
        logger.info("LLM processing finished")

        return result

    except Exception as e:
        logger.error(f"Analyze endpoint failed: {str(e)}")

        return {
            "title": "Internal Error",
            "sections": [
                {"subtitle": "Error", "content": str(e)}
            ]
        }

    finally:
        logger.info(f"Request completed in {time.time() - start:.2f}s")