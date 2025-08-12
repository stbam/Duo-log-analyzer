from duo_client.admin import Admin
from dotenv import load_dotenv
import os
import time
from db_store import store_suspicious_log

load_dotenv()
admin_api = Admin(
    ikey=os.getenv("DUO_IKEY"),  # integration key
    skey=os.getenv("DUO_SKEY") ,       # secret key
    host=os.getenv("DUO_HOST")
)

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
        logs = admin_api.get_authentication_log(mintime=last_seen+1)

        #for log in logs:
        

        for log in logs:
            print(log)
            timestamp = log.get("timestamp")
            if timestamp> last_seen:
                last_seen = timestamp 
                print("User:", log.get("username"))
                print("Timestamp:", log.get("timestamp"))
                print("Result:", log.get("result"))
                print("IP:", log.get("ip"))
                print("Device:", log.get("device"))
                print("-" * 40)
                if log.get("result") != "success": 
                    store_suspicious_log(log)
                    print("stored sus log")
            print("time passed")
        time.sleep(60)
    except Exception as e:
        print("error fetching logs: ",e)
        time.sleep(60)

