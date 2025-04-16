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
        self.migrate_schema()  # Ensure schema is up-to-date

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
        print("Creating tables...")  # Debug print
        
        # Trainers Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class_assigned TEXT,
            contact_email TEXT UNIQUE,
            hire_date DATE NOT NULL
        )
        ''')

        # Batches Table
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
            batch_id INTEGER NOT NULL,
            batch_year INTEGER NOT NULL,
            exams_taken INTEGER DEFAULT 0,
            status TEXT CHECK (status IN ('Active', 'Inactive', 'Completed')),
            remarks TEXT,
            FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
        )
        ''')

        # Exams Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            module_no TEXT NOT NULL,
            num_items INTEGER NOT NULL CHECK (num_items > 0),
            time_limit INTEGER NOT NULL CHECK (time_limit > 0),
            batch_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive')),
            FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE
        )
        ''')

        # Questions Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            correct_answer TEXT NOT NULL,  -- Format: "*A:Text|B:Text|C:Text|D:Text"
            points INTEGER DEFAULT 1 CHECK (points > 0),
            question_type TEXT DEFAULT 'multiple_choice',
            FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
        )
        ''')

        # Results Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_id INTEGER NOT NULL,
            exam_id INTEGER NOT NULL,
            score INTEGER NOT NULL CHECK (score >= 0),
            total_items INTEGER NOT NULL CHECK (total_items > 0),
            percentage REAL CHECK (percentage >= 0 AND percentage <= 100),
            time_spent INTEGER NOT NULL,  -- in seconds
            date_taken DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT CHECK (status IN ('Passed', 'Failed')),
            attempt_number INTEGER DEFAULT 1,
            FOREIGN KEY (trainee_id) REFERENCES trainees(id) ON DELETE CASCADE,
            FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
        )
        ''')

        self.conn.commit()
        self.close()

    def migrate_schema(self):
        """Ensure the database schema is up-to-date."""
        self.connect()
        try:
            # Check and add percentage column to results table
            self.cursor.execute("PRAGMA table_info(results)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'percentage' not in columns:
                self.cursor.execute("""
                ALTER TABLE results 
                ADD COLUMN percentage REAL CHECK (percentage >= 0 AND percentage <= 100)
                """)
            
            # Update existing results with calculated percentages
            self.cursor.execute("""
                UPDATE results 
                SET percentage = (CAST(score AS FLOAT) / total_items) * 100
                WHERE percentage IS NULL AND total_items > 0
            """)
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Schema migration error: {e}")
        finally:
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
            # Whitelist of allowed table names
            allowed_tables = {'exams', 'trainers', 'batches', 'trainees', 'results', 'questions'}
            if table_name not in allowed_tables:
                raise ValueError(f"Invalid table name: {table_name}")
            
            if table_name == 'exams':
                # Explicitly specify the column order for exams table
                self.cursor.execute("""
                    SELECT id, title, module_no, num_items, time_limit, 
                        batch_id, created_at, status 
                    FROM exams WHERE id = ?
                """, (record_id,))
            else:
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
        """Submit exam results and calculate score with proper transaction handling."""
        self.connect()
        try:
            # Start transaction
            self.conn.execute("BEGIN TRANSACTION")
            
            # Get questions and calculate score
            self.cursor.execute("""
                SELECT id, correct_answer, points FROM questions WHERE exam_id = ?
            """, (exam_id,))
            questions = self.cursor.fetchall()
            
            if not questions:
                raise ValueError("No questions found for this exam")
                
            total_points = sum(q[2] for q in questions)
            score = sum(q[2] for q in questions if answers.get(q[0]) == q[1])
            percentage = (score / total_points) * 100 if total_points > 0 else 0
            
            # Insert result
            self.cursor.execute("""
                INSERT INTO results (
                    trainee_id, exam_id, score, total_items, 
                    percentage, time_spent, date_taken, status
                )
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 
                    CASE WHEN ? >= 75 THEN 'Passed' ELSE 'Failed' END)
            """, (trainee_id, exam_id, score, total_points, percentage, 
                  time_spent, percentage))
            
            # Update trainee's exam count
            self.cursor.execute("""
                UPDATE trainees 
                SET exams_taken = exams_taken + 1
                WHERE id = ?
            """, (trainee_id,))
            
            # Commit transaction
            self.conn.commit()
            
            return {
                'score': score,
                'total_items': total_points,
                'percentage': percentage
            }
            
        except Exception as e:
            # Rollback on error
            self.conn.rollback()
            print(f"Error submitting exam result: {e}")
            raise
        finally:
            self.close()

    def get_available_exams(self, trainee_id):
        """Get exams available for a trainee that haven't been taken yet."""
        self.connect()
        try:
            self.cursor.execute("""
                SELECT 
                    e.id, e.title, e.module_no, e.num_items, e.time_limit,
                    CASE WHEN r.id IS NULL THEN 'Not Taken' ELSE 'Completed' END AS status
                FROM exams e
                LEFT JOIN results r ON e.id = r.exam_id AND r.trainee_id = ?
                WHERE e.batch_id = (SELECT batch_id FROM trainees WHERE id = ?)
                  AND e.status = 'Active'
                ORDER BY e.module_no, e.title
            """, (trainee_id, trainee_id))
            columns = ['id', 'title', 'module_no', 'num_items', 'time_limit', 'status']
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error getting available exams: {e}")
            return []
        finally:
            self.close()

    def add_question(self, exam_id, question_text, options, correct_answer, points=1):
        """Add a multiple choice question to an exam
        
        Args:
            exam_id: The ID of the exam this question belongs to
            question_text: The question text
            options: Dictionary of options {'A': 'text', 'B': 'text', ...}
            correct_answer: The correct option letter (A, B, C, or D)
            points: Points for this question
        """
        self.connect()
        try:
            # Format the correct_answer string as "*A:Text|B:Text|C:Text|D:Text"
            options_str = []
            for letter in ['A', 'B', 'C', 'D']:
                if letter in options:
                    prefix = '*' if letter == correct_answer else ''
                    options_str.append(f"{prefix}{letter}:{options[letter]}")
            
            formatted_answer = '|'.join(options_str)
            
            self.cursor.execute('''
            INSERT INTO questions (
                exam_id, question_text, correct_answer, points, question_type
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                exam_id, question_text, formatted_answer, points, 'multiple_choice'
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
        except sqlite3.Error as e:
            print(f"Error getting trainee results: {e}")
            return []
        finally:
            self.close()

    def get_trainee_progress(self, trainee_id):
        """Get detailed progress report for a trainee including all required exams and their status"""
        self.connect()
        try:
            # Get trainee's batch info first
            self.cursor.execute("""
                SELECT t.batch_id, t.name, t.status, b.batch_year
                FROM trainees t
                JOIN batches b ON t.batch_id = b.id
                WHERE t.id = ?
            """, (trainee_id,))
            trainee_info = self.cursor.fetchone()
            
            if not trainee_info:
                raise ValueError("Trainee not found")
                
            batch_id, trainee_name, status, batch_year = trainee_info
            
            # Get all exams for the batch and their status for this trainee
            self.cursor.execute("""
                SELECT 
                    e.id,
                    e.title,
                    e.module_no,
                    e.num_items,
                    COALESCE(r.status, 'Not Taken') as exam_status,
                    COALESCE(r.percentage, 0) as score_percentage,
                    r.date_taken
                FROM exams e
                LEFT JOIN results r ON e.id = r.exam_id AND r.trainee_id = ?
                WHERE e.batch_id = ?
                ORDER BY e.module_no, e.title
            """, (trainee_id, batch_id))
            
            exams = self.cursor.fetchall()
            
            # Calculate overall progress
            total_exams = len(exams)
            completed_exams = sum(1 for exam in exams if exam[4] != 'Not Taken')
            passed_exams = sum(1 for exam in exams if exam[4] == 'Passed')
            
            progress = {
                'trainee_name': trainee_name,
                'batch_year': batch_year,
                'status': status,
                'total_exams': total_exams,
                'completed_exams': completed_exams,
                'passed_exams': passed_exams,
                'completion_percentage': (completed_exams / total_exams * 100) if total_exams > 0 else 0,
                'passing_percentage': (passed_exams / total_exams * 100) if total_exams > 0 else 0,
                'exams': [
                    {
                        'id': exam[0],
                        'title': exam[1],
                        'module_no': exam[2],
                        'num_items': exam[3],
                        'status': exam[4],
                        'score_percentage': exam[5],
                        'date_taken': exam[6]
                    }
                    for exam in exams
                ]
            }
            
            return progress
        finally:
            self.close()

    def validate_batch_assignment(self, batch_id, exam_id=None):
        """Validate batch information and check for any conflicts or issues"""
        self.connect()
        try:
            # Check if batch exists and is active
            self.cursor.execute("""
                SELECT b.id, b.batch_year, b.num_trainees,
                       COUNT(DISTINCT t.id) as current_trainees,
                       COUNT(DISTINCT e.id) as num_exams
                FROM batches b
                LEFT JOIN trainees t ON b.id = t.batch_id AND t.status = 'Active'
                LEFT JOIN exams e ON b.id = e.batch_id AND e.status = 'Active'
                WHERE b.id = ?
                GROUP BY b.id
            """, (batch_id,))
            
            batch_info = self.cursor.fetchone()
            if not batch_info:
                return {
                    'valid': False,
                    'message': 'Batch not found'
                }
                
            batch_id, batch_year, max_trainees, current_trainees, num_exams = batch_info
            
            # If validating for a specific exam
            if exam_id:
                self.cursor.execute("""
                    SELECT COUNT(*) 
                    FROM exams 
                    WHERE batch_id = ? AND module_no = (
                        SELECT module_no FROM exams WHERE id = ?
                    ) AND id != ? AND status = 'Active'
                """, (batch_id, exam_id, exam_id))
                
                duplicate_modules = self.cursor.fetchone()[0] > 0
                if duplicate_modules:
                    return {
                        'valid': False,
                        'message': 'An exam for this module already exists in the batch'
                    }
            
            # Check trainee capacity
            if current_trainees >= max_trainees:
                return {
                    'valid': False,
                    'message': f'Batch is at maximum capacity ({max_trainees} trainees)'
                }
            
            return {
                'valid': True,
                'batch_info': {
                    'id': batch_id,
                    'batch_year': batch_year,
                    'current_trainees': current_trainees,
                    'max_trainees': max_trainees,
                    'num_exams': num_exams
                }
            }
        finally:
            self.close()

    def get_batch_statistics(self, batch_id):
        """Get comprehensive statistics for a batch"""
        self.connect()
        try:
            # Get basic batch info
            self.cursor.execute("""
                SELECT 
                    b.batch_year,
                    b.training_duration,
                    t.name as trainer_name,
                    COUNT(DISTINCT tr.id) as total_trainees,
                    COUNT(DISTINCT e.id) as total_exams,
                    COUNT(DISTINCT CASE WHEN tr.status = 'Active' THEN tr.id END) as active_trainees
                FROM batches b
                LEFT JOIN trainers t ON b.trainer_id = t.id
                LEFT JOIN trainees tr ON b.id = tr.batch_id
                LEFT JOIN exams e ON b.id = e.batch_id AND e.status = 'Active'
                WHERE b.id = ?
                GROUP BY b.id
            """, (batch_id,))
            
            basic_info = self.cursor.fetchone()
            if not basic_info:
                raise ValueError("Batch not found")
                
            # Get exam completion statistics
            self.cursor.execute("""
                SELECT 
                    e.id,
                    e.title,
                    e.module_no,
                    COUNT(DISTINCT r.trainee_id) as attempts,
                    COUNT(DISTINCT CASE WHEN r.status = 'Passed' THEN r.trainee_id END) as passes,
                    AVG(r.percentage) as avg_score
                FROM exams e
                LEFT JOIN results r ON e.id = r.exam_id
                WHERE e.batch_id = ? AND e.status = 'Active'
                GROUP BY e.id
                ORDER BY e.module_no, e.title
            """, (batch_id,))
            
            exam_stats = self.cursor.fetchall()
            
            return {
                'basic_info': {
                    'batch_year': basic_info[0],
                    'training_duration': basic_info[1],
                    'trainer_name': basic_info[2],
                    'total_trainees': basic_info[3],
                    'total_exams': basic_info[4],
                    'active_trainees': basic_info[5]
                },
                'exam_statistics': [
                    {
                        'exam_id': stat[0],
                        'title': stat[1],
                        'module_no': stat[2],
                        'total_attempts': stat[3],
                        'total_passes': stat[4],
                        'average_score': round(stat[5] or 0, 2),
                        'passing_rate': round((stat[4] / stat[3] * 100) if stat[3] > 0 else 0, 2)
                    }
                    for stat in exam_stats
                ]
            }
        finally:
            self.close()

    def validate_exam_attempt(self, trainee_id, exam_id):
        """Validate if a trainee can take an exam"""
        self.connect()
        try:
            # Check if exam exists and is active
            self.cursor.execute("""
                SELECT e.id, e.title, e.module_no,
                       r.status as last_attempt_status,
                       r.date_taken as last_attempt_date,
                       r.percentage as last_score
                FROM exams e
                LEFT JOIN results r ON e.id = r.exam_id 
                    AND r.trainee_id = ?
                    AND r.date_taken = (
                        SELECT MAX(date_taken) 
                        FROM results 
                        WHERE exam_id = e.id AND trainee_id = ?
                    )
                WHERE e.id = ? AND e.status = 'Active'
            """, (trainee_id, trainee_id, exam_id))
            
            result = self.cursor.fetchone()
            if not result:
                return {
                    'can_take': False,
                    'message': 'Exam not found or not active'
                }
            
            exam_id, title, module_no, last_status, last_attempt_date, last_score = result
            
            # If never attempted, allow
            if not last_status:
                return {
                    'can_take': True,
                    'message': 'First attempt'
                }
            
            # If passed, no retake
            if last_status == 'Passed':
                return {
                    'can_take': False,
                    'message': f'You have already passed this exam with {last_score:.1f}%'
                }
            
            # If failed, check cooling period (e.g., 24 hours)
            if last_status == 'Failed':
                from datetime import datetime, timedelta
                last_attempt = datetime.strptime(last_attempt_date, '%Y-%m-%d %H:%M:%S')
                cooling_period = timedelta(hours=24)
                
                if datetime.now() - last_attempt < cooling_period:
                    time_left = cooling_period - (datetime.now() - last_attempt)
                    hours = int(time_left.total_seconds() // 3600)
                    minutes = int((time_left.total_seconds() % 3600) // 60)
                    return {
                        'can_take': False,
                        'message': f'Please wait {hours}h {minutes}m before retaking this exam'
                    }
            
            return {
                'can_take': True,
                'message': 'Retake attempt allowed',
                'previous_attempt': {
                    'status': last_status,
                    'score': last_score,
                    'date': last_attempt_date
                }
            }
            
        finally:
            self.close()

    def get_exam_summary(self, exam_id):
        """Get comprehensive summary of an exam including statistics"""
        self.connect()
        try:
            # Get basic exam info
            self.cursor.execute("""
                SELECT e.title, e.module_no, e.num_items, e.time_limit,
                       b.batch_year, t.name as trainer_name,
                       COUNT(DISTINCT r.trainee_id) as total_attempts,
                       COUNT(DISTINCT CASE WHEN r.status = 'Passed' THEN r.trainee_id END) as total_passes,
                       AVG(r.percentage) as avg_score,
                       MIN(r.percentage) as lowest_score,
                       MAX(r.percentage) as highest_score,
                       AVG(r.time_spent) as avg_time_spent
                FROM exams e
                JOIN batches b ON e.batch_id = b.id
                LEFT JOIN trainers t ON b.trainer_id = t.id
                LEFT JOIN results r ON e.id = r.exam_id
                WHERE e.id = ?
                GROUP BY e.id
            """, (exam_id,))
            
            exam_info = self.cursor.fetchone()
            if not exam_info:
                raise ValueError("Exam not found")
            
            # Get question statistics
            self.cursor.execute("""
                SELECT q.id, q.question_text,
                       COUNT(DISTINCT r.trainee_id) as total_attempts,
                       SUM(CASE WHEN r.answer = q.correct_answer THEN 1 ELSE 0 END) as correct_answers
                FROM questions q
                LEFT JOIN results r ON q.exam_id = r.exam_id
                WHERE q.exam_id = ?
                GROUP BY q.id
            """, (exam_id,))
            
            question_stats = self.cursor.fetchall()
            
            return {
                'exam_info': {
                    'title': exam_info[0],
                    'module_no': exam_info[1],
                    'num_items': exam_info[2],
                    'time_limit': exam_info[3],
                    'batch_year': exam_info[4],
                    'trainer': exam_info[5],
                    'total_attempts': exam_info[6],
                    'total_passes': exam_info[7],
                    'average_score': round(exam_info[8] or 0, 2),
                    'lowest_score': round(exam_info[9] or 0, 2),
                    'highest_score': round(exam_info[10] or 0, 2),
                    'average_time': round(exam_info[11] or 0, 2) if exam_info[11] else 0
                },
                'question_statistics': [
                    {
                        'id': q[0],
                        'text': q[1],
                        'attempts': q[2],
                        'correct_answers': q[3],
                        'success_rate': round((q[3] / q[2] * 100) if q[2] > 0 else 0, 2)
                    }
                    for q in question_stats
                ]
            }
        finally:
            self.close()

    def get_trainee_exam_history(self, trainee_id):
        """Get detailed exam history for a trainee with analytics"""
        self.connect()
        try:
            self.cursor.execute("""
                WITH ExamStats AS (
                    SELECT 
                        r.exam_id,
                        COUNT(*) as attempt_count,
                        MAX(r.percentage) as best_score,
                        MIN(r.percentage) as lowest_score,
                        AVG(r.percentage) as avg_score,
                        MAX(CASE WHEN r.status = 'Passed' THEN 1 ELSE 0 END) as has_passed
                    FROM results r
                    WHERE r.trainee_id = ?
                    GROUP BY r.exam_id
                )
                SELECT 
                    e.id as exam_id,
                    e.title,
                    e.module_no,
                    es.attempt_count,
                    es.best_score,
                    es.lowest_score,
                    es.avg_score,
                    es.has_passed,
                    r.date_taken as last_attempt_date,
                    r.status as last_attempt_status,
                    r.percentage as last_attempt_score
                FROM exams e
                JOIN ExamStats es ON e.id = es.exam_id
                LEFT JOIN results r ON e.id = r.exam_id 
                    AND r.trainee_id = ?
                    AND r.date_taken = (
                        SELECT MAX(date_taken) 
                        FROM results 
                        WHERE exam_id = e.id AND trainee_id = ?
                    )
                ORDER BY e.module_no, e.title
            """, (trainee_id, trainee_id, trainee_id))
            
            exams = self.cursor.fetchall()
            
            # Get overall statistics
            self.cursor.execute("""
                SELECT 
                    COUNT(DISTINCT exam_id) as total_exams_attempted,
                    COUNT(DISTINCT CASE WHEN status = 'Passed' THEN exam_id END) as exams_passed,
                    AVG(percentage) as overall_average,
                    COUNT(*) as total_attempts,
                    SUM(CASE WHEN status = 'Passed' THEN 1 ELSE 0 END) as total_passes
                FROM results
                WHERE trainee_id = ?
            """, (trainee_id,))
            
            stats = self.cursor.fetchone()
            
            return {
                'exam_history': [
                    {
                        'exam_id': exam[0],
                        'title': exam[1],
                        'module_no': exam[2],
                        'attempts': exam[3],
                        'best_score': round(exam[4], 2),
                        'lowest_score': round(exam[5], 2),
                        'average_score': round(exam[6], 2),
                        'passed': bool(exam[7]),
                        'last_attempt_date': exam[8],
                        'last_status': exam[9],
                        'last_score': round(exam[10], 2)
                    }
                    for exam in exams
                ],
                'overall_stats': {
                    'exams_attempted': stats[0],
                    'exams_passed': stats[1],
                    'overall_average': round(stats[2] or 0, 2),
                    'total_attempts': stats[3],
                    'total_passes': stats[4],
                    'pass_rate': round((stats[4] / stats[3] * 100) if stats[3] > 0 else 0, 2)
                }
            }
        finally:
            self.close()

    def update_trainee_status(self, trainee_id):
        """Update trainee status based on exam completion and performance"""
        self.connect()
        try:
            # Start transaction
            self.conn.execute("BEGIN TRANSACTION")
            
            # Get required exams and completion status
            self.cursor.execute("""
                WITH RequiredExams AS (
                    SELECT COUNT(*) as total_exams
                    FROM exams e
                    WHERE e.batch_id = (
                        SELECT batch_id FROM trainees WHERE id = ?
                    )
                    AND e.status = 'Active'
                ),
                CompletedExams AS (
                    SELECT 
                        COUNT(DISTINCT e.id) as completed_exams,
                        COUNT(DISTINCT CASE WHEN r.status = 'Passed' THEN e.id END) as passed_exams
                    FROM exams e
                    LEFT JOIN results r ON e.id = r.exam_id AND r.trainee_id = ?
                    WHERE e.batch_id = (
                        SELECT batch_id FROM trainees WHERE id = ?
                    )
                    AND e.status = 'Active'
                )
                SELECT 
                    re.total_exams,
                    ce.completed_exams,
                    ce.passed_exams
                FROM RequiredExams re, CompletedExams ce
            """, (trainee_id, trainee_id, trainee_id))
            
            result = self.cursor.fetchone()
            if not result:
                raise ValueError("Trainee not found")
                
            total_exams, completed_exams, passed_exams = result
            
            # Determine new status
            new_status = 'Active'
            remarks = None
            
            if completed_exams == total_exams:
                if passed_exams == total_exams:
                    new_status = 'Completed'
                    remarks = 'Successfully completed all required exams'
                else:
                    remarks = f'Completed all exams but passed only {passed_exams}/{total_exams}'
            
            # Update trainee status
            self.cursor.execute("""
                UPDATE trainees
                SET status = ?,
                    remarks = ?,
                    exams_taken = (
                        SELECT COUNT(DISTINCT exam_id)
                        FROM results
                        WHERE trainee_id = ?
                    )
                WHERE id = ?
            """, (new_status, remarks, trainee_id, trainee_id))
            
            # Commit transaction
            self.conn.commit()
            
            return {
                'status': new_status,
                'remarks': remarks,
                'total_exams': total_exams,
                'completed_exams': completed_exams,
                'passed_exams': passed_exams
            }
            
        except Exception as e:
            self.conn.rollback()
            raise
        finally:
            self.close()

    def get_batch_completion_status(self, batch_id):
        """Get detailed completion status for a batch"""
        self.connect()
        try:
            self.cursor.execute("""
                WITH BatchExams AS (
                    SELECT COUNT(*) as total_exams
                    FROM exams
                    WHERE batch_id = ? AND status = 'Active'
                ),
                TraineeProgress AS (
                    SELECT 
                        t.id as trainee_id,
                        t.name,
                        t.status,
                        COUNT(DISTINCT r.exam_id) as exams_taken,
                        COUNT(DISTINCT CASE WHEN r.status = 'Passed' THEN r.exam_id END) as exams_passed,
                        AVG(r.percentage) as avg_score
                    FROM trainees t
                    LEFT JOIN results r ON t.id = r.trainee_id
                    WHERE t.batch_id = ?
                    GROUP BY t.id
                )
                SELECT 
                    tp.*,
                    be.total_exams,
                    CASE 
                        WHEN tp.exams_passed = be.total_exams THEN 'Complete'
                        WHEN tp.exams_taken = be.total_exams THEN 'All Attempted'
                        WHEN tp.exams_taken > 0 THEN 'In Progress'
                        ELSE 'Not Started'
                    END as completion_status,
                    ROUND(CAST(tp.exams_taken AS FLOAT) / be.total_exams * 100, 2) as progress_percentage
                FROM TraineeProgress tp, BatchExams be
                ORDER BY tp.exams_passed DESC, tp.avg_score DESC
            """, (batch_id, batch_id))
            
            trainees = self.cursor.fetchall()
            
            # Get batch summary
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_trainees,
                    SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_trainees,
                    AVG(exams_taken) as avg_exams_taken
                FROM trainees
                WHERE batch_id = ?
            """, (batch_id,))
            
            batch_stats = self.cursor.fetchone()
            
            return {
                'trainees': [
                    {
                        'id': t[0],
                        'name': t[1],
                        'status': t[2],
                        'exams_taken': t[3],
                        'exams_passed': t[4],
                        'average_score': round(t[5] or 0, 2),
                        'total_exams': t[6],
                        'completion_status': t[7],
                        'progress_percentage': t[8]
                    }
                    for t in trainees
                ],
                'batch_stats': {
                    'total_trainees': batch_stats[0],
                    'completed_trainees': batch_stats[1],
                    'completion_rate': round((batch_stats[1] / batch_stats[0] * 100) if batch_stats[0] > 0 else 0, 2),
                    'average_exams_taken': round(batch_stats[2] or 0, 2)
                }
            }
        finally:
            self.close()

    def export_trainee_results(self, trainee_id, format='csv'):
        """Export trainee results to CSV or JSON format"""
        self.connect()
        try:
            # Get trainee details
            self.cursor.execute("""
                SELECT t.name, t.id_no, t.batch_year, b.training_duration
                FROM trainees t
                JOIN batches b ON t.batch_id = b.id
                WHERE t.id = ?
            """, (trainee_id,))
            
            trainee_info = self.cursor.fetchone()
            if not trainee_info:
                raise ValueError("Trainee not found")
            
            # Get exam results with details
            self.cursor.execute("""
                SELECT 
                    e.title,
                    e.module_no,
                    r.score,
                    r.total_items,
                    r.percentage,
                    r.status,
                    r.date_taken,
                    r.time_spent
                FROM results r
                JOIN exams e ON r.exam_id = e.id
                WHERE r.trainee_id = ?
                ORDER BY r.date_taken
            """, (trainee_id,))
            
            results = self.cursor.fetchall()
            
            if format == 'csv':
                import csv
                from io import StringIO
                output = StringIO()
                writer = csv.writer(output)
                
                # Write header with trainee info
                writer.writerow(['Trainee Report'])
                writer.writerow(['Name:', trainee_info[0]])
                writer.writerow(['ID Number:', trainee_info[1]])
                writer.writerow(['Batch Year:', trainee_info[2]])
                writer.writerow(['Training Duration:', trainee_info[3]])
                writer.writerow([])  # Blank line
                
                # Write results header
                writer.writerow([
                    'Exam Title',
                    'Module',
                    'Score',
                    'Total Items',
                    'Percentage',
                    'Status',
                    'Date Taken',
                    'Time Spent (min)'
                ])
                
                # Write results
                for r in results:
                    writer.writerow([
                        r[0],  # title
                        r[1],  # module_no
                        r[2],  # score
                        r[3],  # total_items
                        f"{r[4]:.1f}%",  # percentage
                        r[5],  # status
                        r[6],  # date_taken
                        f"{r[7]/60:.1f}"  # time_spent in minutes
                    ])
                
                return output.getvalue()
                
            elif format == 'json':
                import json
                
                export_data = {
                    'trainee_info': {
                        'name': trainee_info[0],
                        'id_no': trainee_info[1],
                        'batch_year': trainee_info[2],
                        'training_duration': trainee_info[3]
                    },
                    'results': [
                        {
                            'exam_title': r[0],
                            'module_no': r[1],
                            'score': r[2],
                            'total_items': r[3],
                            'percentage': round(r[4], 1),
                            'status': r[5],
                            'date_taken': r[6],
                            'time_spent_minutes': round(r[7]/60, 1)
                        }
                        for r in results
                    ]
                }
                
                return json.dumps(export_data, indent=2)
            
            else:
                raise ValueError("Unsupported export format")
                
        finally:
            self.close()

    def export_batch_report(self, batch_id):
        """Export comprehensive batch report"""
        self.connect()
        try:
            # Get batch overview
            self.cursor.execute("""
                SELECT 
                    b.batch_year,
                    b.training_duration,
                    t.name as trainer_name,
                    COUNT(DISTINCT tr.id) as total_trainees
                FROM batches b
                LEFT JOIN trainers t ON b.trainer_id = t.id
                LEFT JOIN trainees tr ON b.id = tr.batch_id
                WHERE b.id = ?
                GROUP BY b.id
            """, (batch_id,))
            
            batch_info = self.cursor.fetchone()
            if not batch_info:
                raise ValueError("Batch not found")
            
            # Get trainee performance
            self.cursor.execute("""
                WITH TraineeStats AS (
                    SELECT 
                        t.id,
                        t.name,
                        t.id_no,
                        t.status,
                        COUNT(DISTINCT r.exam_id) as exams_taken,
                        COUNT(DISTINCT CASE WHEN r.status = 'Passed' 
                            THEN r.exam_id END) as exams_passed,
                        AVG(r.percentage) as avg_score
                    FROM trainees t
                    LEFT JOIN results r ON t.id = r.trainee_id
                    WHERE t.batch_id = ?
                    GROUP BY t.id
                )
                SELECT *
                FROM TraineeStats
                ORDER BY avg_score DESC
            """, (batch_id,))
            
            trainee_stats = self.cursor.fetchall()
            
            # Generate CSV report
            import csv
            from io import StringIO
            output = StringIO()
            writer = csv.writer(output)
            
            # Write batch info
            writer.writerow(['Batch Performance Report'])
            writer.writerow(['Batch Year:', batch_info[0]])
            writer.writerow(['Training Duration:', batch_info[1]])
            writer.writerow(['Trainer:', batch_info[2]])
            writer.writerow(['Total Trainees:', batch_info[3]])
            writer.writerow([])
            
            # Write trainee performance header
            writer.writerow([
                'Trainee Name',
                'ID Number',
                'Status',
                'Exams Taken',
                'Exams Passed',
                'Average Score',
                'Progress'
            ])
            
            # Write trainee stats
            for stat in trainee_stats:
                writer.writerow([
                    stat[1],  # name
                    stat[2],  # id_no
                    stat[3],  # status
                    stat[4],  # exams_taken
                    stat[5],  # exams_passed
                    f"{stat[6]:.1f}%" if stat[6] else "N/A",  # avg_score
                    f"{(stat[5]/stat[4]*100):.1f}%" if stat[4] > 0 else "0%"
                ])
            
            return output.getvalue()
            
        finally:
            self.close()