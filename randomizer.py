import sqlite3
import random
from datetime import datetime, timedelta

# Users and devices
users = ["alice", "bob", "charlie", "dave", "eve"]
devices = ["iPhone 12", "MacBook Pro", "Windows 10", "iPad", "Linux Laptop"]
results = ["success", "failed"]
emails = [
    "alice.smith@example.com",
    "john.doe@testmail.com",
    "mary.jones@randommail.com",
    "kevin.brown@samplemail.com",
    "emma.wilson@myemail.com",
]
phones = [
    "347-555-1212",
    "646-555-2020",
    "718-555-3434",
    "917-555-4545",
    "212-555-5656",
]

# Connect to DB
conn = sqlite3.connect("duo_logs.db")
cursor = conn.cursor()

# -------------------------------
# Create tables (schema-aligned)
# -------------------------------
cursor.execute('''
CREATE TABLE IF NOT EXISTS suspicious_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    timestamp DATETIME,
    result TEXT,
    ip TEXT,
    device TEXT,
    email TEXT
)
''')

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

cursor.execute('''
CREATE TABLE IF NOT EXISTS phone_number (
    phone_id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE,
    conversation TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS user_name (
    username_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    conversation TEXT
)
''')

# -------------------------------
# Insert phone numbers + usernames
# -------------------------------
for user, phone in zip(users, phones):
    cursor.execute("INSERT OR IGNORE INTO phone_number (phone, conversation) VALUES (?, ?)", (phone, user))
    cursor.execute("INSERT OR IGNORE INTO user_name (username, conversation) VALUES (?, ?)", (user, user))

# -------------------------------
# Generate suspicious logs
# -------------------------------
for _ in range(100):  # 100 logs
    username = random.choice(users)
    timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))  # last 24h
    result = random.choice(results)
    ip = f"192.168.{random.randint(0,255)}.{random.randint(0,255)}"
    device = random.choice(devices)
    email = random.choice(emails)
    cursor.execute('''
        INSERT INTO suspicious_logs (username, timestamp, result, ip, device, email)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, timestamp, result, ip, device, email))

# -------------------------------
# Generate conversation messages
# -------------------------------
sample_messages_user = [
    "I did not authorize this login attempt.",
    "Everything seems fine on my end.",
    "I am seeing repeated login failures.",
    "Please help me with this suspicious activity.",
    "I accidentally pressed the push notification.",
    "I’m not sure what happened, can you check?",
    "Yes, I tried logging in from another device.",
    "No, I did not initiate this login.",
    "I think my account might be compromised.",
    "I received a push I didn’t recognize.",
    "Could someone be trying to hack my account?",
    "I changed my password recently, could that be it?",
    "I’m traveling, could that trigger a security alert?",
    "I don’t remember authorizing this device.",
    "Everything looks normal now, but I’m concerned."
]

sample_messages_bot = [
    "Can you confirm your username?",
    "Can you confirm your email?",
    "Can you confirm your full name?",
    "Was this an accidental push?",
    "If yes, was it caused by spam prompting? Can you describe it?",
]

for user, phone in zip(users, phones):
    num_msgs = random.randint(3, 8)
    for _ in range(num_msgs):
        role = random.choice(["user", "bot"])
        message = random.choice(sample_messages_user if role == "user" else sample_messages_bot)
        conversation_id = f"conv_{user}"
        cursor.execute('''
            INSERT INTO conversation_messages (user_name, conversation_id, role, message, phone_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user, conversation_id, role, message, phone))

# Commit and close
conn.commit()
conn.close()

print("Inserted 100 suspicious logs and sample conversations for users:", users)
