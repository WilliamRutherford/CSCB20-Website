from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import random
import os
import sqlite3
from sqlite3 import Error
import re
import time
import codecs
import base64
import hashlib

app = Flask(__name__)

''' Text Formatting '''

# Before using the username as a SQL query, we wish to make sure there's no funny business
# Since we are accepting just the UTORID, it should be only letters and numbers
# No whitespace, no punctuation, etc. [A-Za-z0-9] only
# This prevents any kind of SQL Injection, with an input like '; DROP TABLE *'
def safestr(str):
    return re.sub(r"[^A-Za-z0-9]*", '', str)

def sql_text(str):
    return re.sub(r"[']", "''", str)

def sql_decode(str):
    return re.sub(r"''","'", str)

''' Passwords '''

def check_pass(username, input_pass):
    user_dat = db_read_query(db, "SELECT * FROM users WHERE utor_id = '"+safestr(username)+"';")
    if(not user_dat):
        print("No User Found")
        return False
    else:
        user_dat = user_dat[0]
    exp_hash = user_dat[3]
    salt = sql_decode(user_dat[4])
    
    hash_res = hashlib.md5((input_pass + salt).encode()).hexdigest()
    if(hash_res == exp_hash):
        return True
    else:
        return False
        
def generate_pass(pass_str):
    salt = base64.b64encode(os.urandom(16))
    hash_res = hashlib.md5((pass_str + str(salt)).encode()).hexdigest()
    return (hash_res, salt)

''' Users '''
        
def add_user(username, student_num, pass_str, is_admin = False):
    curr_users = list(map(lambda x: x[0], db_read_query(db, "SELECT utor_id FROM users")))
    (hash_res, salt) = generate_pass(pass_str)
    if(username not in curr_users):
        db_query(db, \
        f"INSERT INTO users (utor_id, student_num, pw_hash, pw_salt, is_admin) VALUES ('{username}',{student_num},'{hash_res}','{sql_text(str(salt))}', {int(is_admin)});")
    else:
        flash("A user with that UTORID already exists!")
        print(f"A user with the UTORid {username} already exists.")
        
def get_instructors():
    all_instructors = list(map(lambda x: x[0],db_read_query(db, "SELECT utor_id FROM users WHERE is_admin = 1")))
    return all_instructors

def get_students():
    all_students = list(map(lambda x: x[0],db_read_query(db, "SELECT utor_id FROM users WHERE is_admin = 0")))
    return all_students    

''' Feedback '''

""" 
Feedback Info:

    instructor TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    text_qa TEXT,
    text_qb TEXT,
    text_qc TEXT,
    text_qd TEXT
"""
def add_feedback(recipient, qa, qb, qc, qd):
    curr_time = int(time.time())
    db_query(db, f"INSERT INTO feedback (instructor, timestamp, text_qa, text_qb, text_qc, text_qd) VALUES ('{safestr(recipient)}',{curr_time},'{sql_text(qa)}','{sql_text(qb)}','{sql_text(qc)}','{sql_text(qd)}')")
    
def map_feedback(f):
    '''
    id, instructor, timestamp, qa, qb, qc, qd.
    '''
    feedback = {}
    feedback['instructor'] = f[1]
    feedback['time'] = time.strftime('%H:%M %a %B %Y', time.localtime(f[2]))
    feedback['qa'] = f[3]
    feedback['qb'] = f[4]
    feedback['qc'] = f[5]
    feedback['qd'] = f[6]
    return feedback
    
def get_feedback(recipient):
    all_feedback = db_read_query(db, \
        f"SELECT * FROM feedback WHERE instructor = '{safestr(recipient)}'")
    return list(map(map_feedback, all_feedback))

''' Marks '''

''' Marks in Database:
    utor_id TEXT NOT NULL,
    a1_mark REAL, a2_mark REAL, a3_mark REAL,
    t1_mark REAL, t2_mark REAL, t3_mark REAL,
    exam_mark REAL
'''

def input_marks(utorid, a1, a2, a3, t1, t2, t3, exam):
    student_marks = db_read_query(db, f"SELECT * FROM marks WHERE utor_id = '{safestr(utorid)}'")
    if(not student_marks):
        #print(f"no marks found for {utorid}")
        db_query(db, f"INSERT INTO marks (utor_id, a1_mark, a2_mark, a3_mark, t1_mark, t2_mark, t3_mark, exam_mark) VALUES ('{safestr(utorid)}', {a1}, {a2}, {a3}, {t1}, {t2}, {t3}, {exam})")
    else:
        #print(f"marks found for {utorid}")
        db_query(db, f"UPDATE marks SET 'a1_mark' = {a1}, 'a2_mark' = {a2}, 'a3_mark' = {a3}, 't1_mark' = {t1}, 't2_mark' = {t2}, 't3_mark' = {t3}, 'exam_mark' = {exam} WHERE utor_id = '{utorid}'")


