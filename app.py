from flask import Flask, request, redirect, url_for, render_template, session
import openpyxl
import bcrypt
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# File path for registration details
REGISTRATION_FILE = 'workbooks/registration_details.xlsx'

def get_workbook():
    return openpyxl.load_workbook(filename=REGISTRATION_FILE)

def register_user(enrno, email, name, parent_email, password, role, subjects=''):
    wb = get_workbook()
    if role == 'teacher':
        ws = wb['Teachers']
    else:
        ws = wb['Students']
    
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    if role == 'teacher':
        ws.append([email, name, hashed_password.decode(), role, subjects])
    else:
        ws.append([enrno, email, name, parent_email, hashed_password.decode(), role])
    wb.save(filename=REGISTRATION_FILE)

def login_user(email, password, role):
    wb = get_workbook()
    if role == 'teacher':
        ws = wb['Teachers']
    else:
        ws = wb['Students']
    
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] == email:
            stored_hashed_password = row[2].encode()
            if bcrypt.checkpw(password.encode(), stored_hashed_password):
                return row  # Return the whole row for further use
        if row[1] == email:
            stored_hashed_password = row[4].encode()
            if bcrypt.checkpw(password.encode(), stored_hashed_password):
                return row  # Return the whole row for further use
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = login_user(email, password, 'student')
        if user_data:
            session['email'] = email
            session['role'] = 'student'
            session['name'] = user_data[2]  # Extract name
            return redirect(url_for('student_dashboard'))
        return 'Invalid credentials.'
    return render_template('login_student.html')

@app.route('/login_teacher', methods=['GET', 'POST'])
def login_teacher():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = login_user(email, password, 'teacher')
        if user_data:
            session['email'] = email
            session['role'] = 'teacher'
            session['name'] = user_data[1]  # Extract name
            session['subjects'] = user_data[4]  # Extract subjects
            return redirect(url_for('teacher_dashboard'))
        return 'Invalid credentials'
    return render_template('login_teacher.html')

@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        enrno = request.form['enrno']
        email = request.form['email']
        name = request.form['name']
        parent_email = request.form['parent_email']
        password = request.form['password']
        register_user(enrno, email, name, parent_email, password, 'student')
        return redirect(url_for('login_student'))
    return render_template('register_student.html')

@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        subjects = request.form['subjects']
        register_user('', email, name, '', password, 'teacher', subjects)
        return redirect(url_for('login_teacher'))
    return render_template('register_teacher.html')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'role' in session and session['role'] == 'teacher':
        subjects = session.get('subjects', '').split(', ')
        return render_template('teacher_dashboard.html', subjects=subjects)
    return redirect(url_for('index'))

@app.route('/student_dashboard')
def student_dashboard():
    if 'role' in session and session['role'] == 'student':
        return render_template('student_dashboard.html')
    return redirect(url_for('index'))

@app.route('/select_subject', methods=['POST'])
def select_subject():
    if 'role' in session and session['role'] == 'teacher':
        selected_class = request.form['class']
        selected_subject = request.form['subject']
        return redirect(url_for('attendance_form', selected_class=selected_class, selected_subject=selected_subject))
    return redirect(url_for('index'))

@app.route('/attendance_form/<selected_class>/<selected_subject>', methods=['GET', 'POST'])
def attendance_form(selected_class, selected_subject):
    if 'role' in session and session['role'] == 'teacher':
        if request.method == 'POST':
            absent_roll_numbers = request.form['absent_roll_numbers'].split(',')
            absent_roll_numbers = set(int(roll.strip()) for roll in absent_roll_numbers)
            date = request.form['date']
            day = request.form['day']

            workbook_name = f'workbooks/{selected_class}.xlsx'
            division = selected_subject

            try:
                book = openpyxl.load_workbook(workbook_name)
                ws = book[division]

                current_column = 1
                for row in ws.iter_rows(min_row=2):
                    for cell in row:
                        if cell.value is None:
                            break

                current_column = cell.column
                roll_number_column = 1

                for row in range(4, ws.max_row + 1):
                    roll_number = ws.cell(row=row, column=roll_number_column).value
                    cell = ws.cell(row=row, column=current_column)

                    if roll_number in absent_roll_numbers:
                        cell.value = 'A'
                    else:
                        if cell.value is None:
                            cell.value = 'P'

                ws.cell(row=2, column=current_column).value = date
                ws.cell(row=3, column=current_column).value = day

                book.save(workbook_name)

                return render_template('success.html', message='Attendance updated successfully!')
            except Exception as e:
                return render_template('error.html', message=f'Error occurred: {e}')
        return render_template('attendance_form.html', selected_class=selected_class, selected_subject=selected_subject)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
