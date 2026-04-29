import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables FIRST
load_dotenv()

# Create ONE client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))