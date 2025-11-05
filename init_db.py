import sqlite3

def init_suspicious_logs():
    conn = sqlite3.connect('duo_logs.db')
    cursor = conn.cursor()
    try:
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
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

def init_conversation_logs():
    conn = sqlite3.connect('duo_logs.db')
    cursor= conn.cursor()
    try:
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
        conn.commit()
        conn.close()
    except Exception as e :
         print(f"Database error: {e}")

def store_script_decision():
    try:
        conn = sqlite3.connect('duo_logs.db')
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS script_decision (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT UNIQUE,
                matched_keywords TEXT,
                decision TEXT
            )
        """)
        
        conn.commit()
    except Exception as e :
         print(f"Database error: {e}")

    
if __name__ == "__main__":
    init_suspicious_logs()
    init_conversation_logs()
    store_script_decision()