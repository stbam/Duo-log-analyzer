import sqlite3
from db_store import store_script_decision
from dotenv import load_dotenv
import os
from duo_client.admin import Admin

load_dotenv()
admin_api = Admin(
    ikey=os.getenv("DUO_IKEY"),  # integration key
    skey=os.getenv("DUO_SKEY") ,       # secret key
    host=os.getenv("DUO_HOST")
)

# --- rule-based decision engine ---
fraud_indicators = [
    "i did not authorize",
    "this was not me",
    "suspicious activity",
    "keep getting pushes",
    "repeated login failures",
    "unknown device",
    "strange login",
    "hacker",
]

safe_indicators = [
    "it was me",
    "i pressed by accident",
    "everything is fine",
    "all good",
    "authorized",
    "legit"
]

decision=None
def extract_keywords_and_decision(user_messages):
    """Return a list of matched keywords and the decision"""
    msg_text = " ".join(user_messages).lower()
    matched_keywords = []

    for phrase in fraud_indicators + safe_indicators:
        if phrase in msg_text:
            matched_keywords.append(phrase)

    # Determine decision based on matched keywords
    if any(k in fraud_indicators for k in matched_keywords):
        decision = "lockout"
    elif any(k in safe_indicators for k in matched_keywords):
        decision = "safe"
    else:
        decision = "escalate"

    return matched_keywords, decision


def evaluate_conversation(conversation_id,user_key):
    decision = conversation_id #evaluate_conversation(conversation_id) #"conv_CGUoUnraTNG2HbCeeDDXP"
    try:

        """Fetch user messages from DB, extract keywords and decision, store in DB"""
        conn = sqlite3.connect("duo_logs.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT message FROM conversation_messages WHERE conversation_id = ? AND role = 'user'",
            (conversation_id,)
        )
        rows = cur.fetchall()
        conn.close()

        user_messages = [r[0] for r in rows]
        print("User messages:", user_messages)

        matched_keywords, decision = extract_keywords_and_decision(user_messages)
        
        # Store in DB
        store_script_decision(conversation_id, matched_keywords, decision)

        print("Matched keywords:", matched_keywords)
        print("Decision:", decision)

        if decision == "lockout":
            print(user_key,"in rules_based.py")
            admin_api.update_user(user_key, status="disabled") #active
            print("Lock account via Duo API")
        elif decision == "safe":
            admin_api.update_user(user_key, status="active") #disabled
            print("User safe, no lock")
        else:
            print("Escalate to human analyst")


        return decision
    except Exception as e:
        print(f"Database Error: {e}")

    


# --- usage example ---

if decision == "lockout":
    #admin_api.update_user(user_key, status="disabled") #active
    print("Lock account via Duo API")
elif decision == "safe":
   # admin_api.update_user(user_key, status="active") #disabled
    print("User safe, no lock")
else:
    print("Escalate to human analyst")
