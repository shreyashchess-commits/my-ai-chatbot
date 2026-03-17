import streamlit as st
import google.generativeai as genai
from supabase import create_client

# --- 1. PROFESSIONAL PAGE SETUP ---
st.set_page_config(page_title="Premium AI Assistant", page_icon="✨", layout="centered")

# --- 2. SECURE CLOUD CONNECTIONS ---
# Google Gemini AI Setup
try:
    google_key = st.secrets["MY_SECRET_KEY"].strip()
    genai.configure(api_key=google_key)
    
    # THE FIX: Swapping to the "Pro" model to try and bypass the Flash daily limit!
    model = genai.GenerativeModel('gemini-2.5-pro')
    
except Exception as e:
    st.error(f"Configuration Error: Please check your Google API Key. {e}")
    st.stop() # Stops the app gracefully if the key is missing

# Supabase Database Setup (Your Secure Ledger)
try:
    supabase_url = st.secrets["SUPABASE_URL"].strip()
    supabase_key = st.secrets["SUPABASE_KEY"].strip()
    supabase = create_client(supabase_url, supabase_key)
except Exception as e:
    supabase = None
    # A tiny, professional pop-up notification instead of a big red error
    st.toast("Database not connected. Chats won't be saved, but you can still talk!", icon="⚠️")

# --- 3. UI: SIDEBAR (THE APP MENU) ---
with st.sidebar:
    st.title("✨ AI Assistant Pro")
    st.caption("Powered by Advanced AI Models")
    st.divider()
    
    st.markdown("### 🛠️ Controls")
    # A professional, full-width button to reset the app
    if st.button("🗑️ Clear Chat & Memory", use_container_width=True):
        st.session_state.messages = []
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        st.rerun()
        
    st.divider()
    
    # A cool Admin Status area to show off your database connection
    st.markdown("### 📊 System Status")
    if supabase:
        st.success("🟢 Database Online")
        st.caption("All interactions are securely logged.")
    else:
        st.error("🔴 Database Offline")

# --- 4. CORE ENGINE & MEMORY ---
st.title("Welcome to your Premium AI ✨")
st.markdown("Ask me anything—I can write code, analyze data, and brainstorm ideas.")

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. RENDER CHAT HISTORY ---
for message in st.session_state.messages:
    # Clean, professional avatars
    avatar_icon = "👤" if message["role"] == "user" else "✨"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# --- 6. CHAT INPUT & PROCESSING ---
prompt = st.chat_input("Message the AI...")

if prompt:
    # 1. Display and save user prompt
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Display and generate AI response
    with st.chat_message("assistant", avatar="✨"):
        try:
            # Streaming the response for that premium feel
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            
            full_response = st.write_stream(stream_data)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # 3. Log to Supabase Database (Silent operation)
            if supabase:
                try:
                    supabase.table("chat_history").insert({
                        "user_message": prompt, 
                        "ai_message": full_response
                    }).execute()
                except Exception as db_err:
                    # We print this to the server logs, but don't bother the user with red text
                    print(f"Failed to log to database: {db_err}")
                    
        except Exception as e:
            # Professional error handling if the AI is overloaded or out of quota
            st.warning("⚠️ The AI is experiencing high traffic or has hit its daily Free Tier limit.")
            st.info(f"System Log: {str(e)}")