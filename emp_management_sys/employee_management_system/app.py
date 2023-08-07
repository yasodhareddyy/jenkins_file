from flask import Flask, render_template, request, redirect, session
import pymysql

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure secret key

# MySQL Configuration
db = pymysql.connect(
    host='localhost',
    user='root',
    password='8309932066',
    database='employee_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# Create a table for employees if it does not exist
with db.cursor() as cursor:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            age INT,
            experience FLOAT,
            salary FLOAT,
            skills TEXT,
            qualifications TEXT
        )
    ''')


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get user input from the signup form
        username = request.form['username']
        password = request.form['password']

        # Store the user information in the database
        with db.cursor() as cursor:
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
            db.commit()

        return redirect('/login')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get user input from the login form
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists in the database
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = cursor.fetchone()

        if user:
            session['username'] = user['username']
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        # Get employee data from the form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        age = request.form['age']
        experience = request.form['experience']
        salary = request.form['salary']
        skills = request.form['skills']
        qualifications = request.form['qualifications']

        # Save the employee record in the database
        with db.cursor() as cursor:
            cursor.execute('''
                INSERT INTO employees (first_name, last_name, age, experience, salary, skills, qualifications)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (first_name, last_name, age, experience, salary, skills, qualifications))
            db.commit()

    # Fetch all employees from the database

    with db.cursor() as cursor:
        cursor.execute('SELECT * FROM employees ORDER BY first_name ASC')
        employees = cursor.fetchall()

    return render_template('dashboard.html', employees=employees)


@app.route('/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    if 'username' not in session:
        return redirect('/login')

    # Delete the employee record from the database
    with db.cursor() as cursor:
        cursor.execute('DELETE FROM employees WHERE id = %s', (employee_id,))
        db.commit()

    return redirect('/dashboard')


@app.route('/update/<int:employee_id>', methods=['GET', 'POST'])
def update_employee(employee_id):
    if request.method == 'POST':
        # Retrieve the updated employee details from the form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        age = request.form['age']
        experience = request.form['experience']
        salary = request.form['salary']
        skills = request.form['skills']
        qualifications = request.form['qualifications']

        # Update the employee record in the database
        with db.cursor() as cursor:
            cursor.execute('UPDATE employees SET first_name = %s, last_name = %s, age = %s, experience = %s, '
                           'salary = %s, skills = %s, qualifications = %s WHERE id = %s',
                           (first_name, last_name, age, experience, salary, skills, qualifications, employee_id))
            # Commit the changes to the database
            db.commit()

        # Redirect back to the dashboard or the updated employee's details page
        return redirect('/dashboard')

    # Fetch the employee data from the database
    with db.cursor() as cursor:
        cursor.execute('SELECT * FROM employees WHERE id = %s', (employee_id,))
        employee = cursor.fetchone()

    # Render the update_employee.html template with the employee data
    return render_template('update_employee.html', employee=employee)


@app.route('/logout')
def logout():
    # Clear the session data
    session.pop('username', None)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
