from duo_client.admin import Admin
from dotenv import load_dotenv
import os
import time
from db_store import store_suspicious_log,store_user_name, store_phone_number,get_latest_conversation_id
from rules_based import evaluate_conversation #needed to evaluate a convo and send to duo
from twilio_agent import trigger_ai_prompt,handle_media_stream,get_cookie_or_token
import json
import asyncio


load_dotenv()
admin_api = Admin(
    ikey=os.getenv("DUO_IKEY"),  # integration key
    skey=os.getenv("DUO_SKEY") ,       # secret key
    host=os.getenv("DUO_HOST")
)

device ="347-755-9738" # "856-239-9857" #'347-755-9738'
user_name="bob"
store_phone_number(device)
store_user_name(user_name)

#trigger_ai_prompt(device) # triggers ai prompt from another file
try:
    with open("last_seen.txt", "r") as f:
        last_seen = int(f.read())
except FileNotFoundError:
    last_seen = 0
while True:
    print("Starting log fetch cycle...")
    #print(dir(admin_api)) print lets me see all the commands available for duo logs 
    try:
      #  with open("last_seen.txt", "w") as f:
       #     f.write(str(last_seen))
        logs = admin_api.get_authentication_log(api_version=2,mintime=last_seen+1) #commented out to avoid api trigger
       # with open("log_seen.txt","r") as f:
            #logs= json.load(f)  # must be valid JSON list of dicts

       # with open("log_seen.txt","w") as f:
        #     f.write(str(logs))

        print(logs)
        #for log in logs:
        if isinstance(logs, dict) and "authlogs" in logs:
            log_entries = logs["authlogs"]
        else:
            log_entries = logs  # fallback for v1
        for log in log_entries: #  for log in sample_logs:
            #print(log) 
            user_name = log['user']['name']
            timestamp = log.get("timestamp")
            timestamp=timestamp * 1000
            print(timestamp,"here is time stamp!")
            #print(timestamp)
            print(last_seen,"here is last seen!")
            if timestamp> last_seen:
                last_seen = timestamp 

                user_key = log.get("user", {}).get("key")
                user_name=log.get("user",{}).get("name")
                
                print("here is username!!",user_name)
                print(user_key,"here is key")
                print("User ID:", log.get("user", {}).get("key"))
                #txid = log.get("txid")
                #print("here txid",txid)

              #  device= log.get("device") working 
              #  trigger_ai_prompt(device) 

              
                #admin_api.update_user(user_key, status="active")
               
               # txid = "1c6d04af-9634-456b-a40b-00b6d35e59eb"  # auth event TXID
                #print(user_name,"here user name")
                log_entry={
                    "username":user_name,#log.get("username"),
                    "timestamp":log.get("timestamp")
                }
                #store_suspicious_log(log_entry)
                #print("Stored suspicious log")
                if log.get("result") != "success":  #if result returns a fraud
                    trigger_ai_prompt(device) 
                    conversation_id=None
                    for _ in range(12):
                        time.sleep(5)
                        conversation_id= get_latest_conversation_id(user_name) #this is probably the issue
                        if conversation_id:
                            break
                    
                    print(get_latest_conversation_id(user_name),"here is username!!")

                   # evaluate_conversation(conversation_id,user_key)
                    if conversation_id: #needs to end before evaluate
                        print(f"Conversation found: {conversation_id}")
                        time.sleep(60) #conversation_messages isnt created so lets do this for now as a bandaid
                        evaluate_conversation(conversation_id, user_key)
                    else:
                        print("No conversation found yet, skipping evaluation this cycle.")

                    store_suspicious_log(log)
                    print("stored sus log")
                with open("last_seen.txt", "w") as f:
                    f.write(str(last_seen))
                    

            print("time passed")
        time.sleep(60)
    except Exception as e:
        print("error fetching logs: ",e)
        time.sleep(60)




