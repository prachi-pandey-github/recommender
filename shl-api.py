from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in environment variables.")

genai.configure(api_key=api_key)

# Gemini model initialization
model = genai.GenerativeModel("gemini-2.0-flash")

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/recommend")
async def recommend_assessment(request: PromptRequest):
    try:
        response = model.generate_content(request.prompt)
        return {"recommendations": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
