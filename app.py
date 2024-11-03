from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for session management

# Initialize the database
def init_db():
    with sqlite3.connect('blogs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS blogs (
                            id INTEGER PRIMARY KEY,
                            title TEXT NOT NULL,
                            content TEXT NOT NULL
                         )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            username TEXT NOT NULL,
                            password TEXT NOT NULL
                         )''')
init_db()


# Admin Login Credentials
admin_username = 'admin'
admin_password = 'password123'  # Change this to something more secure in production


# Home route
@app.route('/') 
def home_page():
    with sqlite3.connect('blogs.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blogs") 
        blogs = cursor.fetchall()
    return render_template('home.html', blogs=blogs)


# Route to serve blog posts
@app.route('/blogs/<blog_name>')
def blog_post(blog_name):
    try:
        return render_template(f'blogs/{blog_name}')
    except:
        return "Blog not found", 404


# Discussion route
@app.route('/discussion')
def discussion():
    return render_template('discussion.html')


# About Us route
@app.route('/about')
def about():
    return render_template('about.html')


# Contact route
@app.route('/contact')
def contact():
    return render_template('contact.html')


# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('blogs.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')


# Login route for regular users
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('blogs.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = username
                return redirect(url_for('home_page'))
            else:
                return "Invalid credentials"
    return render_template('login.html')


# Admin Dashboard Route
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    with sqlite3.connect('blogs.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blogs")
        blogs = cursor.fetchall()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
    return render_template('admin/dashboard.html', blogs=blogs, users=users)


# Route to handle admin login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == admin_username and password == admin_password:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid credentials"
    return render_template('admin/login.html')


# Route to log out the admin
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home_page'))


if __name__ == '__main__':
    app.run(debug=True)
