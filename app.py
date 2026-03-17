import streamlit as st
import google.generativeai as genai

# 1. Page Setup
st.set_page_config(page_title="My Personal AI", page_icon="🤖")

# --- NEW: SIDEBAR MENU ---
with st.sidebar:
    st.title("⚙️ Settings & Info")
    st.markdown("Welcome to my custom AI! This chatbot is powered by Google's Gemini 2.5 Flash model.")
    st.markdown("It can answer questions, write code, and help with brainstorming.")
    
    st.divider() # This adds a nice neat line
    
    # Add a "Clear Chat" button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = [] # Wipes the memory clean
        st.rerun() # Refreshes the screen
# -------------------------

# 2. Main Title
st.title("🤖 My Personal AI")

# 3. Add your API Key securely from the Streamlit Safe
genai.configure(api_key=st.secrets["MY_SECRET_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# 4. Setup the Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Show the past messages on the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. The Chat Box where the user types
prompt = st.chat_input("Type your message here...")

if prompt:
    # Show the user's message on the screen
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Save the user's message into memory
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Show the AI's response with the "Typing" effect
    with st.chat_message("assistant"):
        # Ask Gemini for the answer and tell it to stream
        response = model.generate_content(prompt, stream=True)
        
        # Create a mini-delivery system to print words one by one
        def stream_data():
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        # Use Streamlit's built-in typing effect!
        full_response = st.write_stream(stream_data)
        
    # Save the AI's final message into memory
    st.session_state.messages.append({"role": "assistant", "content": full_response})