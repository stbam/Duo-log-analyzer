import sqlite3

def store_suspicious_log(log):
    username = log.get("username")
    timestamp = log.get("timestamp")
    result = log.get("result")
    ip = log.get("ip")
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



def store_message(conversation_id, role, message,phone_id):
    print("executed conversation_messages")
    try:
     conn = sqlite3.connect('duo_logs.db')
     cursor = conn.cursor()
     cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT,
                        role TEXT,
                        message TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        phone_id TEXT ,
                        FOREIGN KEY (phone_id) REFERENCES phone_number(phone_id)
                    )
                ''')
     sql = "INSERT INTO conversation_messages (conversation_id, role, message,phone_id) VALUES (?, ?,?,?)"
     cursor.execute(sql, (conversation_id, role, message,phone_id))
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
