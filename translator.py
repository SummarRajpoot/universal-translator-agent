import os
from groq import Groq
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, build_prompt

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def translate_text(text, target_language="Urdu"):
    if not text.strip():
        return "Please enter some text to translate"
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": build_prompt(text, target_language)
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def translate_bulk(texts, target_language="Urdu"):
    results = []
    for text in texts:
        translated = translate_text(text, target_language)
        results.append({
            "original": text,
            "translated": translated
        })
    return results

def extract_text_from_image(image_bytes):
    """
    Extracts text from an image using Groq vision model.
    """
    import base64
    try:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all text from this image. Return only the text, nothing else."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
