import streamlit as st
import google.generativeai as genai
from supabase import create_client

# --- 1. PAGE CONFIG & BRANDING ---
st.set_page_config(page_title="Omni-AI Pro", page_icon="⚡", layout="wide")

# --- 2. SECURE CONNECTIONS ---
try:
    genai.configure(api_key=st.secrets["MY_SECRET_KEY"].strip())
    supabase = create_client(st.secrets["SUPABASE_URL"].strip(), st.secrets["SUPABASE_KEY"].strip())
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# --- 3. SIDEBAR: THE CONTROL CENTER ---
with st.sidebar:
    st.title("⚡ Omni-AI Control")
    st.caption("Commercial Grade Interface")
    st.divider()

    # CATEGORY SELECTOR
    category = st.selectbox("🎯 Capability", ["Chat & Reasoning", "Image Generation"])

    if category == "Chat & Reasoning":
        model_choice = st.selectbox(
            "🧠 Select Brain",
            [
                "gemini-3.1-flash-lite-preview", # Best for Free Tier (500/day)
                "gemini-3.1-pro-preview",        # Smartest
                "gemini-2.5-flash",              # Stable workhorse
                "gemma-3-27b-it",                # Open Source Smart
                "gemma-3-4b-it",                 # Open Source Fast
                "gemini-2.5-flash-native-audio"  # Audio specialist
            ]
        )
    else:
        model_choice = st.selectbox(
            "🎨 Select Artist",
            ["imagen-4.0-generate-001", "imagen-4.0-ultra-generate-001", "imagen-4.0-fast-generate-001"]
        )

    st.divider()
    if st.button("🗑️ Reset All Progress", use_container_width=True):
        st.session_state.messages = []
        if "chat_session" in st.session_state: del st.session_state.chat_session
        st.rerun()

# --- 4. ENGINE INITIALIZATION ---
if "messages" not in st.session_state: st.session_state.messages = []

# --- 5. CHAT INTERFACE ---
st.title(f"Ready: {model_choice}")

# Show History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"]=="user" else "🤖"):
        if "image" in msg: st.image(msg["image"])
        else: st.markdown(msg["content"])

# User Input
prompt = st.chat_input("Ask or describe an image...")

if prompt:
    # Save User Input
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🤖"):
        try:
            # --- CHOICE A: IMAGE GENERATION ---
            if "imagen" in model_choice:
                with st.spinner("🎨 Creating masterpiece..."):
                    img_model = genai.ImageGenerationModel(model_choice)
                    result = img_model.generate_images(prompt=prompt, number_of_images=1)
                    image = result.images[0]
                    st.image(image)
                    st.session_state.messages.append({"role": "assistant", "image": image})
            
            # --- CHOICE B: CHAT GENERATION ---
            else:
                chat_model = genai.GenerativeModel(model_choice)
                if "chat_session" not in st.session_state:
                    st.session_state.chat_session = chat_model.start_chat(history=[])
                
                response = st.session_state.chat_session.send_message(prompt, stream=True)
                
                def stream_data():
                    for chunk in response:
                        if chunk.text: yield chunk.text
                
                full_text = st.write_stream(stream_data)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
                # Silent Log to Supabase
                supabase.table("chat_history").insert({"user_message": prompt, "ai_message": full_text}).execute()

        except Exception as e:
            st.warning("⚠️ This model is at its limit.")
            st.info(f"System Message: {str(e)}")