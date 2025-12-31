"""
Simple debug widget to test chatbot visibility
"""
import streamlit as st
import config

def render_chatbot_sidebar_debug():
    """Debug version with visible indicators"""
    with st.sidebar:
        st.write("🔍 **Chatbot Debug Info:**")
        st.write(f"- logged_in: {st.session_state.get('logged_in', False)}")
        st.write(f"- CHATBOT_ENABLED: {config.CHATBOT_ENABLED}")
        st.write(f"- API Key exists: {bool(config.GEMINI_API_KEY)}")
        
        if st.session_state.get('logged_in', False):
            st.success("✅ User is logged in")
            if config.CHATBOT_ENABLED:
                st.success("✅ Chatbot is enabled in config")
            else:
                st.error("❌ Chatbot is disabled in config")
            
            if config.GEMINI_API_KEY:
                st.success("✅ API key is configured")
            else:
                st.error("❌ API key is NOT configured")
        else:
            st.warning("⚠️ User not logged in yet")
