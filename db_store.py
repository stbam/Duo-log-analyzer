import sqlite3

def store_suspicious_log(log):
    username = log.get("username: ")
    timestamp = log.get("timestamp:")
    result = log.get("result: ")
    ip = log.get("ip: ")
    device = log.get("device:")

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
        ''')

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
