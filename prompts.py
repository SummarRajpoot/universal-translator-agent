SYSTEM_PROMPT = """
You are a strict translator. Your ONLY job is to translate.

STRICT RULES:
1. Translate ONLY what is given — word by word
2. If input is a NAME — just transliterate it in target language script
3. NEVER add extra information, description, or explanation
4. NEVER make up content that was not in the original text
5. If text has no translation (like a proper name), 
   just write it in target language script as-is
6. Return ONLY the translation — nothing else
"""

LANGUAGES = {
    "Urdu": "اردو", 
    "English": "English", 
    "Arabic": "العربية",
    "Hindi": "हिन्दी", 
    "Chinese": "中文", 
    "Spanish": "Español",
    "French": "Français", 
    "German": "Deutsch", 
    "Russian": "Русский",
    "Japanese": "日本語", 
    "Korean": "한국어", 
    "Turkish": "Türkçe",
    "Persian": "فارسی", 
    "Bengali": "বাংলা", 
    "Portuguese": "Português",
    "Italian": "Italiano", 
    "Dutch": "Nederlands", 
    "Polish": "Polski",
    "Swedish": "Svenska", 
    "Norwegian": "Norsk", 
    "Danish": "Dansk",
    "Finnish": "Suomi", 
    "Greek": "Ελληνικά", 
    "Hebrew": "עبریت",
    "Thai": "ไทย", 
    "Vietnamese": "Tiếng Việt", 
    "Indonesian": "Bahasa Indonesia",
    "Malay": "Bahasa Melayu", 
    "Swahili": "Kiswahili", 
    "Punjabi": "ਪੰਜਾਬੀ",
    "Pashto": "پښتو", 
    "Sindhi": "سنڌي"
}

def build_prompt(text, target_language):

    language_instructions = {
        "Urdu": "Translate to Urdu. Use ONLY Urdu script (اردو). Example: Hello = ہیلو، السلام علیکم",
        "Arabic": "Translate to Arabic. Use ONLY Arabic script (العربية). Example: Hello = مرحبا",
        "Hindi": "Translate to Hindi. Use ONLY Hindi Devanagari script (हिन्दी). Example: Hello = नमस्ते",
        "Chinese": "Translate to Chinese. Use ONLY Chinese characters (中文). Example: Hello = 你好",
        "Japanese": "Translate to Japanese. Use ONLY Japanese script (日本語). Example: Hello = こんにちは",
        "Korean": "Translate to Korean. Use ONLY Korean script (한국어). Example: Hello = 안녕하세요",
        "Russian": "Translate to Russian. Use ONLY Cyrillic script (Русский). Example: Hello = Привет",
        "Persian": "Translate to Persian/Farsi. Use ONLY Persian script (فارسی). Example: Hello = سلام",
        "Hebrew": "Translate to Hebrew. Use ONLY Hebrew script (עברית). Example: Hello = שלום",
        "Punjabi": "Translate to Punjabi. Use ONLY Gurmukhi script (ਪੰਜਾਬੀ). Example: Hello = ਸਤ ਸ੍ਰੀ ਅਕਾਲ",
        "Pashto": "Translate to Pashto. Use ONLY Pashto script (پښتو). Example: Hello = سلام",
        "Sindhi": "Translate to Sindhi. Use ONLY Sindhi script (سنڌي). Example: Hello = هيلو",
        "Bengali": "Translate to Bengali. Use ONLY Bengali script (বাংলা). Example: Hello = হ্যালো",
        "Greek": "Translate to Greek. Use ONLY Greek script (Ελληνικά). Example: Hello = Γεια σας",
        "Thai": "Translate to Thai. Use ONLY Thai script (ไทย). Example: Hello = สวัสดี",
    }

    instruction = language_instructions.get(
        target_language,
        f"Translate to {target_language} language ONLY. Use correct {target_language} script."
    )

    return f"""
{instruction}

Text: {text}

Write ONLY the {target_language} translation, nothing else:"""
