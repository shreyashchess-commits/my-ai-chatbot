import streamlit as st
import google.generativeai as genai

# 1. Page Setup
st.set_page_config(page_title="My Personal AI", page_icon="🤖")

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

# --- NEW: SYSTEM INSTRUCTION (THE AI'S PERSONALITY) ---
# You can change this text to make your AI act however you want!
my_ai_personality = """
You are a friendly, funny, and incredibly smart AI assistant. 
Always be encouraging, use a few emojis in every response, and explain things as simply as possible. 
If someone asks who made you, tell them a brilliant coder made you!
"""

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction=my_ai_personality # This gives the AI its instructions!
)
# --------------------------------------------------------

# 3. Setup Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Show past messages with NEW AVATARS
for message in st.session_state.messages:
    # If the user is talking, use a human emoji. If the AI is talking, use a galaxy emoji!
    avatar_icon = "🧑‍💻" if message["role"] == "user" else "🌌"
    
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# 5. The Chat Box
prompt = st.chat_input("Type your message here...")

if prompt:
    # Show user message with their avatar
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show AI response with its custom avatar
    with st.chat_message("assistant", avatar="🌌"):
        response = model.generate_content(prompt, stream=True)
        
        def stream_data():
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        full_response = st.write_stream(stream_data)
        
    # Save AI message
    st.session_state.messages.append({"role": "assistant", "content": full_response})