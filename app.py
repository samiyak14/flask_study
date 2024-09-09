from flask import Flask, request, redirect, url_for, render_template, session
import openpyxl
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

# File path for registration details
REGISTRATION_FILE = 'registration_details.xlsx'

def get_workbook():
    return openpyxl.load_workbook(filename=REGISTRATION_FILE)

def register_student(student_id, student_email, name, parent_email, password):
    wb = get_workbook()
    ws = wb.active
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    ws.append([student_id, student_email, name, parent_email, hashed_password.decode()])
    wb.save(filename=REGISTRATION_FILE)

def login_student(student_email, password):
    wb = get_workbook()
    ws = wb.active
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[1] == student_email:
            stored_hashed_password = row[4].encode()
            if bcrypt.checkpw(password.encode(), stored_hashed_password):
                return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if login_student(email, password):
            session['email'] = email
            return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        student_id = request.form['student_id']
        email = request.form['email']
        name = request.form['name']
        parent_email = request.form['parent_email']
        password = request.form['password']
        register_student(student_id, email, name, parent_email, password)
        return redirect(url_for('login'))
    return render_template('sign_up.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        return f"Welcome to your dashboard, {session['email']}! <a href='{url_for('logout')}'>Logout</a>"
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('email', None)  # Remove 'email' from session
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
