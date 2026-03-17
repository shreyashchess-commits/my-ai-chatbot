import streamlit as st
import google.generativeai as genai
from supabase import create_client

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Omni-AI Pro", page_icon="⚡", layout="wide")

# --- 2. SECURE CONNECTIONS ---
try:
    genai.configure(api_key=st.secrets["MY_SECRET_KEY"].strip())
    supabase = create_client(st.secrets["SUPABASE_URL"].strip(), st.secrets["SUPABASE_KEY"].strip())
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("⚡ Omni-AI Control")
    st.caption("Commercial Grade Interface")
    st.divider()

    category = st.selectbox("🎯 Capability", ["Chat & Reasoning", "Image Generation"])

    if category == "Chat & Reasoning":
        model_choice = st.selectbox(
            "🧠 Select Brain",
            [
                "gemini-1.5-flash-lite",         # Official ID for 3.1 Flash Lite
                "gemini-1.5-flash",              # Stable workhorse
                "gemini-1.5-pro",                # Smartest
                "gemma-2-27b-it",                # Open Source
            ]
        )
    else:
        model_choice = st.selectbox(
            "🎨 Select Artist",
            ["imagen-3.0-generate-001"] # Stable Image Model
        )

    # --- THE MODEL WATCHER ---
    # If the user changes the model, we clear the old session so the new model takes over
    if "current_model" not in st.session_state:
        st.session_state.current_model = model_choice

    if st.session_state.current_model != model_choice:
        st.session_state.current_model = model_choice
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        st.toast(f"Switched to {model_choice}!", icon="🔄")

    st.divider()
    if st.button("🗑️ Reset All Progress", use_container_width=True):
        st.session_state.messages = []
        if "chat_session" in st.session_state: del st.session_state.chat_session
        st.rerun()

# --- 4. ENGINE INITIALIZATION ---
if "messages" not in st.session_state: 
    st.session_state.messages = []

# --- 5. CHAT INTERFACE ---
st.title(f"Ready: {model_choice}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "🤖"):
        if "image" in msg: st.image(msg["image"])
        else: st.markdown(msg["content"])

prompt = st.chat_input("Ask or describe an image...")

if prompt:
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🤖"):
        try:
            if "imagen" in model_choice:
                # Image Logic
                img_model = genai.ImageGenerationModel(model_choice)
                result = img_model.generate_images(prompt=prompt)
                image = result.images[0]
                st.image(image)
                st.session_state.messages.append({"role": "assistant", "image": image})
            
            else:
                # Chat Logic
                chat_model = genai.GenerativeModel(model_choice)
                if "chat_session" not in st.session_state:
                    st.session_state.chat_session = chat_model.start_chat(history=[])
                
                response = st.session_state.chat_session.send_message(prompt, stream=True)
                
                def stream_data():
                    for chunk in response:
                        if chunk.text: yield chunk.text
                
                full_text = st.write_stream(stream_data)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
                if supabase:
                    supabase.table("chat_history").insert({"user_message": prompt, "ai_message": full_text}).execute()

        except Exception as e:
            st.warning("⚠️ This model is temporarily unavailable or at its limit.")
            st.info(f"System Message: {str(e)}")