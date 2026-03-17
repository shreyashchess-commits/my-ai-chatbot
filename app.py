import streamlit as st
import google.generativeai as genai
from supabase import create_client

st.set_page_config(page_title="My AI", page_icon="🤖")
st.title("🤖 My Personal AI")

# --- 1. SETUP API KEYS SAFELY ---
# .strip() prevents errors if you accidentally copied a blank space
google_key = st.secrets["MY_SECRET_KEY"].strip()
genai.configure(api_key=google_key)

# THE FIX: Restoring the correct, modern Google model that you originally had!
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. SETUP DATABASE ---
try:
    supabase_url = st.secrets["SUPABASE_URL"].strip()
    supabase_key = st.secrets["SUPABASE_KEY"].strip()
    supabase = create_client(supabase_url, supabase_key)
except Exception:
    supabase = None

# --- 3. MEMORY SETUP ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. SHOW PAST CHATS ---
for message in st.session_state.messages:
    avatar_icon = "🧑‍💻" if message["role"] == "user" else "🌌"
    st.chat_message(message["role"], avatar=avatar_icon).markdown(message["content"])

# --- 5. THE CHATBOX ---
prompt = st.chat_input("Type your message here...")

if prompt:
    # Show user message
    st.chat_message("user", avatar="🧑‍💻").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show AI response
    with st.chat_message("assistant", avatar="🌌"):
        try:
            # Ask Google for the answer with the "Typing" effect
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            
            full_response = st.write_stream(stream_data)
            
            # Save to memory
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Save to Supabase (Database)
            if supabase:
                try:
                    supabase.table("chat_history").insert({
                        "user_message": prompt, 
                        "ai_message": full_response
                    }).execute()
                except Exception as db_err:
                    print(f"Database error: {db_err}") # Hides DB errors from your UI
                
        except Exception as e:
            # If Google's free tier is overloaded, it traps the error gracefully
            st.error(f"🚨 GOOGLE API ERROR: {str(e)}")
            st.info("Note: If the error above says 'ResourceExhausted', the free tier is just taking a breather. Please wait 60 seconds and try again!")