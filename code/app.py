# flask_app_with_orm.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from PyPDF2 import PdfReader
from transformers import pipeline
import tempfile
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username'].strip()
    email = request.form['email'].strip()
    password = request.form['password'].strip()
    confirm_password = request.form['confirm-password'].strip()

    if not username or not email or not password or not confirm_password:
        flash('All fields are required.')
        return redirect(url_for('signup_page'))

    if password != confirm_password:
        flash('Passwords do not match!')
        return redirect(url_for('signup_page'))

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash('Username already exists!')
        return redirect(url_for('signup_page'))

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    flash('Account created successfully! Please log in.')
    return redirect(url_for('login_page'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password'].strip()

    if not username or not password:
        flash('Both fields are required.')
        return redirect(url_for('login_page'))

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['username'] = username
        flash('Logged in successfully!')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('login_page'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You must be logged in to view this page.')
        return redirect(url_for('login_page'))

    return render_template('dashboard.html', username=session['username'])

@app.route('/pdf_chat', methods=['GET', 'POST'])
def pdf_chat():
    extracted_text = ""
    summary = ""
    action = request.form.get("action")

    if request.method == 'POST':
        file = request.files.get('pdf')

        if file and file.filename.endswith('.pdf'):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                file.save(tmp.name)
                temp_path = tmp.name

            reader = PdfReader(temp_path)
            for page in reader.pages:
                extracted_text += page.extract_text() or ""
            reader.stream.close()
            os.remove(temp_path)

            if action == "summarize":
                max_chunk = 2000
                chunks = [extracted_text[i:i+max_chunk] for i in range(0, len(extracted_text), max_chunk)]
                for c in chunks:
                    result = summarizer(c, max_length=200, min_length=50, do_sample=False)
                    summary += result[0]['summary_text'] + " "

    return render_template(
        'pdf_chat.html',
        extracted_text=extracted_text or None,
        summary=summary.strip() or None
    )

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/account')
def my_account():
    if 'username' not in session:
        flash('Please log in first.')
        return redirect(url_for('login_page'))

    user = User.query.filter_by(username=session['username']).first()
    email = user.email if user else 'N/A'

    return render_template('account.html', username=user.username, email=email)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
