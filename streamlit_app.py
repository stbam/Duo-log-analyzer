import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from twilio.rest import Client

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_store import merge_phone_dashboard, extract_sid

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CLIENT_SID = os.getenv('CLIENT_SID')
ClIENT_TOKEN = os.getenv('ClIENT_TOKEN')
client = Client(CLIENT_SID, ClIENT_TOKEN)

def get_recording_sid(call_sid):
    recordings = client.recordings.list(call_sid=call_sid)
    if recordings:
        return recordings[0].sid
    return None

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "duo_logs.db"))

st.set_page_config(
    page_title="Duo Security System",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Duo Security System")

# Example mapping
role_mapping = {
    "user": "User",
    "bot": "AI Bot",
    "admin": "Admin"
}

# Connect and read database
conn = sqlite3.connect(db_path)
df_logs = pd.read_sql_query("SELECT * FROM suspicious_logs", conn)
df_conv = pd.read_sql_query("SELECT * FROM conversation_messages", conn)
df_sus = pd.read_sql_query("SELECT * from script_decision", conn)
conn.close()

# Create tabs
tab1, tab2, tab4 = st.tabs(["Suspicious Logs", "Conversation", "Script Decision"])

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
    
    # Get all call SIDs upfront and create a mapping
    call_sids = extract_sid()
    print(call_sids)
    call_sid_dict = {}
    for idx, row in enumerate(call_sids):
        call_sid_dict[idx] = row[0]
    
    # Group by conversation_id (i.e., user)
    counter = 0
    for conversation_id, group in df_conv.groupby("conversation_id"):
        username = group["user_name"].iloc[0] if "user_name" in group else "Unknown"
        
        # Skip conversations that don't match the filter
        if user_filter and user_filter.lower() not in conversation_id.lower():
            continue
        
        # Create an expandable box per conversation
        with st.expander(f"Conversation with {username} (Username: {conversation_id})", expanded=False):
            # Combine messages into one string for this conversation
            messages_text = ""
            for _, row in group.iterrows():
                role = role_mapping.get(row.get("role", "Chatbot"), "Chatbot")
                message = row.get("message", "")
                timestamp = row.get("timestamp", "")
                phonenumber = row.get("phone_id")
                messages_text += f"[{timestamp}] {phonenumber} {role}: {message}\n"
            
            # Display in a scrollable text area
            st.text_area(
                f"{conversation_id} - {username} Messages",
                value=messages_text,
                height=250,
                disabled=True
            )
            
            # Get the recording for THIS specific conversation
            print(call_sid_dict)
            if counter < len(call_sid_dict):
                call_sid = call_sid_dict[counter]
                recording_sid = get_recording_sid(call_sid)
                #print(call_sid)
                
                if recording_sid:
                    url = f"https://api.twilio.com/2010-04-01/Accounts/{CLIENT_SID}/Recordings/{recording_sid}.mp3"
                    response = requests.get(url, auth=HTTPBasicAuth(CLIENT_SID, ClIENT_TOKEN))
                    
                    if response.status_code == 200:
                        st.audio(response.content, format="audio/mpeg")
                    else:
                        st.error("Unable to fetch the recording")
                else:
                    st.warning("No recording found for this conversation")
            
            counter += 1

with tab4:
    user_filter = st.text_input("Filter by Decisions", key="decision_filter")
    filtered_logs = df_sus
    if user_filter:
        filtered_logs = df_sus[df_sus['decision'].str.contains(user_filter, case=False)]
    st.dataframe(filtered_logs)