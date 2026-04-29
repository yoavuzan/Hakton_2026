import aiohttp
import asyncio
import trafilatura
from bs4 import BeautifulSoup
import time
from BackEnd.core.logger import setup_logger, get_logger


# use centralized logger
logger = get_logger(__name__)


# ---------- FETCH ----------
async def get_html(url: str) -> str:
    timeout = aiohttp.ClientTimeout(total=10)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url) as response:

                logger.info(f"HTTP {response.status} | {url}")

                #  bad HTTP response
                if response.status != 200:
                    raise Exception(f"HTTP error {response.status}")

                content_type = response.headers.get("Content-Type", "")

                #  not HTML
                if "text/html" not in content_type:
                    raise Exception(f"Not HTML: {content_type}")

                return await response.text()

    except asyncio.TimeoutError:
        raise Exception("Request timed out")

    except aiohttp.ClientError as e:
        raise Exception(f"Connection error: {str(e)}")


# ---------- TRAFILATURA ----------
def extract_text_sync(html: str):
    return trafilatura.extract(html, include_formatting=True)


async def extract_text_async(html: str):
    return await asyncio.to_thread(extract_text_sync, html)


# ---------- TITLE ----------
def extract_title(html: str):
    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    if soup.title:
        return soup.title.get_text(strip=True)

    return ""


# ---------- SMART PARSER ----------
def parse_text_smart(text: str):
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    sections = []
    current = None

    has_subtitles = any(line.startswith("## ") for line in lines)

    if has_subtitles:
        for line in lines:
            if line.startswith("## "):
                if current:
                    sections.append(current)

                current = {
                    "subtitle": line.replace("## ", ""),
                    "text": ""
                }
            else:
                if current:
                    current["text"] += " " + line

        if current:
            sections.append(current)

    else:
        for i, line in enumerate(lines):
            sections.append({
                "subtitle": f"פסקה {i+1}",
                "text": line
            })

    return sections


# ---------- PIPELINE ----------
async def process_url(url: str):
    start_total = time.time()

    logger.info(f"Start scraping | url={url}")

    try:
        # ---------- FETCH ----------
        t0 = time.time()
        html = await get_html(url)
        logger.info(f"HTML fetched in {time.time() - t0:.2f}s")

        # ---------- TITLE ----------
        t1 = time.time()
        title = await asyncio.to_thread(extract_title, html)
        logger.info(f"Title extracted in {time.time() - t1:.2f}s | title={title[:50]}")

        # ---------- TEXT ----------
        t2 = time.time()
        text = await extract_text_async(html)
        logger.info(f"Text extracted in {time.time() - t2:.2f}s")

        if not text:
            logger.warning("No text extracted")
            return {"title": title, "sections": []}

        # ---------- PARSE ----------
        t3 = time.time()
        sections = parse_text_smart(text)
        logger.info(f"Parsed into {len(sections)} sections in {time.time() - t3:.2f}s")

        return {
            "title": title,
            "sections": sections
        }

    except Exception:
        logger.exception("Scraping failed")  # full traceback

        return {"title": "Error", "sections": []}

    finally:
        logger.info(f"Total scraping time: {time.time() - start_total:.2f}s")