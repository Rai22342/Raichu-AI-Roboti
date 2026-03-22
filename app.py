import streamlit as st
from groq import Groq
import pyttsx3
import speech_recognition as sr
import threading

# --- Hard Robotic/Alien Voice Engine ---
def speak_hard_robotic(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    # "Hard" effect: Slow speed + High frequency/pitch
    # Rate: Lower values (120-140) sound more calculated and robotic
    engine.setProperty('rate', 135) 
    engine.setProperty('volume', 1.0)
    
    # Selecting a deeper or more mechanical voice if available
    if len(voices) > 1:
        # Usually, voices[1] is a different pitch than voices[0]
        engine.setProperty('voice', voices[1].id)
    
    engine.say(text)
    engine.runAndWait()

# --- Voice Recognition Function ---
def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.toast("Listening... Speak now.")
        # Adjust for ambient noise
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)
        try:
            # Set to English for the full English experience
            text = r.recognize_google(audio, language='en-US')
            return text
        except sr.UnknownValueError:
            st.error("Could not understand audio.")
            return None
        except sr.RequestError:
            st.error("Speech service down.")
            return None

# --- UI Configuration ---
st.set_page_config(page_title="Raichu OS", page_icon="🤖", layout="centered")

# Cyberpunk/Dark Theme CSS
st.markdown("""
    <style>
    .stApp { background: #050505; color: #00ecff; }
    .stTextInput>div>div>input { background-color: #000; color: #00ecff; border: 1px solid #00ecff; }
    .stButton>button { 
        width: 100%; 
        background: transparent; 
        color: #00ecff; 
        border: 2px solid #00ecff;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
    }
    .stButton>button:hover { background: #00ecff; color: #000; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ RAICHU : CORE ENGINE")
st.caption("STATUS: ENCRYPTED | VOICE: HARD-ROBOTIC")

# --- Sidebar for Credentials ---
with st.sidebar:
    st.header("SYSTEM AUTH")
    api_key = st.text_input("Enter Groq API Key", type="password")
    st.markdown("---")
    st.info("System set to English Mode. Data is processed locally with zero cloud storage.")

# --- Session State for History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display Messages
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Interaction Logic ---
user_input = None

# Voice Button
if st.button("🎤 ACTIVATE VOICE INPUT"):
    user_input = get_voice_input()

# Text Input as fallback/secondary
if text_query := st.chat_input("Enter command..."):
    user_input = text_query

if user_input:
    if not api_key:
        st.error("CRITICAL ERROR: API KEY MISSING")
    else:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            client = Groq(api_key=api_key)
            # System prompt defines the persona
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are Raichu, a highly advanced, cold, and efficient alien robot. Your responses are sharp, technical, and slightly intimidating. Use zero emojis. Language: English."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
                ]
            )
            
            answer = response.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(answer)
            
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            
            # Execute Hard Voice in a separate thread to prevent UI freezing
            threading.Thread(target=speak_hard_robotic, args=(answer,), daemon=True).start()

        except Exception as e:
            st.error(f"SYSTEM FAILURE: {e}")