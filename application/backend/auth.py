
# t3-1
import os
from flask import session, redirect, url_for, render_template, request, flash
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Fetch email and password from environment variables
EMAIL = os.getenv('EMAIL_ADDRESS')
PASSWORD = os.getenv('UMINEKO_FUND_PASSWORD')

# Hash the password from the .env file
hashed_password = generate_password_hash(PASSWORD)

# Dummy user credentials fetched from environment variables
users = {
    EMAIL: {
        "password": hashed_password
    }
}

# Function to check if the user is logged in
def is_logged_in():
    return 'user' in session

# Login logic
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users.get(email)
        if user and check_password_hash(user['password'], password):
            session['user'] = email  # Store the email in the session
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('login.html')

# Logout logic
def logout():
    session.pop('user', None)  # Remove the user from the session
    return redirect(url_for('login'))


