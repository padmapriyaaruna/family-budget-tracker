"""Ultra-minimal chatbot widget"""
import streamlit as st

def render_chatbot_sidebar_simple():
    """Minimal chatbot button"""
    st.sidebar.write("🤖 **Budget Assistant**")
    st.sidebar.button("Open Chat", key="chat_btn_minimal")
