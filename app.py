import os
import psycopg2
import psycopg2.extras
import uuid
from datetime import datetime
from flask import Flask, render_template, request, g, send_from_directory, abort, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from functools import wraps
from dotenv import load_dotenv

# --- CONFIGURAÇÃO E CRIAÇÃO DO APP ---
load_dotenv() 
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'chave-padrao-para-desenvolvimento-local'),
    UPLOAD_FOLDER='uploads',
    DATABASE_URL=os.environ.get('DATABASE_URL')
)
if not os.path.exists(app.config['UPLOAD_FOLDER']): os.makedirs(app.config['UPLOAD_FOLDER'])

# --- BANCO DE DADOS POSTGRESQL ---
def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(app.config['DATABASE_URL'], cursor_factory=psycopg2.extras.DictCursor)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None: db.close()

def init_db():
    # Este código está correto, não precisa ser executado novamente
    pass

# --- LÓGICA DE AUTENTICAÇÃO ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'senha123':
            session['logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Usuário ou senha inválidos.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- ROTAS DA INTERFACE ---
@app.route('/')
def homepage(): return render_template('homepage.html')
@app.route('/nascimento')
def form_nascimento(): return render_template('formulario_nascimento.