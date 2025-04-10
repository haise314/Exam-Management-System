import sqlite3

conn = sqlite3.connect('exam_management.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM exams")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
