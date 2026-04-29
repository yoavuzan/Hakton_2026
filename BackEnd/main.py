from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl
import json
import time

from services.scrapper import process_url
from services.langchain import stream_url_for_disability
from services.llm_pipeline import generate_main_summary
from core.logger import setup_logger, get_logger

# ✅ setup logger ONCE
setup_logger()
logger = get_logger("api")


# ✅ unified request model
class AnalyzeRequest(BaseModel):
    url: HttpUrl
    disability: str


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

    logger.info(f"Received request | url={request.url} | disability={request.disability}")

    async def event_generator():
        try:
            # 🔹 STATUS 1
            yield json.dumps({"type": "status", "message": "מנתח את הקישור..."}) + "\n"

            logger.info("Starting scraping...")
            scraped = await process_url(str(request.url))

            sections = scraped.get("sections", [])
            content = "\n".join([s.get("text", "") for s in sections])

            summary = await generate_main_summary(content)
            
            logger.info(f"Summary generated: {summary.title}")

            logger.info(f"Scraping done | sections={len(sections)}")

            if not summary:
                logger.warning("No summary extracted")
                yield json.dumps({"type": "error", "message": "לא נמצא תוכן."}) + "\n"
                return

            # 🔹 STATUS 2
            yield json.dumps({"type": "status", "message": "מנתח את התוכן..."}) + "\n"

            logger.info(f"Summary generated: {summary.title}")

            # 🔹 STREAM LLM
            async for chunk in stream_url_for_disability(summary.model_dump_json(), request.disability):
                yield json.dumps({
                    "type": "data",
                    "chunk": chunk
                }) + "\n"

            # 🔹 END
            yield json.dumps({"type": "end"}) + "\n"

            logger.info("Streaming completed successfully")

        except Exception as e:
            logger.exception("Analyze endpoint failed")

            yield json.dumps({
                "type": "error",
                "message": f"שגיאה: {str(e)}"
            }) + "\n"

        finally:
            elapsed = time.time() - start
            logger.info(f"Request completed in {elapsed:.2f}s")

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")
