import streamlit as st
import sys
import os
import uuid

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.backend.orchestrator import get_agents, get_messages, submit_message, trigger_roundtable_step, get_next_agent, transcribe_audio_to_text
from src.backend.demo_loader import load_demo_transcript
from src.backend.db import update_agent_provider

# Page Configuration
st.set_page_config(
    page_title="Multi-Agent Roundtable",
    page_icon="🤖",
    layout="wide"
)

import time

# Custom CSS for rich aesthetics
st.markdown(f"""
<style>
    /* Cache Buster: {time.time()} */
    
    /* NUCLEAR OPTION: Force ALL inner divs of the selectbox to be transparent */
    .stSelectbox div, 
    [data-testid="stSelectbox"] div {{
        background-color: transparent !important;
        border-color: transparent !important;
    }}
    
    /* NUCLEAR OPTION: Kill the red focus ring on ALL states and ALL child elements */
    .stSelectbox div:focus,
    .stSelectbox div:active,
    .stSelectbox div:hover,
    .stSelectbox div:focus-within,
    [data-testid="stSelectbox"] div:focus,
    [data-testid="stSelectbox"] div:active,
    [data-testid="stSelectbox"] div:hover,
    [data-testid="stSelectbox"] div:focus-within {{
        box-shadow: none !important;
        border-color: transparent !important;
        outline: none !important;
    }}
    
    /* 
       ABSOLUTE ULTIMATE POPOVER OVERRIDE:
       Targeting every possible class, role, and testid used by any version of Streamlit
       for the selectbox dropdown menu to force it to #262730 (agent-card grey).
    */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"],
    div[role="listbox"],
    [data-testid="stSelectboxVirtualDropdown"] {{
        background-color: #262730 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    
    /* Strip all inner backgrounds that might override it */
    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"] *,
    ul[role="listbox"] *,
    div[role="listbox"] *,
    [data-testid="stSelectboxVirtualDropdown"] * {{
        background-color: transparent !important;
    }}
    
    /* Hover effect: explicitly DARKER background ONLY for the hovered option */
    [role="option"]:hover,
    [role="option"]:hover * {{
        background-color: #111115 !important;
        cursor: pointer !important;
    }}
</style>
""", unsafe_allow_html=True)

# Generate or retrieve session ID and initialize state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.live_mode = True  # Default to Live Mode
    
    # Inject an automatic welcome message from Alice
    agents_for_init = get_agents()
    sorted_agents = sorted(agents_for_init, key=lambda a: a.name)
    if sorted_agents:
        alice = sorted_agents[0]
        greeting = f"Hello! I am {alice.name} ({alice.role}). What topic should we discuss today?"
        submit_message(st.session_state.session_id, alice.id, greeting)

# Header Section
st.title("🤖 Multi-Agent Roundtable")
st.markdown("*A secure, isolated collaborative workspace for autonomous intelligence.*")
st.divider()

# Get agents & build fast O(1) lookup dictionary
agents = get_agents()
agents_dict = {agent.id: agent for agent in agents}

# Sidebar - Participating Agents & Details
st.sidebar.header("Participating Agents")
for agent in agents:
    with st.sidebar.container(border=True):
        st.markdown(
            f"**👤 {agent.name}**<br><small style='color: #888888;'>Role: {agent.role}</small>",
            unsafe_allow_html=True
        )
        
        provider_options = ["gemini", "gpt", "claude"]
        # Handle case where llm_provider might not be in the list
        current_index = provider_options.index(agent.llm_provider) if agent.llm_provider in provider_options else 0
        
        new_provider = st.selectbox(
            f"LLM", 
            provider_options, 
            index=current_index,
            key=f"llm_sel_{agent.id}",
            label_visibility="collapsed"
        )
        
        if new_provider != agent.llm_provider:
            update_agent_provider(agent.id, new_provider)
            st.rerun()


# Sidebar Controls
st.sidebar.subheader("Controls")
if "live_mode" not in st.session_state:
    st.session_state.live_mode = True

new_live_mode = st.sidebar.toggle("Live AI Mode (Gemini)", value=st.session_state.live_mode, help="Toggles between local demo and real AI generation via Google Gemini.")

if new_live_mode != st.session_state.live_mode:
    st.session_state.live_mode = new_live_mode
    # Reset discussion when mode changes
    st.session_state.session_id = str(uuid.uuid4())
    
    if new_live_mode:
        sorted_agents = sorted(agents, key=lambda a: a.name)
        if sorted_agents:
            alice = sorted_agents[0]
            greeting = f"Hello! I am {alice.name} ({alice.role}). What topic should we discuss today?"
            submit_message(st.session_state.session_id, alice.id, greeting)
    else:
        demo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../demo_data/transcript_001.json")
        load_demo_transcript(st.session_state.session_id, demo_path)
        
    st.rerun()

