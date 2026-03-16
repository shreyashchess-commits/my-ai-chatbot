import streamlit as st
import google.generativeai as genai

# 1. Page Setup
st.title("🤖 My Personal AI")

# 2. Add your API Key (Replace the text inside the quotes with your real key!)
genai.configure(api_key="AIzaSyBCiuM4hLhPFpVbFk6iK_qlwkSwDaI0ZTc")
model = genai.GenerativeModel('gemini-2.5-flash')

# 3. Setup the Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. The Chat Input Box
if prompt := st.chat_input("Type your message here..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get and show AI response
    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})