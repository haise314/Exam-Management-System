import sqlite3
from datetime import datetime

class ExamManager:
    def __init__(self, db_name='exam_management.db'):
        self.db_name = db_name
        self.connect()
        self.create_tables()

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Ensures all necessary tables exist."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            module_no TEXT,
            num_items INTEGER,
            time_limit INTEGER,
            batch_id INTEGER,
            FOREIGN KEY (batch_id) REFERENCES batches(id)
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER,
            question_text TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            points INTEGER DEFAULT 1,
            FOREIGN KEY (exam_id) REFERENCES exams(id)
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_id INTEGER,
            exam_id INTEGER,
            score REAL,
            date_taken DATETIME,
            FOREIGN KEY (trainee_id) REFERENCES trainees(id),
            FOREIGN KEY (exam_id) REFERENCES exams(id)
        )
        ''')
        self.conn.commit()

    def add_exam(self, title, module_no, num_items, time_limit, batch_id):
        """Creates a new exam."""
        self.cursor.execute('''
        INSERT INTO exams (title, module_no, num_items, time_limit, batch_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (title, module_no, num_items, time_limit, batch_id))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_exams(self):
        """Retrieves all exams."""
        self.cursor.execute("SELECT * FROM exams")
        return self.cursor.fetchall()

    def delete_exam(self, exam_id):
        """Deletes an exam by ID."""
        self.cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
        self.conn.commit()

    def record_result(self, trainee_id, exam_id, score):
        """Stores the exam result."""
        self.cursor.execute('''
        INSERT INTO results (trainee_id, exam_id, score, date_taken)
        VALUES (?, ?, ?, ?)
        ''', (trainee_id, exam_id, score, datetime.now()))
        self.conn.commit()

    def update_exam(self, exam_id, title, module_no, num_items, time_limit, batch_id):
        """Updates an existing exam."""
        self.cursor.execute('''
        UPDATE exams
        SET title = ?, module_no = ?, num_items = ?, time_limit = ?, batch_id = ?
        WHERE id = ?
        ''', (title, module_no, num_items, time_limit, batch_id, exam_id))
        self.conn.commit()

    def get_exam_by_id(self, exam_id):
        """Retrieve a single exam by ID."""
        self.cursor.execute("SELECT * FROM exams WHERE id = ?", (exam_id,))
        return self.cursor.fetchone()

    def get_exam_questions(self, exam_id):
        """Retrieve all questions for a given exam."""
        self.cursor.execute("SELECT id, question_text, correct_answer, points FROM questions WHERE exam_id = ?", (exam_id,))
        return self.cursor.fetchall()

    def submit_exam(self, trainee_id, exam_id, answers):
        """Process and store exam results."""
        questions = self.get_exam_questions(exam_id)
        total_score = 0
        for question in questions:
            question_id, question_text, correct_answer, points = question
            if answers.get(question_id) == correct_answer:
                total_score += points
        self.record_result(trainee_id, exam_id, total_score)