def mark_map(m, user):
    marks = {}
    marks['utorid'] = user
    marks['a1'] = m[0]
    marks['a2'] = m[1]
    marks['a3'] = m[2]
    marks['t1'] = m[3]
    marks['t2'] = m[4]
    marks['t3'] = m[5]
    marks['final'] = m[6]
    return marks

'''
Since this is used for the context of our template, it must be a map.
eg marks.a1, marks.a2, ... marks.exam
'''
def student_marks(utorid):
    marks = []
    db_marks = db_read_query(db, \
        f"SELECT * FROM marks WHERE utor_id = '{safestr(utorid)}'")
    if(db_marks):
        db_marks = db_marks[0]
        marks = db_marks[2:]
        return mark_map(marks, utorid)
    else:
        return {}

def get_all_marks():
    marks = []
    for student in get_students():
        marks.append(student_marks(student))
    return marks
    

''' Remark Request '''

'''
    utor_id TEXT NOT NULL,
    assessment INT NOT NULL,
    explain TEXT,
'''

def add_remark(student, assessment, explain):
    db_query(db, f"INSERT INTO remarks (utor_id, assessment, explain) VALUES ('{safestr(student)}', {assessment}, '{sql_text(explain)}')")

def map_remark(remark):
    remark_map = {}
    remark_map['utorid'] = remark[1]
    remark_map['explain'] = remark[3]
    remark_map['assessment'] = (['Assignment 1', 'Assignment 2', 'Assignment 3', 'Test 1', 'Test 2', 'Test 3', 'Final'])[remark[2]]
    return remark_map
    
def get_remarks():
    all_remarks = db_read_query(db, f"SELECT * from remarks")
    
    return list(map(map_remark, all_remarks))

''' Using SQLite Database '''

def create_db_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


db = create_db_connection(r".\assignment3.db")

def db_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def db_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
    
        
''' Current User Info '''

'''
User Info:

  [0] id INTEGER PRIMARY KEY AUTOINCREMENT,  
  [1] utor_id TEXT NOT NULL, 
  [2] student_num INTEGER NOT NULL,
  [3] pw_hash TEXT NOT NULL,
  [4] pw_salt TEXT NOT NULL,
  [5] is_admin INTEGER NOT NULL
'''

def get_user(utorid):
    user_row = db_read_query(db, "SELECT * FROM users WHERE utor_id = '"+safestr(utorid)+"';")
    user_row = user_row[0]
    return user_map(user_row[1], user_row[2], bool(user_row[5]))

curr_user = {}

def user_map(utorid, studentnum, isadmin=False):
    curr_user['utorid'] = utorid
    curr_user['studentnum'] = studentnum
    curr_user['instructor'] = isadmin
    return curr_user

''' Pages '''

@app.route('/')
def home():
    if (not session.get('logged_in')):
        return render_template('login.html')
    else:
        return render_template('index.html', user=curr_user)

@app.route('/login', methods=['POST'])
def login():
    input_username = request.form['username']
    input_password = request.form['password']
    if(check_pass(input_username, input_password)):
        session['logged_in'] = True
        user = get_user(input_username)
        session['admin'] = user['instructor']
    else:
        flash('wrong password!')
    return home()
            
@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('login.html', user=curr_user)

@app.route("/create-account", methods=['GET','POST'])
def sign_up():  
    return render_template("create-account.html")

@app.route("/account-form", methods=['POST'])
def create_account():
    input_username = request.form['username']
    input_password = request.form['password']
    input_number   = request.form['student-num']
    input_admin = request.form.get('instructor')
    if(input_admin == 1 or input_admin == "1"):
        input_admin = True
    else:
        input_admin = False
    
    #print(input_admin)
    add_user(input_username, input_number, input_password, input_admin)
    #print(f"user {input_username} was added as an instructor? {input_admin}")
    return render_template('login.html')

@app.route("/feedback")
def feedback():
    if( curr_user == {}):
        return render_template('login.html')
    if(session['admin']):
        return feedback_instructor()
    else:
        return feedback_student()

@app.route("/feedback-student", methods=['GET', 'POST'])
def feedback_student():
    return render_template('feedback.html', user=curr_user, instructors=get_instructors())

@app.route("/feedback-instructor", methods=['GET', 'POST'])
def feedback_instructor():
    your_feedback = get_feedback(curr_user['utorid'])
    return render_template('feedback-instructor.html', user=curr_user, all_feedback=your_feedback)

'''
Feedback Info:

    instructor TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    text_qa TEXT, text_qb TEXT, text_qc TEXT, text_qd TEXT
'''
@app.route("/send-feedback", methods=['GET', 'POST'])
def send_feedback():
    recipient = request.form['instructor']
    qa = request.form['a']
    qb = request.form['b']
    qc = request.form['c']
    qd = request.form['d']
    add_feedback(recipient, qa, qb, qc, qd)
    return home()    

def check_mark_input(x):
    if(x == ""):
        return 0
    else:
        return x

