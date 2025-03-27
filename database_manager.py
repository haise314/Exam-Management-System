import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='exam_management.db'):
        """
        Initialize the database connection and create tables if they don't exist
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.create_tables()

    def connect(self):
        """Establish a database connection"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Create all necessary tables for the exam management system"""
        self.connect()
        
        # Trainer Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class_assigned TEXT,
            contact_email TEXT,
            hire_date DATE
        )
        ''')

        # Batch Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_year TEXT NOT NULL,
            num_trainees INTEGER,
            training_duration TEXT,
            training_location TEXT,
            trainer_id INTEGER,
            FOREIGN KEY (trainer_id) REFERENCES trainers(id)
        )
        ''')

        # Trainees Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            id_no TEXT UNIQUE,
            uli TEXT,
            batch_year TEXT,
            trainer_name TEXT,
            exams_taken INTEGER DEFAULT 0,
            status TEXT,
            remarks TEXT,
            batch_id INTEGER,
            FOREIGN KEY (batch_id) REFERENCES batches(id)
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_id INTEGER,
            trainer_id INTEGER,
            exam_id INTEGER,
            competency REAL,
            date_taken DATETIME,
            remarks TEXT,
            FOREIGN KEY (trainee_id) REFERENCES trainees(id),
            FOREIGN KEY (trainer_id) REFERENCES trainers(id),
            FOREIGN KEY (exam_id) REFERENCES exams(id)
        )
        ''')

        # Results Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_id INTEGER,
            trainer_id INTEGER,
            exam_id INTEGER,
            competency REAL,
            date_taken DATETIME,
            remarks TEXT,
            FOREIGN KEY (trainee_id) REFERENCES trainees(id),
            FOREIGN KEY (trainer_id) REFERENCES trainers(id),
            FOREIGN KEY (exam_id) REFERENCES exams(id)
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER,
            question_text TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            points INTEGER DEFAULT 1,
            question_type TEXT DEFAULT 'multiple_choice',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (exam_id) REFERENCES exams(id)
        )
        ''')

        self.conn.commit()
        self.close()

    def insert_trainer(self, name, class_assigned, contact_email=None, hire_date=None):
        """Insert a new trainer"""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT INTO trainers (name, class_assigned, contact_email, hire_date)
            VALUES (?, ?, ?, ?)
            ''', (name, class_assigned, contact_email, hire_date))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting trainer: {e}")
            return None
        finally:
            self.close()

    def insert_batch(self, batch_year, num_trainees, training_duration, training_location, trainer_id):
        """Insert a new batch"""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT INTO batches (batch_year, num_trainees, training_duration, training_location, trainer_id)
            VALUES (?, ?, ?, ?, ?)
            ''', (batch_year, num_trainees, training_duration, training_location, trainer_id))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting batch: {e}")
            return None
        finally:
            self.close()

    def insert_trainee(self, name, id_no, uli, batch_year, trainer_name, batch_id, status=None, remarks=None):
        """Insert a new trainee"""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT INTO trainees (name, id_no, uli, batch_year, trainer_name, batch_id, status, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, id_no, uli, batch_year, trainer_name, batch_id, status, remarks))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting trainee: {e}")
            return None
        finally:
            self.close()

    def insert_exam(self, title, module_no, num_items, time_limit, batch_id):
        """Insert a new exam"""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT INTO exams (title, module_no, num_items, time_limit, batch_id)
            VALUES (?, ?, ?, ?, ?)
            ''', (title, module_no, num_items, time_limit, batch_id))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting exam: {e}")
            return None
        finally:
            self.close()

    def insert_result(self, trainee_id, trainer_id, exam_id, competency, date_taken, remarks=None):
        """Insert exam result for a trainee"""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT INTO results (trainee_id, trainer_id, exam_id, competency, date_taken, remarks)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (trainee_id, trainer_id, exam_id, competency, date_taken, remarks))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting result: {e}")
            return None
        finally:
            self.close()

    def get_all_records(self, table_name):
        """Retrieve all records from a specified table"""
        self.connect()
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving records from {table_name}: {e}")
            return []
        finally:
            self.close()

    def update_record(self, table_name, record_id, update_data):
        """Update a record in a specified table"""
        self.connect()
        try:
            # Construct update query dynamically
            set_clause = ', '.join([f"{k} = ?" for k in update_data.keys()])
            values = list(update_data.values()) + [record_id]
            
            self.cursor.execute(f"""
            UPDATE {table_name} 
            SET {set_clause} 
            WHERE id = ?
            """, values)
            
            self.conn.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error updating record in {table_name}: {e}")
            return 0
        finally:
            self.close()

    def delete_record(self, table_name, record_id):
        """Delete a record from a specified table"""
        self.connect()
        try:
            self.cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
            self.conn.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error deleting record from {table_name}: {e}")
            return 0
        finally:
            self.close()
    
    def get_record_by_id(self, table_name, record_id):
        """Retrieve a single record by its ID"""
        self.connect()
        try:
            self.cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (record_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error retrieving record from {table_name}: {e}")
            return None
        finally:
            self.close()

    def insert_record(self, table_name, data):
        """Dynamically insert a record into a specified table"""
        self.connect()
        try:
            # Construct insert query dynamically
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = tuple(data.values())
            
            self.cursor.execute(f"""
            INSERT INTO {table_name} ({columns}) 
            VALUES ({placeholders})
            """, values)
            
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting record into {table_name}: {e}")
            raise
        finally:
            self.close()
            
    def get_available_exams_for_batch(self, batch_id):
        """Retrieve exams available for a specific batch"""
        self.connect()
        try:
            self.cursor.execute("""
                SELECT id, title, module_no, num_items, time_limit 
                FROM exams 
                WHERE batch_id = ?
            """, (batch_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving exams: {e}")
            return []
        finally:
            self.close()

    def get_exam_questions(self, exam_id):
        """Retrieve questions for a specific exam"""
        self.connect()
        try:
            self.cursor.execute("""
                SELECT id, question_text, correct_answer, points 
                FROM questions 
                WHERE exam_id = ?
            """, (exam_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving questions: {e}")
            return []
        finally:
            self.close()

    def submit_exam_result(self, trainee_id, exam_id, score):
        """Record exam result for a trainee"""
        self.connect()
        try:
            self.cursor.execute("""
                INSERT INTO results (trainee_id, exam_id, competency, date_taken)
                VALUES (?, ?, ?, ?)
            """, (trainee_id, exam_id, score, datetime.now()))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error submitting exam result: {e}")
            return None
        finally:
            self.close()