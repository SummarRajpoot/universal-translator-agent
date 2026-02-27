import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class Translator:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in .env")
        self.client = Groq(api_key=self.api_key)

    def translate(self, text, target_lang="English", source_lang=None):
        if not text:
            return ""
        
        system_prompt = "You are a fast real-time translator. Translate the text to the target language. Return ONLY the translation."
        user_prompt = f"Translate to {target_lang}: {text}"
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant", # or llama3-70b-8192
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Translation Error: {e}"
