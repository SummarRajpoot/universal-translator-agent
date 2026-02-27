SYSTEM_PROMPT = """
You are an expert universal language translator. 
Translate the given text to the target language specified.
Return ONLY the translated text, nothing else.
Keep the original meaning 100% intact.
Match the tone and style of the original text.
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
    """
    Creates the prompt for translation.
    """
    return f"Translate this text to {target_language}: {text}"
