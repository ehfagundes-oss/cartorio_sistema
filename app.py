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
    SECRET_KEY=os.environ.get('SECRET_KEY', 'default-secret-key'),
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

# --- LÓGICA DE AUTENTICAÇÃO E ROTAS DE INTERFACE (sem alterações) ---
# ... (código existente)

# --- ROTAS DE PROCESSAMENTO (COM A MUDANÇA PRINCIPAL NO NASCIMENTO) ---
@app.route('/enviar-nascimento', methods=['POST'])
def receber_nascimento():
    conn = None
    try:
        print("--- INICIANDO TESTE COM AUTOCOMMIT ---")
        conn = psycopg2.connect(app.config['DATABASE_URL'])
        conn.autocommit = True # <-- A MUDANÇA MÁGICA
        
        cursor = conn.cursor()
        
        nome_nascido = request.form.get('nome_nascido')
        mae_nome = request.form.get('mae_nome')
        pai_nome = request.form.get('pai_nome')

        print(f"Tentando inserir com autocommit: {nome_nascido}, {mae_nome}, {pai_nome}")
        
        query = "INSERT INTO nascimentos (nome_nascido, mae_nome, pai_nome) VALUES (%s, %s, %s)"
        
        cursor.execute(query, (nome_nascido, mae_nome, pai_nome))
        
        print("!!! COMANDO INSERT ENVIADO COM AUTOCOMMIT !!!")
        
        cursor.close()
        
    except Exception as e:
        print(f"!!!!!!!!!! ERRO CRÍTICO NO TESTE COM AUTOCOMMIT !!!!!!!!!!")
        print(str(e))
        return "<h1>Ocorreu um erro. Verifique os logs.</h1>", 500
    finally:
        if conn:
            conn.close()
            
    return "<h1>Teste com autocommit executado! Verifique o painel /admin.</h1>"

# As outras funções de recebimento permanecem como estavam
@app.route('/enviar-obito', methods=['POST'])
def receber_obito():
    # ... (código original)
    return "<h1>Função de Óbito temporariamente desabilitada para teste.</h1>"

@app.route('/enviar-casamento', methods=['POST'])
def receber_casamento():
    # ... (código original)
    return "<h1>Função de Casamento temporariamente desabilitada para teste.</h1>"

# --- O RESTO DO ARQUIVO (ROTAS DE LOGIN, ADMIN, DETALHES, ETC) CONTINUA IGUAL ---
# ... (cole o resto do seu app.py aqui)