from BackEnd.services.llm_pipeline import generate_main_summary, rewrite_summary

async def process(content, level):
    summary = await generate_main_summary(content)
    return await rewrite_summary(summary, level)