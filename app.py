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
# Carrega as variáveis do arquivo .env
load_dotenv() 

# Cria a aplicação Flask. Esta linha PRECISA vir antes das rotas.
app = Flask(__name__)

# Configura as chaves e pastas a partir das variáveis de ambiente ou valores padrão
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'chave-padrao-para-desenvolvimento-local'),
    UPLOAD_FOLDER='uploads',
    DATABASE_URL=os.environ.get('DATABASE_URL')
)

# Garante que a pasta de uploads exista
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# --- BANCO DE DADOS POSTGRESQL ---
def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(app.config['DATABASE_URL'], cursor_factory=psycopg2.extras.DictCursor)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    # ... (código da função init_db sem alterações)
    schema = [
        "DROP TABLE IF EXISTS nascimentos;", "DROP TABLE IF EXISTS obitos;", "DROP TABLE IF EXISTS casamentos;",
        """CREATE TABLE nascimentos (id SERIAL PRIMARY KEY, data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP, nome_nascido TEXT, mae_nome TEXT, mae_naturalidade TEXT, mae_estado_civil TEXT, mae_profissao TEXT, mae_endereco TEXT, mae_cep TEXT, mae_telefone TEXT, mae_rg TEXT, mae_cpf TEXT, mae_cnh TEXT, mae_avos TEXT, pai_nome TEXT, pai_naturalidade TEXT, pai_estado_civil TEXT, pai_profissao TEXT, pai_endereco TEXT, pai_cep TEXT, pai_telefone TEXT, pai_rg TEXT, pai_cpf TEXT, pai_cnh TEXT, pai_avos TEXT, arquivos_dnv TEXT, arquivos_identidade TEXT, arquivos_endereco TEXT);""",
        """CREATE TABLE obitos (id SERIAL PRIMARY KEY, data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP, falecido_nome TEXT, falecido_dt_nasc TEXT, falecido_naturalidade TEXT, falecido_estado_civil TEXT, falecido_conjuge TEXT, falecido_profissao TEXT, falecido_rg TEXT, falecido_cpf TEXT, falecido_cnh TEXT, falecido_pais TEXT, falecido_endereco TEXT, do_numero TEXT, medico_nome TEXT, medico_crm TEXT, causa_morte TEXT, data_obito TEXT, hora_obito TEXT, local_obito TEXT, local_sepultamento TEXT, era_eleitor TEXT, deixou_testamento TEXT, deixou_bens TEXT, tinha_filhos TEXT, nomes_filhos TEXT, declarante_nome TEXT, declarante_profissao TEXT, declarante_estado_civil TEXT, declarante_naturalidade TEXT, declarante_dt_nasc TEXT, declarante_endereco TEXT, declarante_rg TEXT, declarante_cpf TEXT, declarante_cnh TEXT, arquivos_do TEXT, arquivos_falecido TEXT, arquivos_declarante TEXT);""",
        """CREATE TABLE casamentos (id SERIAL PRIMARY KEY, data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP, noivo1_nome TEXT, noivo1_cpf TEXT, noivo1_rg TEXT, noivo1_cnh TEXT, noivo1_dt_nasc TEXT, noivo1_profissao TEXT, noivo1_naturalidade TEXT, noivo1_estado_civil TEXT, noivo1_endereco TEXT, noivo1_pai TEXT, noivo1_mae TEXT, noivo1_nome_futuro TEXT, noivo2_nome TEXT, noivo2_cpf TEXT, noivo2_rg TEXT, noivo2_cnh TEXT, noivo2_dt_nasc TEXT, noivo2_profissao TEXT, noivo2_naturalidade TEXT, noivo2_estado_civil TEXT, noivo2_endereco TEXT, noivo2_pai TEXT, noivo2_mae TEXT, noivo2_nome_futuro TEXT, test1_nome TEXT, test1_cpf TEXT, test1_rg TEXT, test1_profissao TEXT, test1_estado_civil TEXT, test1_endereco TEXT, test2_nome TEXT, test2_cpf TEXT, test2_rg TEXT, test2_profissao TEXT, test2_estado_civil TEXT, test2_endereco TEXT, arquivos_noivo1_id TEXT, arquivos_noivo1_end TEXT, arquivos_noivo2_id TEXT, arquivos_noivo2_end TEXT, arquivos_test1_id TEXT, arquivos_test1_end TEXT, arquivos_test2_id TEXT, arquivos_test2_end TEXT);"""
    ]
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        for statement in schema:
            cursor.execute(statement)
        db.commit()
        cursor.close()
    print("Banco de dados PostgreSQL inicializado com sucesso diretamente do app.py.")

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
def form_nascimento(): return render_template('formulario_nascimento.html')
@app.route('/obito')
def form_obito(): return render_template('formulario_obito.html')
@app.route('/casamento')
def form_casamento(): return render_template('formulario_casamento.html')

# --- FUNÇÃO AUXILIAR PARA SALVAR ARQUIVOS ---
def salvar_arquivos(file_storage, subpasta):
    nomes_salvos=[]
    for file in file_storage:
        if file and file.filename!='':
            nome_original = secure_filename(file.filename);extensao = nome_original.rsplit('.', 1)[1].lower()
            nome_unico = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.{extensao}"
            caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], subpasta)
            if not os.path.exists(caminho_salvar): os.makedirs(caminho_salvar)
            file.save(os.path.join(caminho_salvar, nome_unico));nomes_salvos.append(nome_unico)
    return ','.join(nomes_salvos)

# --- ROTAS DE PROCESSAMENTO ---
@app.route('/enviar-nascimento', methods=['POST'])
def receber_nascimento():
    db = get_db(); cursor = db.cursor()
    dados = dict(request.form)
    dados['arquivos_dnv'] = salvar_arquivos(request.files.getlist('doc_dnv[]'), 'nascimento')
    dados['arquivos_identidade'] = salvar_arquivos(request.files.getlist('doc_identidade[]'), 'nascimento')
    dados['arquivos_endereco'] = salvar_arquivos(request.files.getlist('doc_endereco[]'), 'nascimento')
    colunas = ', '.join(dados.keys()); placeholders = ', '.join(['%s'] * len(dados))
    query = f"INSERT INTO nascimentos ({colunas}) VALUES ({placeholders})"
    cursor.execute(query, list(dados.values())); db.commit(); cursor.close()
    return "<h1>Dados e documentos de Nascimento salvos com sucesso!</h1>"

@app.route('/enviar-obito', methods=['POST'])
def receber_obito():
    db = get_db(); cursor = db.cursor()
    dados = dict(request.form)
    dados['arquivos_do'] = salvar_arquivos(request.files.getlist('doc_do[]'), 'obito')
    dados['arquivos_falecido'] = salvar_arquivos(request.files.getlist('doc_falecido[]'), 'obito')
    dados['arquivos_declarante'] = salvar_arquivos(request.files.getlist('doc_declarante[]'), 'obito')
    colunas = ', '.join(dados.keys()); placeholders = ', '.join(['%s'] * len(dados))
    query = f"INSERT INTO obitos ({colunas}) VALUES ({placeholders})"
    cursor.execute(query, list(dados.values())); db.commit(); cursor.close()
    return "<h1>Dados e documentos de Óbito salvos com sucesso!</h1>"

@app.route('/enviar-casamento', methods=['POST'])
def receber_casamento():
    db = get_db(); cursor = db.cursor()
    dados = dict(request.form)
    dados['arquivos_noivo1_id'] = salvar_arquivos(request.files.getlist('doc_noivo1_id[]'), 'casamento')
    dados['arquivos_noivo1_end'] = salvar_arquivos(request.files.getlist('