import google.generativeai as genai
import os


google_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
