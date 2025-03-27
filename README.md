# Exam Management System

A desktop application for managing Basic Competency Exams for Trainers Methodology (TM) Level 1 in PTC-Iba. Built with Python using CustomTkinter for a modern UI experience.

## Features

### 🔐 Authentication System
- Multi-user login system supporting Admin and Trainee roles
- Secure access control based on user type
- Username/ULI-based authentication for trainees

### 👨‍💼 Admin Dashboard
- **Comprehensive Data Management**
  - Trainers management (personal info, class assignments)
  - Batch management (year, size, duration, location)
  - Trainee records (personal info, batch assignment, progress)
  - Exam creation and modification
  - Results tracking and verification

- **Exam Management Features**
  - Create and edit exam details (title, module, time limits)
  - Dynamic question management
  - Multiple-choice question support
  - Point-based scoring system
  - Batch-specific exam assignments

### 👨‍🎓 Trainee Dashboard
- **Personal Profile**
  - View and manage personal information
  - Track training progress
  - View batch and trainer details

- **Exam Features**
  - Access assigned exams
  - Time-limited exam sessions
  - Immediate feedback on completion
  - View exam history and results

### 📊 Results Management
- Automatic scoring system
- Detailed result tracking
- Performance analytics
- Progress monitoring

## Technical Details

### Database Structure
- SQLite database with related tables:
  - Trainers
  - Batches
  - Trainees
  - Exams
  - Questions
  - Results

### Built With
- Python 3.x
- CustomTkinter - For modern UI components
- SQLite3 - For database management
- Tkinter - For additional UI elements

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/exam-management-system.git
```

2. Install required dependencies:
```bash
pip install customtkinter
```

3. Run the application:
```bash
python app.py
```

## Usage

### Admin Access
- Username: admin
- Password: admin123
- Full access to all management features

### Trainee Access
- Login using assigned ULI number
- Access to personal dashboard and assigned exams

## Project Structure