@app.route("/marks-instructor", methods=['POST'])
def marks_instructor():
    '''all_students = get_students()
    all_marks = get_all_marks()
    all_remarks = get_remarks()'''
    
    #which student
    student = request.form['student']
    # assignments
    a1_mark = check_mark_input(request.form['a1'])
    a2_mark = check_mark_input(request.form['a2'])
    a3_mark = check_mark_input(request.form['a3'])
    # tests
    t1_mark = check_mark_input(request.form['t1'])
    t2_mark = check_mark_input(request.form['t2'])
    t3_mark = check_mark_input(request.form['t3'])
    # final
    exam_mark = check_mark_input(request.form['final'])
    
    input_marks(student, a1_mark, a2_mark, a3_mark, t1_mark, t2_mark, t3_mark, exam_mark)
    return marks()
    #return render_template('marks-instructor.html', user=curr_user, students=all_students, marks=all_marks, remarks=all_remarks)

@app.route("/marks-student", methods=['GET', 'POST'])
def marks_student():
    users_marks = student_marks(curr_user['utorid'])
    utorid = curr_user['utorid']
    assign = request.form['assessment']
    assessment = (['Assignment 1', 'Assignment 2', 'Assignment 3', 'Test 1', 'Test 2', 'Test 3', 'Final']).index(assign)
    explain = request.form['explanation']
    add_remark(utorid, assessment, explain)
    return render_template('marks-student.html', user=curr_user, marks=users_marks)

@app.route("/marks", methods=['GET', 'POST'])
def marks():
    if( curr_user == {}):
        return render_template('login.html')    
    if(session['admin']):
        all_students = get_students()
        all_marks = get_all_marks()
        all_remarks = get_remarks()        
        return render_template('marks-instructor.html', user=curr_user, students=all_students, marks=all_marks, remarks=all_remarks)
    else:
        users_marks = student_marks(curr_user['utorid'])
        return render_template('marks-student.html', user=curr_user, marks=users_marks)


@app.route("/assignments")
def assignments():
    return render_template('assignments.html', user=curr_user)

@app.route("/tutorials")
def tutorials():
    return render_template('tutorials.html', user=curr_user)

@app.route("/course-team")
def course_team():
    return render_template('course-team.html', user=curr_user)

def default_users():
    for i in ["1","2"]:
        add_user("student"+i, int(i), "student"+i)
        add_user("instructor"+i, 100+int(i), "instructor"+i, True)


create_student_table = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,  
  utor_id TEXT NOT NULL, 
  student_num INTEGER NOT NULL,
  pw_hash TEXT NOT NULL,
  pw_salt TEXT NOT NULL,
  is_admin INTEGER NOT NULL
);
"""

create_marks_table = """ 
CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utor_id TEXT NOT NULL,
    a1_mark REAL,
    a2_mark REAL,
    a3_mark REAL,
    t1_mark REAL,
    t2_mark REAL,
    t3_mark REAL,
    exam_mark REAL,
    FOREIGN KEY (utor_id) REFERENCES users (utor_id)
);
"""

''' 
Remark Request Info:

utor_id: Who submitted the request
assessment: an int from 0 to 6. 
0-2 are assignments, 3-5 are tests, 6 is the final exam.
explain: The explanation or reasoning given for why it should be remarked.
'''

create_remarks_table = """ 
CREATE TABLE IF NOT EXISTS remarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utor_id TEXT NOT NULL,
    assessment INT NOT NULL,
    explain TEXT,
    FOREIGN KEY (utor_id) REFERENCES users (utor_id)
);
"""

create_feedback_table = '''
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instructor TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    text_qa TEXT,
    text_qb TEXT,
    text_qc TEXT,
    text_qd TEXT,
    FOREIGN KEY (instructor) REFERENCES users (utor_id) 
);
'''

app.secret_key = 'super secret key'

db_query(db, create_student_table)
db_query(db, create_marks_table)
db_query(db, create_remarks_table)
db_query(db, create_feedback_table)

# No users
if(not db_read_query(db, "SELECT * FROM users")):
    default_users()
    add_user("ruther60", 1002583475, "password")
    add_user("amy", 100, "admin")

# No marks
if(not db_read_query(db, "SELECT * FROM marks")):
    input_marks("ruther60",100,100,100,100,100,100,100)
    input_marks("student1", 50, 50, 80, 50, 20, 30, 50)
    input_marks("student2",  0,  0,  0,  0,  0,  0,  0)
    input_marks("amy"     , 20, 20, 30,  0,  0,  0,100)

# No remarks
if(not db_read_query(db, "SELECT * FROM remarks")):
    add_remark("ruther60",0,"Example Text")
    add_remark("student1",3,"Lorem Ipsum")

# No feedback
if(not db_read_query(db, "SELECT * FROM feedback")):
    add_feedback("instructor1", "PROBABLY", "MAYBE", "SEEMS LIKELY", "ABSOLUTELY")


if(__name__=="__main__"):
    
    if 'WINGDB_ACTIVE' in os.environ:
        app.debug = False
    
    app.run()
