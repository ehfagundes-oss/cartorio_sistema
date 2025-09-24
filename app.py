import os
import psycopg2
import psycopg2.extras
import uuid
from datetime import datetime
from flask import Flask, render_template, request, g, send_from_directory, abort, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from functools import wraps
from dotenv import load_dotenv

load_dotenv() 
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'default-secret-key'),
    UPLOAD_FOLDER='uploads',
    DATABASE_URL=os.environ.get('DATABASE_URL')
)
if not os.path.exists(app.config['UPLOAD_FOLDER']): os.makedirs(app.config['UPLOAD_FOLDER'])

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(app.config['DATABASE_URL'])
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None: db.close()

def init_db():
    # ... (código sem alterações)
    pass

# --- LÓGICA DE AUTENTICAÇÃO E ROTAS DE INTERFACE (sem alterações) ---
# ...

# --- ROTAS DE PROCESSAMENTO (COM COMMIT EXPLÍCITO) ---
@app.route('/enviar-nascimento', methods=['POST'])
def receber_nascimento():
    db = get_db()
    cursor = db.cursor()
    dados = dict(request.form)
    # ... (resto da lógica para pegar arquivos e montar dados)
    dados['arquivos_dnv'] = salvar_arquivos(request.files.getlist('doc_dnv[]'), 'nascimento')
    dados['arquivos_identidade'] = salvar_arquivos(request.files.getlist('doc_identidade[]'), 'nascimento')
    dados['arquivos_endereco'] = salvar_arquivos(request.files.getlist('doc_endereco[]'), 'nascimento')

    colunas = ', '.join(dados.keys())
    placeholders = ', '.join(['%s'] * len(dados))
    query = f"INSERT INTO nascimentos ({colunas}) VALUES ({placeholders})"
    
    cursor.execute(query, list(dados.values()))
    db.commit() # FORÇA O COMMIT
    cursor.close()
    return "<h1>Dados e documentos de Nascimento salvos com sucesso!</h1>"

@app.route('/enviar-obito', methods=['POST'])
def receber_obito():
    db = get_db()
    cursor = db.cursor()
    dados = dict(request.form)
    # ... (resto da lógica para pegar arquivos e montar dados)
    dados['arquivos_do'] = salvar_arquivos(request.files.getlist('doc_do[]'), 'obito')
    dados['arquivos_falecido'] = salvar_arquivos(request.files.getlist('doc_falecido[]'), 'obito')
    dados['arquivos_declarante'] = salvar_arquivos(request.files.getlist('doc_declarante[]'), 'obito')
    
    colunas = ', '.join(dados.keys())
    placeholders = ', '.join(['%s'] * len(dados))
    query = f"INSERT INTO obitos ({colunas}) VALUES ({placeholders})"
    
    cursor.execute(query, list(dados.values()))
    db.commit() # FORÇA O COMMIT
    cursor.close()
    return "<h1>Dados e documentos de Óbito salvos com sucesso!</h1>"

@app.route('/enviar-casamento', methods=['POST'])
def receber_casamento():
    db = get_db()
    cursor = db.cursor()
    dados = dict(request.form)
    # ... (resto da lógica para pegar arquivos e montar dados)
    dados['arquivos_noivo1_id'] = salvar_arquivos(request.files.getlist('doc_noivo1_id[]'), 'casamento')
    dados['arquivos_noivo1_end'] = salvar_arquivos(request.files.getlist('doc_noivo1_end[]'), 'casamento')
    dados['arquivos_noivo2_id'] = salvar_arquivos(request.files.getlist('doc_noivo2_id[]'), 'casamento')
    dados['arquivos_noivo2_end'] = salvar_arquivos(request.files.getlist('doc_noivo2_end[]'), 'casamento')
    dados['arquivos_test1_id'] = salvar_arquivos(request.files.getlist('doc_test1_id[]'), 'casamento')
    dados['arquivos_test1_end'] = salvar_arquivos(request.files.getlist('doc_test1_end[]'), 'casamento')
    dados['arquivos_test2_id'] = salvar_arquivos(request.files.getlist('doc_test2_id[]'), 'casamento')
    dados['arquivos_test2_end'] = salvar_arquivos(request.files.getlist('doc_test2_end[]'), 'casamento')
    
    colunas = ', '.join(dados.keys())
    placeholders = ', '.join(['%s'] * len(dados))
    query = f"INSERT INTO casamentos ({colunas}) VALUES ({placeholders})"
    
    cursor.execute(query, list(dados.values()))
    db.commit() # FORÇA O COMMIT
    cursor.close()
    return "<h1>Dados e documentos de Casamento salvos com sucesso!</h1>"

# --- ROTAS PROTEGIDAS e EXECUÇÃO DO SERVIDOR (sem alterações) ---
# ... (o resto do arquivo continua igual)