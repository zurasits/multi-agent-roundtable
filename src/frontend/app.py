import streamlit as st
import sys
import os

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.backend.orchestrator import get_agents, get_messages, submit_message, trigger_roundtable_step

st.set_page_config(page_title="Multi-Agent Roundtable", layout="wide")
st.title("Multi-Agent Roundtable")

agents = get_agents()
st.sidebar.header("Participating Agents")
for agent in agents:
    st.sidebar.markdown(f"**{agent.name}** - *{agent.role}*")

messages = get_messages()
st.subheader("Discussion Transcript")

for msg in messages:
    agent_name = next((a.name for a in agents if a.id == msg.agent_id), "User")
    is_user = msg.agent_id == "live_user"
    with st.chat_message("user" if is_user else "assistant"):
        st.markdown(f"**{agent_name}**: {msg.content}")

st.sidebar.subheader("Controls")
if st.sidebar.button("Trigger Agent Step"):
    trigger_roundtable_step()
    st.rerun()

user_input = st.chat_input("Inject a message as live_user...")
if user_input:
    submit_message("live_user", user_input)
    st.rerun()
