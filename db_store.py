import sqlite3

def store_suspicious_log(log):
    username = log.get("username")
    timestamp = log.get("timestamp")
    result = log.get("result")
    ip = log.get("ip")
    device = log.get("device")

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
                device TEXT
            )
        '''
        )

        # Insert data using regular SQL with placeholders
        cursor.execute('''
            INSERT INTO suspicious_logs (username, timestamp, result, ip, device)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, timestamp, result, ip, device))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Stored suspicious log for user: {username}")

    except Exception as e:
        print(f"Database error: {e}")

def store_user_response(response):
    try:
        conn = sqlite3.connect('duo_logs.db')
        cursor= conn.cursor()
        
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            full_name TEXT,
            accident_push TEXT,
            spam_prompting TEXT,
            suspicious_login TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            '''
        )

        cursor.execute('''
            INSERT INTO responses (username, email, full_name, accident_push, spam_prompting, suspicious_login)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, full_name, accident_push, spam_prompting, suspicious_login))
        conn.commit()
        conn.close()

        
    except Exception as e:
        print(f"Database error: {e}")

def store_message(conversation_id, role, message):
    try:
     conn = sqlite3.connect('duo_logs.db')
     cursor = conn.cursor()
     cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversation_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT,
                        role TEXT,
                        message TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
     sql = "INSERT INTO conversation_messages (conversation_id, role, message) VALUES (?, ?,?)"
     cursor.execute(sql, (conversation_id, role, message))
     conn.commit()
     conn.close()
    except Exception as e:
        print(f"Database error:{e}")
