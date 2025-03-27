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
            contact_email TEXT UNIQUE,
            hire_date DATE NOT NULL
        )
        ''')

        # Batch Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_year TEXT NOT NULL,
            num_trainees INTEGER CHECK (num_trainees >= 0),
            training_duration TEXT NOT NULL,
            training_location TEXT,
            trainer_id INTEGER,
            FOREIGN KEY (trainer_id) REFERENCES trainers(id) ON DELETE SET NULL
        )
        ''')

        # Trainees Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            id_no TEXT UNIQUE NOT NULL,
            uli TEXT UNIQUE,
            batch_year TEXT NOT NULL,
            trainer_name TEXT,
            exams_taken INTEGER DEFAULT 0,
            status TEXT CHECK (status IN ('Active', 'Inactive', 'Completed')),
            remarks TEXT,
            batch_id INTEGER,
            FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE SET NULL
        )
        ''')

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_id INTEGER NOT NULL,
            exam_id INTEGER NOT NULL,
            score INTEGER NOT NULL CHECK (score >= 0),
            total_items INTEGER NOT NULL CHECK (total_items > 0),
            percentage REAL GENERATED ALWAYS AS (CAST(score AS REAL) / total_items * 100) STORED,
            date_taken DATETIME DEFAULT CURRENT_TIMESTAMP,
            time_spent INTEGER CHECK (time_spent > 0),
            status TEXT CHECK (status IN ('Passed', 'Failed')),
            FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE,
            FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
            UNIQUE(trainee_id, exam_id)
        )
        """)
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
            points INTEGER DEFAULT 1 CHECK (points > 0),
            FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            module_no TEXT NOT NULL,
            num_items INTEGER NOT NULL CHECK (num_items > 0),
            time_limit INTEGER NOT NULL CHECK (time_limit > 0),
            batch_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive')),
            FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
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

    def submit_exam_result(self, trainee_id, exam_id, answers, time_spent):
        """Submit exam results and calculate score"""
        self.connect()
        try:
            # Get correct answers and calculate score
            self.cursor.execute("""
                SELECT id, correct_answer, points
                FROM questions
                WHERE exam_id = ?
            """, (exam_id,))
            questions = self.cursor.fetchall()
            
            total_points = sum(q[2] for q in questions)
            score = sum(
                q[2] for q in questions 
                if str(answers.get(q[0])) == q[1]
            )
            
            # Insert result
            self.cursor.execute("""
                INSERT INTO results (
                    trainee_id, exam_id, score, total_items,
                    time_spent, date_taken, status
                ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP,
                    CASE WHEN CAST(? AS FLOAT) / ? >= 0.75 THEN 'Passed' ELSE 'Failed' END
                )
            """, (trainee_id, exam_id, score, total_points, time_spent, score, total_points))
            
            self.conn.commit()
            
            return {
                'score': score,
                'total_items': total_points,
                'percentage': (score / total_points) * 100
            }
        finally:
            self.close()

    def get_available_exams(self, trainee_id):
        """Get exams available for a trainee that haven't been taken yet"""
        self.connect()
        try:
            self.cursor.execute("""
                SELECT e.id, e.title, e.module_no, e.num_items, e.time_limit,
                    CASE 
                        WHEN r.id IS NULL THEN 'Not Taken'
                        ELSE 'Completed'
                    END as status
                FROM exams e
                LEFT JOIN results r ON e.id = r.exam_id AND r.trainee_id = ?
                WHERE e.batch_id = (
                    SELECT batch_id FROM trainees WHERE id = ?
                )
            """, (trainee_id, trainee_id))
            
            columns = ['id', 'title', 'module_no', 'num_items', 'time_limit', 'status']
            results = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            return results
        except sqlite3.Error as e:
            print(f"Error getting available exams: {e}")
            return []
        finally:
            self.close()

    def add_question(self, exam_id, question_text, options, correct_answer, points=1):
        """Add a multiple choice question to an exam"""
        self.connect()
        try:
            self.cursor.execute('''
            INSERT INTO questions (
                exam_id, question_text, option_a, option_b, 
                option_c, option_d, correct_answer, points
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                exam_id, question_text, 
                options['A'], options['B'], options['C'], options['D'],
                correct_answer, points
            ))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding question: {e}")
            return None
        finally:
            self.close()

    def get_exam_details(self, exam_id):
        """Get detailed exam information"""
        self.connect()
        try:
            self.cursor.execute("""
                SELECT id, title, module_no, num_items, time_limit, status
                FROM exams
                WHERE id = ? AND status = 'Active'
            """, (exam_id,))
            columns = ['id', 'title', 'module_no', 'num_items', 'time_limit', 'status']
            result = self.cursor.fetchone()
            return dict(zip(columns, result)) if result else None
        finally:
            self.close()

    def has_taken_exam(self, trainee_id, exam_id):
        """Check if trainee has already taken an exam"""
        self.connect()
        try:
            self.cursor.execute("""
                SELECT 1 FROM results 
                WHERE trainee_id = ? AND exam_id = ?
            """, (trainee_id, exam_id))
            return bool(self.cursor.fetchone())
        finally:
            self.close()

    def get_trainee_results(self, trainee_id):
        """Get exam results for a specific trainee"""
        self.connect()
        try:
            self.cursor.execute("""
                SELECT 
                    e.title,
                    r.score,
                    r.total_items,
                    r.percentage,
                    r.date_taken,
                    r.time_spent,
                    r.status
                FROM results r
                JOIN exams e ON r.exam_id = e.id
                WHERE r.trainee_id = ?
                ORDER BY r.date_taken DESC
            """, (trainee_id,))
            columns = ['exam_title', 'score', 'total_items', 'percentage', 
                      'date_taken', 'time_spent', 'status']
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        finally:
            self.close()