live_mode = st.session_state.live_mode

if st.sidebar.button("Trigger Next Agent Turn"):
    st.session_state.pending_agent_step = True
    st.session_state.is_user_reply = False
    st.rerun()

if st.sidebar.button("Reset Discussion"):
    # Regenerate session ID to get a fresh discussion state
    st.session_state.session_id = str(uuid.uuid4())
    
    if live_mode:
        # Inject an automatic welcome message from Alice (the first agent)
        sorted_agents = sorted(agents, key=lambda a: a.name)
        if sorted_agents:
            alice = sorted_agents[0]
            greeting = f"Hello! I am {alice.name} ({alice.role}). What topic should we discuss today?"
            submit_message(st.session_state.session_id, alice.id, greeting)
    else:
        demo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../demo_data/transcript_001.json")
        load_demo_transcript(st.session_state.session_id, demo_path)
        
    st.rerun()

# Discussion transcript
st.subheader("Discussion Transcript")

messages = get_messages(st.session_state.session_id)

if not messages:
    st.info("No messages in this session yet. Inject a message or trigger an agent step to start.")
else:
    for msg in messages:
        agent = agents_dict.get(msg.agent_id)
        is_user = msg.agent_id == "live_user"
        
        name = "User" if is_user else (agent.name if agent else "System Agent")
        avatar = "👤" if is_user else "🤖"
        
        with st.chat_message("user" if is_user else "assistant", avatar=avatar):
            # Escaping the message input text slightly to prevent HTML execution (keeping Markdown safe)
            clean_content = msg.content.replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(f"**{name}**: {clean_content}")

# Message Injection
# Place the auto-trigger logic here, right before chat input, but after drawing messages
if st.session_state.get("pending_agent_step", False):
    is_user_reply = st.session_state.get("is_user_reply", False)
    st.session_state.pending_agent_step = False
    st.session_state.is_user_reply = False
    
    # Predict next agent for spinner
    next_agent = get_next_agent(st.session_state.session_id, is_user_reply)
    if next_agent:
        spinner_text = f"🤖 {next_agent.role} {next_agent.name} is thinking..."
    else:
        spinner_text = "🤖 An agent is thinking..."
        
    with st.spinner(spinner_text):
        trigger_roundtable_step(st.session_state.session_id, live_mode=live_mode, is_user_reply=is_user_reply)
    st.rerun()

if "draft_audio_text" not in st.session_state:
    st.session_state.draft_audio_text = None

if st.session_state.draft_audio_text is not None:
    with st.container(border=True):
        st.markdown("**🎤 Audio Transkription prüfen:**")
        edited_text = st.text_area("Korrigiere den Text falls nötig:", value=st.session_state.draft_audio_text, height=100)
        
        col1, col2, col3 = st.columns([2, 2, 6])
        with col1:
            if st.button("Senden", type="primary", use_container_width=True):
                submit_message(st.session_state.session_id, "live_user", edited_text)
                st.session_state.draft_audio_text = None
                st.session_state.pending_agent_step = True
                st.session_state.is_user_reply = True
                st.rerun()
        with col2:
            if st.button("Verwerfen", use_container_width=True):
                st.session_state.draft_audio_text = None
                st.rerun()
else:
    user_input = st.chat_input("Type or record a message...", accept_audio=True)
    if user_input:
        message_text = None
        is_audio = False
        
        # Check if user_input is a string (text) or an audio file (bytes/file-like object)
        if isinstance(user_input, str):
            message_text = user_input
        else:
            # It is a ChatInputValue object
            text_content = getattr(user_input, "text", None) or (user_input.get("text") if hasattr(user_input, "get") else None)
            audio_content = getattr(user_input, "audio", None) or (user_input.get("audio") if hasattr(user_input, "get") else None)
            
            if audio_content:
                is_audio = True
                with st.spinner("🎙️ Transcribing audio..."):
                    audio_bytes = audio_content.read() if hasattr(audio_content, "read") else audio_content
                    message_text = transcribe_audio_to_text(audio_bytes)
                    
                if message_text.startswith("[System"):
                    st.error(message_text)
                    st.stop()
            elif text_content:
                message_text = text_content

        if message_text:
            if is_audio:
                st.session_state.draft_audio_text = message_text
                st.rerun()
            else:
                submit_message(st.session_state.session_id, "live_user", message_text)
                # Tell Streamlit to trigger the agent AFTER drawing the user message on the next run
                st.session_state.pending_agent_step = True
                st.session_state.is_user_reply = True
                st.rerun()



