import streamlit as st
import google.generativeai as genai
from supabase import create_client

# 1. Page Setup
st.set_page_config(page_title="My Custom AI", page_icon="🤖")

# --- DATABASE SETUP ---
# Grab the keys from the Streamlit Safe
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = create_client(supabase_url, supabase_key)
# ----------------------

# --- SIDEBAR MENU ---
with st.sidebar:
    st.title("⚙️ Settings & Info")
    st.markdown("Welcome to my custom AI!")
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
# -------------------------

st.title("🤖 My Custom AI")

# 2. Add API Key safely
genai.configure(api_key=st.secrets["MY_SECRET_KEY"])

my_ai_personality = """
You are a friendly, funny, and incredibly smart AI assistant. 
Always be encouraging, use a few emojis in every response, and explain things as simply as possible. 
If someone asks who made you, tell them a brilliant coder made you!
"""

model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction=my_ai_personality
)

# 3. Setup Chat Memory
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
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🌌"):
        response = model.generate_content(prompt, stream=True)
        
        def stream_data():
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        full_response = st.write_stream(stream_data)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # --- NEW: SAVE TO DATABASE ---
    # This quietly writes the conversation to your Supabase ledger!
    try:
        supabase.table("chat_history").insert({
            "user_message": prompt,
            "ai_message": full_response
        }).execute()
    except Exception as e:
        print(f"Database error: {e}")