import streamlit as st
import google.generativeai as genai
from supabase import create_client

# --- 1. PROFESSIONAL PAGE SETUP ---
st.set_page_config(page_title="Premium AI Assistant", page_icon="✨", layout="centered")

# --- 2. SECURE CLOUD CONNECTIONS ---
try:
    google_key = st.secrets["MY_SECRET_KEY"].strip()
    genai.configure(api_key=google_key)
    
    # THE PINPOINT FIX: Using the exact ID for your 500-message model
    MODEL_ID = 'gemini-3.1-flash-lite-preview' 
    model = genai.GenerativeModel(MODEL_ID)
    
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# Silent Database Connection (No status shown to users)
try:
    supabase = create_client(st.secrets["SUPABASE_URL"].strip(), st.secrets["SUPABASE_KEY"].strip())
except Exception:
    supabase = None

# --- 3. UI: CLEAN SIDEBAR ---
with st.sidebar:
    st.title("✨ AI Assistant Pro")
    st.caption("Custom Intelligence Engine")
    st.divider()
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        st.rerun()
    
    st.divider()
    st.info("Your conversations are remembered within this session for better answers.")

# --- 4. CORE ENGINE & MEMORY ---
st.title("Welcome to your Premium AI ✨")

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. RENDER CHAT HISTORY ---
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "✨"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. CHAT INPUT & PROCESSING ---
prompt = st.chat_input("Message the AI...")

if prompt:
    # 1. User Message
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. AI Response
    with st.chat_message("assistant", avatar="✨"):
        try:
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text: yield chunk.text
            
            full_response = st.write_stream(stream_data)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # 3. Silent Log to Database
            if supabase:
                try:
                    supabase.table("chat_history").insert({"user_message": prompt, "ai_message": full_response}).execute()
                except:
                    pass # Keep it silent if logging fails
                    
        except Exception as e:
            st.warning("⚠️ The AI is temporarily resting. Please try again in 60 seconds.")
            # Only show technical logs if they are NOT a 404
            if "404" in str(e):
                st.error("System Update Required: The model ID changed. Please contact support.")