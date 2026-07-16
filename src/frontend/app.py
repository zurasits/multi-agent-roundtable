import streamlit as st
import sys
import os
import uuid

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.backend.orchestrator import get_agents, get_messages, submit_message, trigger_roundtable_step, get_next_agent
from src.backend.demo_loader import load_demo_transcript

# Page Configuration
st.set_page_config(
    page_title="Multi-Agent Roundtable",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for rich aesthetics (Glassmorphism & SLEEK layouts)
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #262730;
        color: white;
        border-radius: 8px;
        border: 1px solid #4a4a4a;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff4b4b;
        color: white;
        border-color: #ff4b4b;
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.4);
    }
    .agent-card {
        padding: 10px;
        border-radius: 10px;
        background-color: #1e222b;
        border: 1px solid #2e3440;
        margin-bottom: 10px;
    }
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
        greeting = f"Hallo! Ich bin {alice.name} ({alice.role}). Welches Thema sollen wir heute diskutieren?"
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
    st.sidebar.markdown(
        f"""
        <div class="agent-card">
            <strong>👤 {agent.name}</strong><br>
            <small style="color: #888888;">Role: {agent.role}</small>
        </div>
        """,
        unsafe_allow_html=True
    )

st.sidebar.subheader("Session Metadata")
st.sidebar.info(f"**Session ID:**\n`{st.session_state.session_id}`")

# Sidebar Controls
st.sidebar.subheader("Controls")
if "live_mode" not in st.session_state:
    st.session_state.live_mode = True

new_live_mode = st.sidebar.toggle("Live KI-Modus (Gemini)", value=st.session_state.live_mode, help="Schaltet um zwischen lokaler Demo und echter KI-Generierung via Google Gemini.")

if new_live_mode != st.session_state.live_mode:
    st.session_state.live_mode = new_live_mode
    # Reset discussion when mode changes
    st.session_state.session_id = str(uuid.uuid4())
    
    if new_live_mode:
        sorted_agents = sorted(agents, key=lambda a: a.name)
        if sorted_agents:
            alice = sorted_agents[0]
            greeting = f"Hallo! Ich bin {alice.name} ({alice.role}). Welches Thema sollen wir heute diskutieren?"
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
            greeting = f"Hallo! Ich bin {alice.name} ({alice.role}). Welches Thema sollen wir heute diskutieren?"
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
    
    # Predict who will answer next to personalize the spinner
    next_agent = get_next_agent(st.session_state.session_id, is_user_reply)
    if next_agent:
        spinner_text = f"🤖 {next_agent.role} {next_agent.name} denkt nach..."
    else:
        spinner_text = "🤖 Ein Agent denkt nach..."
        
    with st.spinner(spinner_text):
        trigger_roundtable_step(st.session_state.session_id, live_mode=live_mode, is_user_reply=is_user_reply)
    st.rerun()

user_input = st.chat_input("Type a message to inject into the roundtable...")
if user_input:
    submit_message(st.session_state.session_id, "live_user", user_input)
    # Tell Streamlit to trigger the agent AFTER drawing the user message on the next run
    st.session_state.pending_agent_step = True
    st.session_state.is_user_reply = True
    st.rerun()
