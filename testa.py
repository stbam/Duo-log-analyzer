import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from twilio.rest import Client


# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db_store import merge_phone_dashboard

load_dotenv()
# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CLIENT_SID = os.getenv('CLIENT_SID')
ClIENT_TOKEN=os.getenv('ClIENT_TOKEN')



client = Client(CLIENT_SID,ClIENT_TOKEN)



db_path = os.path.join("..", "duo_logs.db")


st.title("Duo Security System")
# Example mapping
role_mapping = {
    "user": "User",
    "bot": "AI Bot",
    "admin": "Admin"
}
st.set_page_config(
    page_title="Duo Security System",
    layout="wide",      # <-- makes the dashboard stretch full width
    initial_sidebar_state="expanded"
)


# Connect and read database
conn = sqlite3.connect(db_path)
#conn = sqlite3.connect("duo_logs.db")
df_logs = pd.read_sql_query("SELECT * FROM suspicious_logs", conn)
df_conv = pd.read_sql_query("SELECT * FROM conversation_messages", conn)
df_sus = pd.read_sql_query("SELECT * from script_decision",conn)

conn.close()

# Create tabs
tab1, tab2,tab4,  = st.tabs(["Suspicious Logs", "Conversation", "Script Decision"])

# -----------------------------
# Tab 1: Suspicious Logs
# -----------------------------
with tab1:
    user_filter = st.text_input("Filter by Username", key="logs_filter")
    filtered_logs = df_logs
    if user_filter:
        filtered_logs = df_logs[df_logs['username'].str.contains(user_filter, case=False)]
    st.dataframe(filtered_logs)

# -----------------------------
# Tab 2: Conversation
# -----------------------------
with tab2:
    st.subheader("Conversation Messages")
    user_filter = st.text_input("Filter by Username", key="conversation_filter")

    # Group by conversation_id (i.e., user)
    for conversation_id, group in df_conv.groupby("conversation_id"):
        username = group["user_name"].iloc[0] if "user_name" in group else "Unknown"

        # Skip conversations that don't match the filter
        if user_filter and user_filter.lower() not in username.lower():
            continue

        messages_text = ""
        last_sid = None  # store the last SID in this conversation

        for _, row in group.iterrows():
            role = role_mapping.get(row.get("role", "Chatbot"), "Chatbot")
            message = row.get("message", "")
            timestamp = row.get("timestamp", "")
            phone = row.get("phone", "Unknown")
            sid = row.get("SID", None)
            if sid:  # remember the last SID in the conversation
                last_sid = sid

            messages_text += f"[{timestamp}] {phone} {role}: {message}\n"

        # Display conversation messages
        with st.expander(f"Conversation with {username} (ID: {conversation_id})", expanded=False):
            st.text_area(
                f"{conversation_id} - {username} Messages",
                value=messages_text,
                height=250,
                disabled=True
            )

            # Play the Twilio recording for the conversation if SID exists
            if last_sid:
                recording_url = f"https://api.twilio.com/2010-04-01/Accounts/{CLIENT_SID}/Recordings/{last_sid}.mp3"
                response = requests.get(recording_url, auth=HTTPBasicAuth(CLIENT_SID, ClIENT_TOKEN))
                if response.status_code == 200:
                    st.audio(response.content, format="audio/mpeg")
                else:
                    st.warning(f"No recording found for SID: {last_sid}")



with tab4:
    user_filter = st.text_input("Filter by Decisions", key="decision_filter")
    filtered_logs = df_sus
    if user_filter:
        filtered_logs = df_sus[df_sus['decision'].str.contains(user_filter, case=False)]
    st.dataframe(filtered_logs)

