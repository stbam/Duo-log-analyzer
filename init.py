from duo_client.admin import Admin
from dotenv import load_dotenv
import os
import time
from db_store import store_suspicious_log
from twilio_agent import trigger_ai_prompt

sample_logs = [
    {
        "username": "alice",
        "timestamp": 1756060999,
        "result": "FRAUD",
        "ip": "192.168.1.10",
        "device": "iPhone"
    },
    {
        "username": "bob",
        "timestamp": 1756061999,
        "result": "SUCCESS",
        "ip": "74.89.43.241",
        "device": "MacBook Pro"
    },
    {
        "username": "charlie",
        "timestamp": 1756062999,
        "result": "FRAUD",
        "ip": "10.0.0.5",
        "device": "Windows Laptop"
    }
]


load_dotenv()
admin_api = Admin(
    ikey=os.getenv("DUO_IKEY"),  # integration key
    skey=os.getenv("DUO_SKEY") ,       # secret key
    host=os.getenv("DUO_HOST")
)
trigger_ai_prompt() # triggers ai prompt from another file
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
        #for log in logs:
        for log in logs: #  for log in sample_logs:
            
           # print(log) 
            timestamp = log.get("timestamp")
            if timestamp> last_seen:
                last_seen = timestamp 
                print("User:", log.get("username"))
                print("Timestamp:", log.get("timestamp"))
                print("Result:", log.get("result"))
                print("IP:", log.get("ip"))
                print("Device:", log.get("device"))
                print("-" * 40)
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

log_entry = {
    "username": "alice",
    "timestamp": "",
    "result": "failed",
    "ip": "192.168.1.10",
    "device": "iPhone"
}