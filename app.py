import streamlit as st
import google.generativeai as genai
from supabase import create_client

st.set_page_config(page_title="My AI", page_icon="🤖")
st.title("🤖 My Personal AI")

# --- 1. SETUP API KEYS SAFELY ---
# .strip() removes any accidental invisible spaces you might have copied!
google_key = st.secrets["MY_SECRET_KEY"].strip()
genai.configure(api_key=google_key)

# Using the most stable model name
model = genai.GenerativeModel('gemini-pro')

# --- 2. SETUP DATABASE ---
try:
    supabase_url = st.secrets["SUPABASE_URL"].strip()
    supabase_key = st.secrets["SUPABASE_KEY"].strip()
    supabase = create_client(supabase_url, supabase_key)
except Exception as e:
    st.warning(f"Database isn't connected yet, but chat will still work! Error: {e}")
    supabase = None

# --- 3. MEMORY SETUP ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. SHOW PAST CHATS ---
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

# --- 5. THE CHATBOX ---
prompt = st.chat_input("Type your message here...")

if prompt:
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show AI response with the ERROR TRAP
    with st.chat_message("assistant"):
        try:
            # We are turning OFF 'stream=True' temporarily to see if it fixes the crash
            response = st.session_state.chat_session.send_message(prompt)
            st.markdown(response.text)
            
            # Save to memory
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # Save to Supabase
            if supabase:
                supabase.table("chat_history").insert({
                    "user_message": prompt, 
                    "ai_message": response.text
                }).execute()
                
        except Exception as e:
            # THIS IS THE TRAP! It forces the hidden error to show on your screen!
            st.error(f"🚨 GOOGLE API ERROR: {str(e)}")
            st.info("Please copy the red text above and send it to me!")