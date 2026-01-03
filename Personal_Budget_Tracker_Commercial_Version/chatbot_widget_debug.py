"""
Simple debug widget to test chatbot visibility
"""
import streamlit as st
import config

def render_chatbot_sidebar_debug():
    """Debug version with visible indicators - VERSION 2.0"""
    # This should ALWAYS show up if function is called
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 CHATBOT DEBUG v2.0")
    st.sidebar.markdown("**If you see this, the function IS being called**")
    
    try:
        st.sidebar.write(f"✅ logged_in: {st.session_state.get('logged_in', False)}")
        st.sidebar.write(f"✅ CHATBOT_ENABLED: {config.CHATBOT_ENABLED}")
        st.sidebar.write(f"✅ API Key exists: {bool(config.GEMINI_API_KEY)}")
        
        if st.session_state.get('logged_in', False):
            st.sidebar.success("✅ User is logged in")
            if config.CHATBOT_ENABLED:
                st.sidebar.success("✅ Chatbot is enabled in config")
            else:
                st.sidebar.error("❌ Chatbot is DISABLED in config.py")
            
            if config.GEMINI_API_KEY:
                st.sidebar.success(f"✅ API key configured (length: {len(config.GEMINI_API_KEY)})")
            else:
                st.sidebar.error("❌ API key is NOT set in environment")
        else:
            st.sidebar.warning("⚠️ User not logged in yet")
    except Exception as e:
        st.sidebar.error(f"❌ Error in debug: {e}")
