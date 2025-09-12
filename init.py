from duo_client.admin import Admin
from dotenv import load_dotenv
import os
import time
from db_store import store_suspicious_log
from twilio_agent import trigger_ai_prompt,handle_media_stream,get_cookie_or_token
import json


load_dotenv()
admin_api = Admin(
    ikey=os.getenv("DUO_IKEY"),  # integration key
    skey=os.getenv("DUO_SKEY") ,       # secret key
    host=os.getenv("DUO_HOST")
)
device = '347-755-9738'


trigger_ai_prompt(device) # triggers ai prompt from another file
#get_cookie_or_token(device,device)
#handle_media_stream(device)
#last_seen= 0 
try:
    with open("last_seen.txt", "r") as f:
        last_seen = int(f.read())
except FileNotFoundError:
    last_seen = 0
while True:
    print("Starting log fetch cycle...")
    #print(dir(admin_api)) print lets me see all the commands available for duo logs 
    try:
        with open("last_seen.txt", "w") as f:
            f.write(str(last_seen))
        logs = admin_api.get_authentication_log(mintime=last_seen+1) #commented out to avoid api trigger
       # with open("log_seen.txt","r") as f:
            #logs= json.load(f)  # must be valid JSON list of dicts

       # with open("log_seen.txt","w") as f:
        #     f.write(str(logs))

      #  print(logs)
        #for log in logs:
        for log in logs: #  for log in sample_logs:
            
            print(log) 
            timestamp = log.get("timestamp")
            #print(timestamp)
            if timestamp> last_seen:
                last_seen = timestamp 
                print("User:", log.get("username"))
                print("Timestamp:", log.get("timestamp"))
                print("Result:", log.get("result"))
                print("IP:", log.get("ip"))
                print("Device:", log.get("device"))
                print("Email:", log.get("email"))
                print("Factor:", log.get("factor"))
                print("Integration:", log.get("integration"))
                print("ISO Timestamp:", log.get("isotimestamp"))
                print("Reason:", log.get("reason"))
                print("Event Type:", log.get("eventtype"))
                print("Host:", log.get("host"))
                print("Alias:", log.get("alias"))
                print("New Enrollment:", log.get("new_enrollment"))
                print("OOD Software:", log.get("ood_software"))
                print("-" * 40)


              #  device= log.get("device") working 
              #  trigger_ai_prompt(device) 


                log_entry={
                    "username":log.get("username"),
                    "timestamp":log.get("timestamp")
                }
                store_suspicious_log(log_entry)
                print("Stored suspicious log")
                if log.get("result") != "success": 
                    store_suspicious_log(log)
                    print("stored sus log")
                    
            print("time passed")
        time.sleep(60)
    except Exception as e:
        print("error fetching logs: ",e)
        time.sleep(60)





