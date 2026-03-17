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

# --- 3. AUTO-MODEL DISCOVERY ---
# This part is the "expert" fix. It looks for a working 'lite' model.
@st.cache_resource
def get_available_lite_model():
    try:
        for m in genai.list_models():
            # Looks for any model with 'flash' and 'lite' in the name
            if 'flash' in m.name and 'lite' in m.name:
                return m.name
        return "gemini-1.5-flash" # Fallback if no lite is found
    except:
        return "gemini-1.5-flash"

LITE_MODEL = get_available_lite_model()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚡ Omni-AI Control")
    st.caption("Commercial Grade Interface")
    st.divider()

    category = st.selectbox("🎯 Capability", ["Chat & Reasoning", "Image Generation"])

    if category == "Chat & Reasoning":
        model_choice = st.selectbox(
            "🧠 Select Brain",
            [
                LITE_MODEL,      # The auto-discovered Lite model (500/day)
                "gemini-1.5-flash", 
                "gemini-1.5-pro",
                "gemma-2-27b-it"
            ]
        )
    else:
        model_choice = st.selectbox(
            "🎨 Select Artist",
            ["imagen-3.0-generate-001"]
        )

    st.divider()
    if st.button("🗑️ Reset All Progress", use_container_width=True):
        st.session_state.messages = []
        if "chat_session" in st.session_state: del st.session_state.chat_session
        st.rerun()

# --- 5. ENGINE INITIALIZATION ---
if "messages" not in st.session_state: st.session_state.messages = []

# --- 6. CHAT INTERFACE ---
st.title(f"Ready: {model_choice}")

for msg in st.session_state.messages:
    avatar = "👤" if msg["role"]=="user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        if "image" in msg: st.image(msg["image"])
        else: st.markdown(msg["content"])

prompt = st.chat_input("Ask or describe an image...")

if prompt:
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🤖"):
        try:
            if "imagen" in model_choice:
                img_model = genai.ImageGenerationModel(model_choice)
                result = img_model.generate_images(prompt=prompt)
                st.image(result.images[0])
                st.session_state.messages.append({"role": "assistant", "image": result.images[0]})
            else:
                chat_model = genai.GenerativeModel(model_choice)
                # Ensure the session uses the current chosen model
                if "chat_session" not in st.session_state or st.session_state.get("last_model") != model_choice:
                    st.session_state.chat_session = chat_model.start_chat(history=[])
                    st.session_state.last_model = model_choice
                
                response = st.session_state.chat_session.send_message(prompt, stream=True)
                
                def stream_data():
                    for chunk in response:
                        if chunk.text: yield chunk.text
                
                full_text = st.write_stream(stream_data)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
                if supabase:
                    supabase.table("chat_history").insert({"user_message": prompt, "ai_message": full_text}).execute()

        except Exception as e:
            st.warning("⚠️ Access Issue")
            st.info(f"System Message: {str(e)}")