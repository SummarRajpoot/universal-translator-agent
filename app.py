import streamlit as st
import streamlit.components.v1 as components
import os
import io
import datetime
from gtts import gTTS
import PyPDF2
from docx import Document
from PIL import Image
from translator import translate_text, translate_bulk, extract_text_from_image
from prompts import LANGUAGES
import base64
import tempfile

# RTL Languages list
RTL_LANGUAGES = ["Urdu", "Arabic", "Persian", "Hebrew", "Sindhi", "Pashto"]

# Page Configuration
st.set_page_config(
    page_title="🌍 Universal Translator Agent",
    page_icon="🌍",
    layout="wide"
)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state["history"] = []

# Custom CSS for dark theme and styling
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Input/Output Containers */
    .translation-container {
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #30363d;
        background-color: #161b22;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .translation-header {
        color: #58a6ff;
        font-weight: 600;
        margin-bottom: 10px;
        font-size: 1.1rem;
    }
    
    /* Text result containers */
    .result-text-ltr {
        direction: ltr;
        text-align: left;
        font-size: 1.2rem;
        padding: 15px;
        background: #0d1117;
        border-radius: 8px;
        border-left: 4px solid #58a6ff;
        white-space: pre-wrap;
    }
    
    .result-text-rtl {
        direction: rtl;
        text-align: right;
        font-size: 1.4rem;
        padding: 15px;
        background: #0d1117;
        border-radius: 8px;
        border-right: 4px solid #58a6ff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif, 'Noto Naskh Arabic';
        white-space: pre-wrap;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Divider styling */
    hr {
        margin: 2em 0;
        border: 0;
        border-top: 1px solid #30363d;
    }
    
    .history-item {
        background: #161b22;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 3px solid #58a6ff;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_text_style(lang_name):
    return "result-text-rtl" if lang_name in RTL_LANGUAGES else "result-text-ltr"

def play_audio(text, lang_code="en"):
    try:
        tts = gTTS(text=text, lang='en' if lang_code not in ['ur', 'ar', 'hi', 'fr', 'es', 'de'] else lang_code) # Limited codes for safety, gtts supports many
        # Better: map language names to codes for gTTS
        lang_map = {
            "Urdu": "ur", "English": "en", "Arabic": "ar", "Hindi": "hi", "Spanish": "es", 
            "French": "fr", "German": "de", "Russian": "ru", "Japanese": "ja", "Korean": "ko"
        }
        code = lang_map.get(text, "en") # This is wrong logic, I need target_lang
        # Corrected below in UI
        pass
    except Exception as e:
        st.error(f"Audio Error: {e}")

def add_to_history(original, translated, target_lang):
    item = {
        "original": original,
        "translated": translated,
        "source": "Auto-Detected",
        "target": target_lang,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state["history"].insert(0, item)

def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text, len(reader.pages)

def extract_docx_text(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text, len(text.split())

# Language codes mapping for voice
VOICE_CODES = {
    "Urdu": "ur-PK", "Arabic": "ar-SA", "French": "fr-FR", "Spanish": "es-ES",
    "German": "de-DE", "Chinese": "zh-CN", "Japanese": "ja-JP", "Hindi": "hi-IN",
    "Portuguese": "pt-BR", "Russian": "ru-RU", "Turkish": "tr-TR", "Korean": "ko-KR",
    "Italian": "it-IT", "Dutch": "nl-NL", "English": "en-US"
}

# App Header
st.title("🌍 Universal Translator Agent")
st.markdown("---")

# Language choices
lang_options = [f"{name} — {native}" for name, native in LANGUAGES.items()]
lang_names = list(LANGUAGES.keys())
lang_to_code = {
    "Urdu": "ur", "English": "en", "Arabic": "ar", "Hindi": "hi", "Chinese": "zh",
    "Spanish": "es", "French": "fr", "German": "de", "Russian": "ru", "Japanese": "ja",
    "Korean": "ko", "Turkish": "tr", "Persian": "fa", "Bengali": "bn", "Portuguese": "pt",
    "Italian": "it", "Dutch": "nl", "Polish": "pl", "Swedish": "sv", "Norwegian": "no",
    "Danish": "da", "Finnish": "fi", "Greek": "el", "Thai": "th", "Vietnamese": "vi",
    "Indonesian": "id", "Swahili": "sw"
}

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Single Translation", "Bulk Translation", "Multi Language", 
    "📄 File Upload", "📷 Image Translation", "📜 History"
])

# Tab 1: Single Translation
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Input Text")
        input_text = st.text_area("Original Text:", height=200, key="single_input")
        target_lang_str = st.selectbox("Target Language:", lang_options, key="single_target")
        target_lang = target_lang_str.split(" — ")[0]
        
        if st.button("Translate", type="primary", key="btn_single"):
            if input_text.strip():
                with st.spinner(f"Translating to {target_lang}..."):
                    result = translate_text(input_text, target_lang)
                    st.session_state["single_result"] = result
                    st.session_state["single_target_lang"] = target_lang
                    add_to_history(input_text, result, target_lang)
            else:
                st.warning("Please enter some text.")
        
        # Voice Input (STT)
        voice_input_code = f"""
        <style>
            .mic-container {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin-top: 10px;
                font-family: sans-serif;
            }}
            .mic-btn {{
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background-color: #e63946;
                border: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            }}
            .mic-btn svg {{ fill: white; width: 24px; height: 24px; }}
            .mic-btn.recording {{
                animation: pulse 1.5s infinite;
                background-color: #ff4d4d;
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(230, 57, 70, 0.7); }}
                70% {{ transform: scale(1.1); box-shadow: 0 0 0 10px rgba(230, 57, 70, 0); }}
                100% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(230, 57, 70, 0); }}
            }}
            .status {{ color: #a0a0b0; font-size: 14px; display: none; }}
        </style>
        <div class="mic-container">
            <button id="mic-btn" class="mic-btn" title="Click to speak">
                <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
            </button>
            <span id="mic-status" class="status">🎤 Listening...</span>
        </div>
        <script>
            const micBtn = document.getElementById('mic-btn');
            const micStatus = document.getElementById('mic-status');
            let recognition;
            let recording = false;

            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
                micBtn.style.display = 'none';
                console.log('Speech recognition not supported');
            }} else {{
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = true;
                recognition.lang = 'en-US'; // Default

                recognition.onstart = () => {{
                    recording = true;
                    micBtn.classList.add('recording');
                    micStatus.style.display = 'inline';
                }};

                recognition.onend = () => {{
                    recording = false;
                    micBtn.classList.remove('recording');
                    micStatus.style.display = 'none';
                }};

                recognition.onresult = (event) => {{
                    let transcript = '';
                    for (let i = event.resultIndex; i < event.results.length; i++) {{
                        transcript += event.results[i][0].transcript;
                    }}
                    // Try to find the Streamlit textarea in parent
                    const textareas = window.parent.document.querySelectorAll('textarea');
                    const target = Array.from(textareas).find(t => t.getAttribute('aria-label') === 'Original Text:');
                    if (target) {{
                        target.value = transcript;
                        target.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }};

                micBtn.onclick = () => {{
                    if (recording) {{
                        recognition.stop();
                    }} else {{
                        recognition.start();
                    }}
                }};
            }}
        </script>
        """
        components.html(voice_input_code, height=70)

    with col2:
        st.subheader("Translation Result")
        if "single_result" in st.session_state:
            res = st.session_state["single_result"]
            lang = st.session_state["single_target_lang"]
            
            st.markdown(f'<div class="translation-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="translation-header">{lang} Translation:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="{get_text_style(lang)}">{res}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Feature 1: TTS
            LANG_CODES = {
                "Urdu": "ur", "English": "en", "Arabic": "ar",
                "Hindi": "hi", "French": "fr", "Spanish": "es",
                "German": "de", "Chinese": "zh", "Japanese": "ja",
                "Korean": "ko", "Turkish": "tr", "Russian": "ru",
                "Persian": "fa", "Italian": "it", "Portuguese": "pt"
            }
            
            if st.button("🔊 Listen Translation"):
                with st.spinner("Generating audio..."):
                    try:
                        lang_code = LANG_CODES.get(lang, "en")
                        tts = gTTS(text=res, lang=lang_code, slow=False)
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                            tts.save(f.name)
                            st.audio(f.name, format='audio/mp3')
                    except Exception as e:
                        st.error(f"Speech error: {e}")
            
            # Browser Voice Output (TTS)
            voice_out_lang = VOICE_CODES.get(lang, "en-US")
            voice_output_code = f"""
            <style>
                .spk-container {{
                    display: flex;
                    justify-content: flex-end;
                    margin-top: -40px;
                    margin-bottom: 20px;
                }}
                .spk-btn {{
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background-color: #2ecc71;
                    border: none;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.3s;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                }}
                .spk-btn svg {{ fill: white; width: 20px; height: 20px; }}
                .spk-btn:hover {{ background-color: #27ae60; transform: scale(1.1); }}
                .spk-btn.speaking {{ animation: pulse-green 1s infinite; }}
                @keyframes pulse-green {{
                    0% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }}
                    70% {{ transform: scale(1.05); box-shadow: 0 0 0 10px rgba(46, 204, 113, 0); }}
                    100% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }}
                }}
            </style>
            <div class="spk-container">
                <button id="spk-btn" class="spk-btn" title="Click to listen (Browser Voice)">
                    <svg viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
                </button>
            </div>
            <script>
                const spkBtn = document.getElementById('spk-btn');
                const textToSpeak = `{res.replace('`', '\\`').replace('$', '\\$')}`;
                const lang = '{voice_out_lang}';

                spkBtn.onclick = () => {{
                    if (window.speechSynthesis.speaking) {{
                        window.speechSynthesis.cancel();
                        spkBtn.classList.remove('speaking');
                        return;
                    }}
                    
                    const utterance = new SpeechSynthesisUtterance(textToSpeak);
                    utterance.lang = lang;
                    
                    utterance.onstart = () => spkBtn.classList.add('speaking');
                    utterance.onend = () => spkBtn.classList.remove('speaking');
                    utterance.onerror = () => spkBtn.classList.remove('speaking');
                    
                    window.speechSynthesis.speak(utterance);
                }};
            </script>
            """
            components.html(voice_output_code, height=50)
        else:
            st.info("Translation will appear here...")

# Tab 2: Bulk Translation
with tab2:
    st.subheader("Bulk Translation")
    bulk_input = st.text_area("Enter lines (one per line):", height=200, key="bulk_input")
    bulk_lang_str = st.selectbox("Target Language:", lang_options, key="bulk_target")
    bulk_lang = bulk_lang_str.split(" — ")[0]
    
    if st.button("Translate All", type="primary"):
        if bulk_input.strip():
            lines = [l.strip() for l in bulk_input.split('\n') if l.strip()]
            with st.spinner(f"Translating {len(lines)} lines..."):
                results = translate_bulk(lines, bulk_lang)
                for item in results:
                    add_to_history(item["original"], item["translated"], bulk_lang)
                
                st.subheader("Results:")
                for i, item in enumerate(results):
                    res = item["translated"]
                    with st.expander(f"Result {i+1}: {item['original'][:50]}...", expanded=True):
                        st.markdown(f'<div class="{get_text_style(bulk_lang)}">{res}</div>', unsafe_allow_html=True)
                        if st.button(f"🔊 Listen Line {i+1}", key=f"listen_bulk_{i}"):
                            lang_code = lang_to_code.get(bulk_lang, "en")
                            gTTS(text=res, lang=lang_code).save(f"temp_bulk_{i}.mp3")
                            st.audio(open(f"temp_bulk_{i}.mp3", "rb").read())

# Tab 3: Multi Language
with tab3:
    st.subheader("Multi-Language Translation")
    multi_input = st.text_area("Original Text:", height=150, key="multi_input")
    selected_langs = st.multiselect("Select Target Languages:", lang_names, default=["Urdu", "Spanish"])
    
    if st.button("Translate to All"):
        if multi_input.strip() and selected_langs:
            cols = st.columns(2)
            with st.spinner("Translating..."):
                for i, lang in enumerate(selected_langs):
                    res = translate_text(multi_input, lang)
                    add_to_history(multi_input, res, lang)
                    with cols[i % 2]:
                        st.markdown(f'<div class="translation-container">', unsafe_allow_html=True)
                        st.markdown(f'<div class="translation-header">{lang}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="{get_text_style(lang)}">{res}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

# Tab 4: File Upload
with tab4:
    st.subheader("📄 File Translation (PDF/Word)")
    uploaded_file = st.file_uploader("Upload a PDF or Word file", type=["pdf", "docx"])
    file_target_lang_str = st.selectbox("Target Language:", lang_options, key="file_target")
    file_target = file_target_lang_str.split(" — ")[0]
    
    if uploaded_file and st.button("Extract & Translate"):
        with st.spinner("Processing file..."):
            extracted_text = ""
            stats = ""
            if uploaded_file.name.endswith(".pdf"):
                extracted_text, pages = extract_pdf_text(uploaded_file)
                stats = f"Pages: {pages}"
            else:
                extracted_text, words = extract_docx_text(uploaded_file)
                stats = f"Word count: {words}"
            
            if extracted_text.strip():
                st.write(f"**Filename:** {uploaded_file.name} | **{stats}**")
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    st.text_area("Original Extracted Text", extracted_text, height=300)
                
                translated_file_text = translate_text(extracted_text[:4000], file_target) # Limit to 4000 chars for API
                with col_f2:
                    st.markdown(f'<div class="{get_text_style(file_target)}" style="height:315px; overflow-y:auto;">{translated_file_text}</div>', unsafe_allow_html=True)
                
                add_to_history(f"File: {uploaded_file.name}", translated_file_text, file_target)
                
                st.download_button(
                    label="📥 Download Translated Text (.txt)",
                    data=translated_file_text,
                    file_name=f"translated_{uploaded_file.name}.txt",
                    mime="text/plain"
                )

# Tab 5: Image Translation
with tab5:
    st.subheader("📷 Image Text Extraction & Translation")
    img_option = st.radio("Choose Input Method:", ["Upload Image", "Use Camera"])
    img_file = None
    if img_option == "Upload Image":
        img_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "gif"])
    else:
        img_file = st.camera_input("Take a photo")
    
    img_target_lang_str = st.selectbox("Target Language:", lang_options, key="img_target")
    img_target = img_target_lang_str.split(" — ")[0]

    if img_file and st.button("Extract Text"):
        with st.spinner("OCR-ing Image via Groq Vision..."):
            bytes_data = img_file.getvalue()
            extracted = extract_text_from_image(bytes_data)
            
            if extracted and not extracted.startswith("Error:"):
                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    st.image(img_file, caption="Original Image")
                    st.info(f"**Extracted Text:**\n{extracted}")
                
                with col_i2:
                    with st.spinner("Translating extracted text..."):
                        translated_img = translate_text(extracted, img_target)
                        st.markdown(f'<div class="translation-container">', unsafe_allow_html=True)
                        st.markdown(f'<div class="translation-header">Translated Text ({img_target}):</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="{get_text_style(img_target)}">{translated_img}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        add_to_history("Image OCR", translated_img, img_target)
            else:
                st.error(f"Failed to extract text: {extracted}")

# Tab 6: History
with tab6:
    st.subheader("📜 Translation History")
    if st.button("🗑️ Clear History"):
        st.session_state["history"] = []
        st.success("History cleared!")
    
    if not st.session_state["history"]:
        st.info("No history yet. Start translating!")
    else:
        for i, entry in enumerate(st.session_state["history"]):
            with st.expander(f"{entry['timestamp']} — To {entry['target']} ({entry['original'][:40]}...)", expanded=(i==0)):
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    st.markdown("**Original:**")
                    st.write(entry["original"])
                with col_h2:
                    st.markdown(f"**{entry['target']} Translation:**")
                    st.markdown(f'<div class="{get_text_style(entry["target"])}">{entry["translated"]}</div>', unsafe_allow_html=True)
                st.caption(f"Source: {entry['source']}")

# Footer
st.markdown("---")
st.markdown("""
<style>
.footer {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    padding: 30px 20px;
    border-radius: 12px;
    margin-top: 20px;
    border-top: 3px solid #e63946;
}
.footer-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 30px;
    margin-bottom: 30px;
}
@media (min-width: 768px) {
    .footer-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}
.footer-section h4 {
    color: #e63946;
    font-size: 15px;
    margin-bottom: 12px;
    font-weight: bold;
}
.footer-section p {
    color: #a0a0b0;
    font-size: 13px;
    line-height: 1.7;
    word-break: break-word;
}
.footer-section a {
    color: #a0a0b0;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 13px;
    word-break: break-word;
}
.footer-section a:hover { color: #e63946; }
.footer-section a img {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
}
.footer-bottom {
    border-top: 1px solid #2a2a4a;
    padding-top: 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: center;
    text-align: center;
}
.footer-bottom p { 
    color: #606080; 
    font-size: 12px; 
}
.badge {
    background: #e63946;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ── Feedback section rendered via components.html() so that JS is executed ──
feedback_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { background: transparent; font-family: 'Segoe UI', sans-serif; color: #fff; margin: 0; padding: 0; }
  .fb-wrap { background: linear-gradient(135deg,#1a1a2e,#16213e); border-radius: 12px; padding: 30px; text-align: center; border-top: 3px solid #e63946; }
  .fb-wrap h4 { color: #e63946; font-size: 20px; margin-bottom: 8px; }
  .fb-wrap p  { color: #a0a0b0; margin-bottom: 12px; }
  .fb-btn { margin: 5px; padding: 8px 20px; border-radius: 20px; border: none; color: white; cursor: pointer; font-size: 14px; transition: all 0.2s; }
  .fb-btn:hover { transform: scale(1.05); }
  #exc { background: #4CAF50; }
  #goo { background: #2196F3; }
  #imp { background: #e63946; }
  input, textarea {
    width: 55%; padding: 10px; border-radius: 10px; border: 1px solid #30363d;
    background: #161b22; color: #fff; font-size: 14px; display: block;
    margin: 10px auto 0 auto;
  }
  textarea { height: 80px; resize: vertical; }
  #submitBtn {
    margin-top: 14px; padding: 10px 30px; border-radius: 20px; border: none;
    background: #e63946; color: white; font-weight: bold; cursor: pointer; font-size: 15px;
  }
  #submitBtn:hover { background: #c0303d; }
  #thankMsg { display:none; color: #4CAF50; font-weight: bold; margin-top: 12px; }
  #commentsBox { margin-top: 24px; text-align: left; max-width: 600px; margin-left: auto; margin-right: auto; }
  .comment-card {
    background: #161b22; padding: 14px; border-radius: 10px;
    margin-bottom: 10px; border: 1px solid #30363d;
  }
  .comment-header { display: flex; justify-content: space-between; margin-bottom: 4px; }
  .comment-name  { color: #58a6ff; font-weight: bold; }
  .comment-time  { font-size: 11px; color: #8b949e; }
  .comment-rating{ color: #e63946; font-size: 13px; margin-bottom: 6px; }
  .comment-text  { color: #c9d1d9; font-size: 14px; margin: 0; }
</style>
</head>
<body>
<div class="fb-wrap">
  <h4>&#128172; Feedback</h4>
  <p>How was your experience?</p>
  <div>
    <button class="fb-btn" id="exc" onclick="pickRating(this)">&#11088; Excellent</button>
    <button class="fb-btn" id="goo" onclick="pickRating(this)">&#128077; Good</button>
    <button class="fb-btn" id="imp" onclick="pickRating(this)">&#128078; Needs Improvement</button>
  </div>
  <input  id="userName"    placeholder="Your name (Optional)" />
  <textarea id="feedbackText" placeholder="Write your feedback..."></textarea>
  <br>
  <button id="submitBtn" onclick="doSubmit()">Submit Feedback &#9989;</button>
  <p id="thankMsg">&#9989; Thank you for your feedback!</p>
  <div id="commentsBox"></div>
</div>

<script>
var picked = "";

function pickRating(btn) {
  document.querySelectorAll('.fb-btn').forEach(function(b) {
    b.style.opacity = '0.5';
    b.style.outline = 'none';
  });
  btn.style.opacity = '1';
  btn.style.outline = '3px solid white';
  picked = btn.innerText;
}

function doSubmit() {
  var text = document.getElementById('feedbackText').value.trim();
  var name = document.getElementById('userName').value.trim() || 'Anonymous';
  if (!text) { alert('Please write something!'); return; }

  var list = JSON.parse(localStorage.getItem('feedbacks') || '[]');
  list.push({ name: name, rating: picked, text: text, time: new Date().toLocaleString() });
  localStorage.setItem('feedbacks', JSON.stringify(list));

  document.getElementById('feedbackText').value = '';
  document.getElementById('userName').value    = '';
  document.getElementById('thankMsg').style.display = 'block';
  setTimeout(function() {
    document.getElementById('thankMsg').style.display = 'none';
  }, 3000);
  renderComments();
}

function renderComments() {
  var list = JSON.parse(localStorage.getItem('feedbacks') || '[]');
  var box  = document.getElementById('commentsBox');
  if (!box) return;
  if (!list.length) { box.innerHTML = ''; return; }
  var html = '<h4 style="color:white;border-bottom:1px solid #30363d;padding-bottom:8px;">&#128172; User Comments</h4>';
  list.slice().reverse().forEach(function(c) {
    html += '<div class="comment-card">' +
      '<div class="comment-header"><span class="comment-name">' + c.name + '</span><span class="comment-time">' + c.time + '</span></div>' +
      '<div class="comment-rating">' + c.rating + '</div>' +
      '<p class="comment-text">' + c.text + '</p></div>';
  });
  box.innerHTML = html;
}

renderComments();
</script>
</body></html>
"""
components.html(feedback_html, height=600, scrolling=True)

st.markdown("""
<div class="footer">
    <div class="footer-grid">
        <div class="footer-section">
            <h4>🌍 About Us</h4>
            <p>Universal Translator Agent is an AI-powered 
            translation tool that instantly translates text
            across 30+ world languages.
            Built on Groq AI — one of the fastest AI engines available — it
            delivers accurate, context-aware translations in real time.
            Whether you need to translate a single sentence or bulk content 
            across multiple languages simultaneously, Universal Translator
            Agent makes it effortless. Our multi-language mode lets you reach 
            global audiences instantly, without the wait.
                          Fast. Accurate. Borderless.</p>
        </div>
        <div class="footer-section">
            <div class="contact-section">
  <h4>
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#25D366" style="vertical-align:middle; margin-right:8px">
      <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
    </svg>
    +92308-7322219
  </h4>

  <!-- Email -->
  <a href="mailto:ranasummar48@email.com" style="display:flex; align-items:center; gap:8px; text-decoration:none; color:inherit; margin:8px 0">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#EA4335">
      <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
    </svg>
    ranasummar48@email.com
  </a>

  <!-- LinkedIn -->
  <a href="https://www.linkedin.com/in/rana-summar-295a1a262" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none; color:inherit; margin:8px 0">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#0A66C2">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
    </svg>
    LinkedIn — Rana Summar
  </a>

  <!-- GitHub -->
  <a href="https://github.com/SummarRajpoot" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none; color:inherit; margin:8px 0">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#181717">
      <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
    </svg>
    GitHub — SummarRajpoot
  </a>

  <!-- Facebook -->
  <a href="https://www.facebook.com/share/1KubRomdkX/" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none; color:inherit; margin:8px 0">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#1877F2">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
    </svg>
    Facebook — Rana Summar
  </a>

  <!-- Instagram -->
  <a href="https://www.instagram.com/ranasummar_0" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none; color:inherit; margin:8px 0">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="url(#ig)">
      <defs>
        <linearGradient id="ig" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#FFDC80"/>
          <stop offset="25%" stopColor="#FCAF45"/>
          <stop offset="50%" stopColor="#F77737"/>
          <stop offset="75%" stopColor="#C13584"/>
          <stop offset="100%" stopColor="#833AB4"/>
        </linearGradient>
      </defs>
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/>
    </svg>
    Instagram — ranasummar_0
  </a>

  <!-- YouTube -->
  <a href="https://www.youtube.com/@ranasummar_0" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none; color:inherit; margin:8px 0">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#FF0000">
      <path d="M23.495 6.205a3.007 3.007 0 00-2.088-2.088c-1.87-.501-9.396-.501-9.396-.501s-7.507-.01-9.396.501A3.007 3.007 0 00.527 6.205a31.247 31.247 0 00-.522 5.805 31.247 31.247 0 00.522 5.783 3.007 3.007 0 002.088 2.088c1.868.502 9.396.502 9.396.502s7.506 0 9.396-.502a3.007 3.007 0 002.088-2.088 31.247 31.247 0 00.5-5.783 31.247 31.247 0 00-.5-5.805zM9.609 15.601V8.408l6.264 3.602z"/>
    </svg>
    YouTube — ranasummar_0
  </a>

  <!-- TikTok -->
  <a href="https://www.tiktok.com/@ranasummar_0" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none; color:inherit; margin:8px 0">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#000000">
      <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
    </svg>
    TikTok — ranasummar_0
  </a>

</div>
        </div>
        <div class="footer-section">
            <h4>🌐 Supported Languages</h4>
            <p>✅ 30+ World Languages</p>
            <p>✅ RTL & LTR Support</p>
            <p>✅ Bulk Translation</p>
            <p>✅ File Upload (PDF/Word)</p>
            <p>✅ Image Translation</p>
            <p>✅ Text to Speech</p>
        </div>
    </div>
    <div class="footer-bottom">
        <p>© 2025 Universal Translator Agent. All rights reserved.</p>
        <p>Made with ❤️ by <strong style="color:#e63946">M. Sun Rajpoot</strong></p>
        <span class="badge">Powered by Groq AI</span>
    </div>
</div>
""", unsafe_allow_html=True)
