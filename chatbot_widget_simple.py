"""
Simple working chatbot widget - no complex imports
"""
import streamlit as st

def render_chatbot_sidebar_simple():
    """Simple chatbot button without complex dependencies"""
    
    # Show the button directly
    with st.sidebar:
        st.divider()
        st.markdown("### 🤖 Budget Assistant")
        
        if st.button("💬 Open Chat", use_container_width=True, key="open_chat_btn"):
            st.session_state.chat_expanded = not st.session_state.get('chat_expanded', False)
        
        # Show chat interface if expanded
        if st.session_state.get('chat_expanded', False):
            st.markdown("---")
            st.markdown("#### Chat Interface")
            
            # Simple chat UI
            user_input = st.text_input("Ask a question:", key="chat_input_simple")
            
            if st.button("Send", key="send_btn"):
                if user_input:
                    st.info(f"You asked: {user_input}")
                    st.warning("⚠️ Full chatbot functionality coming soon!")
                    st.write("For now, this proves the UI works.")
                    st.write("Next step: Connect to chatbot engine.")
            
            if st.button("Close Chat", key="close_chat_btn"):
                st.session_state.chat_expanded = False
                st.rerun()
