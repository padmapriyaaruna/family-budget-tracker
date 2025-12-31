"""
AI Chatbot Widget UI Component for Family Budget Tracker
Renders floating action button (FAB) and chat window interface
"""
import streamlit as st
import streamlit.components.v1 as components
from typing import List, Dict
import config
from chatbot_engine import ChatbotEngine


# Initialize chatbot engine
@st.cache_resource
def get_chatbot_engine():
    """Initialize and cache the chatbot engine"""
    try:
        return ChatbotEngine(
            docs_directory=config.CHATBOT_DOCS_DIR,
            api_key=config.GEMINI_API_KEY
        )
    except Exception as e:
        st.error(f"⚠️ Chatbot initialization error: {e}")
        return None


def render_chatbot_widget(db_connection):
    """
    Render the chatbot widget if user is logged in
    
    Args:
        db_connection: Database connection object
    """
    # Only show if logged in and chatbot is enabled
    if not st.session_state.get('logged_in', False) or not config.CHATBOT_ENABLED:
        return
    
    # Check if API key is configured
    if not config.GEMINI_API_KEY:
        # Silently skip if no API key - admin can configure later
        return
    
    user = st.session_state.user
    if not user:
        return
    
    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'chat_expanded' not in st.session_state:
        st.session_state.chat_expanded = False
    
    # Add chatbot CSS and JS
    chatbot_css = """
    <style>
        /* Floating Action Button */
        .chatbot-fab {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 9999;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .chatbot-fab:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        }
        
        .chatbot-fab-icon {
            font-size: 28px;
            line-height: 1;
        }
        
        /* Chat Window */
        .chatbot-window {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 380px;
            height: 550px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            display: flex;
            flex-direction: column;
            z-index: 9998;
            overflow: hidden;
        }
        
        .chatbot-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chatbot-title {
            font-size: 18px;
            font-weight: bold;
            margin: 0;
        }
        
        .chatbot-close {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chatbot-close:hover {
            opacity: 0.8;
        }
        
        .chatbot-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f5f5f5;
        }
        
        .chat-message {
            margin-bottom: 12px;
            display: flex;
            align-items: flex-start;
        }
        
        .chat-message.user {
            justify-content: flex-end;
        }
        
        .chat-message.ai {
            justify-content: flex-start;
        }
        
        .message-bubble {
            max-width: 75%;
            padding: 10px 14px;
            border-radius: 16px;
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
        }
        
        .chat-message.user .message-bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .chat-message.ai .message-bubble {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        
        .chatbot-input-container {
            padding: 12px 16px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .chatbot-loading {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 14px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 16px;
            max-width: 75%;
            font-size: 14px;
            color: #666;
        }
        
        .loading-dots {
            display: flex;
            gap: 4px;
        }
        
        .loading-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #667eea;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        
        .loading-dot:nth-child(1) {
            animation-delay: -0.32s;
        }
        
        .loading-dot:nth-child(2) {
            animation-delay: -0.16s;
        }
        
        @keyframes bounce {
            0%, 80%, 100% {
                transform: scale(0);
            }
            40% {
                transform: scale(1);
            }
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .chatbot-window {
                width: calc(100vw - 20px);
                right: 10px;
                bottom: 90px;
                height: 500px;
            }
            
            .chatbot-fab {
                right: 20px;
                bottom: 20px;
            }
        }
    </style>
    """
    
    st.markdown(chatbot_css, unsafe_allow_html=True)
    
    # Render FAB button
    fab_html = """
    <div class="chatbot-fab" onclick="toggleChat()" id="chatbot-fab">
        <div class="chatbot-fab-icon">🤖</div>
    </div>
    """
    
    # Chat window (conditionally rendered)
    if st.session_state.chat_expanded:
        # Create columns for chat interface
        st.markdown('<div id="chatbot-window-container">', unsafe_allow_html=True)
        
        # Chat window header
        col_header1, col_header2 = st.columns([5, 1])
        with col_header1:
            st.markdown("### 🤖 Budget Assistant")
        with col_header2:
            if st.button("✖", key="close_chat"):
                st.session_state.chat_expanded = False
                st.rerun()
        
        st.divider()
        
        # Messages container
        messages_container = st.container()
        with messages_container:
            if not st.session_state.chat_history:
                st.info("👋 Hi! I'm your Budget Assistant. Ask me about your expenses, income, or how to use this tracker!")
            else:
                for msg in st.session_state.chat_history[-config.MAX_CHAT_HISTORY:]:
                    role = msg['role']
                    content = msg['content']
                    
                    if role == 'user':
                        st.markdown(f"""
                        <div class="chat-message user">
                            <div class="message-bubble">{content}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-message ai">
                            <div class="message-bubble">{content}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Input area
        with st.form(key="chat_input_form", clear_on_submit=True):
            user_input = st.text_input(
                "Ask a question...",
                placeholder="e.g., How much did I spend on groceries?",
                label_visibility="collapsed",
                key="chat_input"
            )
            submit_btn = st.form_submit_button("Send", use_container_width=True)
            
            if submit_btn and user_input.strip():
                # Add user message
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input
                })
                
                # Get chatbot response
                try:
                    chatbot = get_chatbot_engine()
                    if chatbot:
                        # Show loading state
                        with st.spinner("🤔 Thinking..."):
                            response = chatbot.process_query(
                                query=user_input,
                                user_id=user['id'],
                                family_id=user['household_id'],
                                role=user['role'],
                                full_name=user['full_name'],
                                db_connection=db_connection
                            )
                        
                        # Add AI response
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': response
                        })
                    else:
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': "⚠️ Chatbot is currently unavailable. Please check API configuration."
                        })
                except Exception as e:
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': f"⚠️ Error: {str(e)}"
                    })
                
                # Rerun to show new messages
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Render FAB
    components.html(fab_html + """
    <script>
        function toggleChat() {
            // Use Streamlit's setComponentValue to trigger rerun with state change
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: 'toggle_chat'
            }, '*');
        }
    </script>
    """, height=0)
    
    # Handle FAB click (alternative approach using session state)
    if st.button("", key="fab_button_hidden", help="Open Chatbot"):
        st.session_state.chat_expanded = not st.session_state.chat_expanded
        st.rerun()


def render_chatbot_sidebar():
    """Render chatbot toggle in sidebar (alternative placement)"""
    if not st.session_state.get('logged_in', False) or not config.CHATBOT_ENABLED:
        return
    
    with st.sidebar:
        st.divider()
        if st.button("🤖 Budget Assistant", use_container_width=True):
            st.session_state.chat_expanded = not st.session_state.get('chat_expanded', False)
            st.rerun()
