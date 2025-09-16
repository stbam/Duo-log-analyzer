import sqlite3
import random


def generate_random_ip():
    # IPv4 has 4 octets, each 0-255
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

def store_suspicious_log(log):

    username = log.get('user', {}).get('name', 'UNKNOWN_USER')
    print(username,"in db")
    #username = log.get("username")
    timestamp = log.get("timestamp")
    result = log.get("result")
    ip = generate_random_ip() #log.get("ip")
    device = log.get("device")
    email=log.get("email")

    try:
        conn = sqlite3.connect('duo_logs.db')
        cursor = conn.cursor()

        #Sql table 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suspicious_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                timestamp INTEGER,
                result TEXT,
                ip TEXT,
                device TEXT,
                email TEXT
            )
        '''
        )

        # Insert data using regular SQL with placeholders
        cursor.execute('''
            INSERT INTO suspicious_logs (username, timestamp, result, ip, device,email)
            VALUES (?, ?, ?, ?, ?,?)
        ''', (username, timestamp, result, ip, device,email))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Stored suspicious log for user: {username}")

    except Exception as e:
        print(f"Database error: {e}")



def store_message(user_name,conversation_id, role, message,phone_id):
    print("executed conversation_messages")
    try:
     conn = sqlite3.connect('duo_logs.db')
     cursor = conn.cursor()
     cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name TEXT,
                        conversation_id TEXT,
                        role TEXT,
                        message TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        phone_id TEXT
                    )
                ''')
     sql = "INSERT INTO conversation_messages (user_name,conversation_id, role, message,phone_id) VALUES (?,?, ?,?,?)"
     cursor.execute(sql, (user_name,conversation_id,role, message,phone_id))
     conn.commit()
     conn.close()
    except Exception as e:
        print(f"Database error:{e}")

import sqlite3

def store_phone_number(number, conversation_id=None):
    print("executed phone_number")
    try:
        conn = sqlite3.connect('duo_logs.db')
        cursor = conn.cursor()   
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phone_number (
                phone_id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE,
                conversation TEXT
            )
        ''')     
        # Insert or ignore phone, then update conversation_id if provided
        sql = "INSERT OR IGNORE INTO phone_number (phone, conversation) VALUES (?, ?)"
        cursor.execute(sql, (number, conversation_id))
        
        # If conversation_id provided and row already exists, update it
        if conversation_id:
            cursor.execute(
                "UPDATE phone_number SET conversation = ? WHERE phone = ?",
                (conversation_id, number)
            )    
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")

def store_user_name(username, conversation_id=None):
    print("executed name")
    try:
        conn = sqlite3.connect('duo_logs.db')
        cursor = conn.cursor()   
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_name (
                username_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                conversation TEXT
            )
        ''')     
        # Insert or ignore phone, then update conversation_id if provided
        sql = "INSERT OR IGNORE INTO user_name (username, conversation) VALUES (?, ?)"
        cursor.execute(sql, (username, conversation_id))
        
        # If conversation_id provided and row already exists, update it
        if conversation_id:
            cursor.execute(
                "UPDATE user_name SET conversation = ? WHERE username = ?",
                (conversation_id, username)
            )    
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")




def create_conversation_dashboard_table():
    try:
        conn = sqlite3.connect('duo_logs.db')
        cursor = conn.cursor()

        # Create a merged table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_dashboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                role TEXT,
                message TEXT,
                phone TEXT,
                timestamp DATETIME
            )
        ''')
        conn.commit()
        conn.close()
        print("Conversation dashboard table created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")
      




def merge_phone_dashboard():
    try:
        conn = sqlite3.connect('duo_logs.db')
        cursor = conn.cursor()

        # Drop the view first if it exists
        cursor.execute('DROP VIEW IF EXISTS phone_plus_conversation;')

        # Create the view
        cursor.execute('''
            CREATE VIEW phone_plus_conversation AS
            SELECT 
                cm.conversation_id, 
                cm.role, 
                cm.message, 
                cm.phone_id,
                pn.phone
            FROM conversation_messages cm
            JOIN phone_number pn ON cm.phone_id = pn.phone_id;
        ''')

        conn.commit()
        conn.close()
        print("Dashboard merged successfully.")
    except Exception as e:
        print(f"Error merging dashboard: {e}")




def store_conversation_phone(conversation_id, phone_number):
    """Store the mapping between conversation_id and phone_number"""
    # Your SQL code here
    pass

def update_record_with_conversation_id(phone, conversation_id):
    try:
        conn = sqlite3.connect('duo_logs.db')
        cursor = conn.cursor()
        
        sql = "UPDATE phone_number SET conversation = ? WHERE phone = ?"
        cursor.execute(sql, (conversation_id, phone))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")

# for script decision user conversation_id,name has to be tied to the "store_script_decision" function .
def store_script_decision(conversation_id, matched_keywords, decision):
    try:
        conn = sqlite3.connect('duo_logs.db')
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS script_decision (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                matched_keywords TEXT,
                decision TEXT
            )
        """)

        sql = "INSERT OR IGNORE INTO script_decision (conversation_id, matched_keywords, decision) VALUES (?, ?, ?)"
        cursor.execute(sql, (conversation_id, ", ".join(matched_keywords), decision))

        conn.commit()
        conn.close()
        print(f"Stored script decision for {conversation_id}: {matched_keywords} -> {decision}")

    except Exception as e:
        print(f"Database error: {e}")


def get_latest_conversation_id(user_name):
    """
    Fetch the most recent conversation_id for a given user_name
    from conversation_messages table.
    """
    try:
        conn = sqlite3.connect("duo_logs.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT conversation_id 
            FROM conversation_messages 
            WHERE user_name = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (user_name,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]  # return the conversation_id
        else:
            return None  # user has no messages yet
    except Exception as e:
        print(f"Database error fetching latest conversation: {e}")
        return None