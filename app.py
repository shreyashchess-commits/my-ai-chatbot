import streamlit as st
import google.generativeai as genai
from supabase import create_client

# 1. Page Setup
st.set_page_config(page_title="My Custom AI", page_icon="🤖")

# --- DATABASE SETUP ---
# We use 'try/except' so the app won't crash if the database is asleep
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    print("Database connection failed:", e)
    supabase = None
# ----------------------

# --- SIDEBAR MENU ---
with st.sidebar:
    st.title("⚙️ Settings & Info")
    st.markdown("Welcome to my custom AI!")
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        st.rerun()
# -------------------------

st.title("🤖 My Custom AI")

# 2. Add API Key Safely (The .strip() removes any accidental invisible spaces!)
api_key = st.secrets["MY_SECRET_KEY"].strip()
genai.configure(api_key=api_key)

# Use the exact, official model name
model = genai.GenerativeModel('models/gemini-1.5-flash')

# 3. Setup Official Chat Memory
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Show past messages
for message in st.session_state.messages:
    avatar_icon = "🧑‍💻" if message["role"] == "user" else "🌌"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# 5. The Chat Box
prompt = st.chat_input("Type your message here...")

if prompt:
    # Show user message
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show AI response
    with st.chat_message("assistant", avatar="🌌"):
        # Send the message to the memory bank!
        response = st.session_state.chat_session.send_message(prompt, stream=True)
        
        def stream_data():
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        full_response = st.write_stream(stream_data)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # --- SAVE TO DATABASE ---
    if supabase:
        try:
            supabase.table("chat_history").insert({
                "user_message": prompt,
                "ai_message": full_response
            }).execute()
        except Exception as e:
            print(f"Database error: {e}")