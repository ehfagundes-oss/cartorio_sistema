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

# FUNÇÃO init_db VOLTA A LER O ARQUIVO schema.sql
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        with app.open_resource('schema.sql', mode='r') as f:
            cursor.execute(f.read())
        db.commit()
        cursor.close()
    print("Banco de dados PostgreSQL inicializado com sucesso a partir do schema.sql.")

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
            if not os.path.exists(caminho_salvar):
                os.makedirs(caminho_salvar)
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
    dados['arquivos_noivo1_end'] = salvar_arquivos(request.files.getlist('doc_noivo1_end[]'), 'casamento')
    dados['arquivos_noivo2_id'] = salvar_arquivos(request.files.getlist('doc_noivo2_id[]'), 'casamento')
    dados['arquivos_noivo2_end'] = salvar_arquivos(request.files.getlist('doc_noivo2_end[]'), 'casamento')
    dados['arquivos_test1_id'] = salvar_arquivos(request.files.getlist('doc_test1_id[]'), 'casamento')
    dados['arquivos_test1_end'] = salvar_arquivos(request.files.getlist('doc_test1_end[]'), 'casamento')
    dados['arquivos_test2_id'] = salvar_arquivos(request.files.getlist('doc_test2_id[]'), 'casamento')
    dados['arquivos_test2_end'] = salvar_arquivos(request.files.getlist('doc_test2_end[]'), 'casamento')
    colunas = ', '.join(dados.keys()); placeholders = ', '.join(['%s'] * len(dados))
    query = f"INSERT INTO casamentos ({colunas}) VALUES ({placeholders})"
    cursor.execute(query, list(dados.values())); db.commit(); cursor.close()
    return "<h1>Dados e documentos de Casamento salvos com sucesso!</h1>"

# --- ROTAS PROTEGIDAS ---
@app.route('/admin')
@login_required
def admin_panel():
    db = get_db(); cursor = db.cursor()
    cursor.execute('SELECT id, nome_nascido, mae_nome, pai_nome FROM nascimentos ORDER BY id DESC'); nascimentos = cursor.fetchall()
    cursor.execute('SELECT id, falecido_nome, declarante_nome FROM obitos ORDER BY id DESC'); obitos = cursor.fetchall()
    cursor.execute('SELECT id, noivo1_nome, noivo2_nome FROM casamentos ORDER BY id DESC'); casamentos = cursor.fetchall()
    cursor.close()
    return render_template('admin.html', nascimentos=nascimentos, obitos=obitos, casamentos=casamentos)

@app.route('/nascimento/<int:id>')
@login_required
def detalhes_nascimento(id):
    db = get_db(); cursor = db.cursor()
    cursor.execute('SELECT * FROM nascimentos WHERE id = %s', (id,)); registro = cursor.fetchone(); cursor.close()
    if registro is None: abort(404)
    return render_template('detalhes_nascimento.html', reg=registro)

@app.route('/obito/<int:id>')
@login_required
def detalhes_obito(id):
    db = get_db(); cursor = db.cursor()
    cursor.execute('SELECT * FROM obitos WHERE id = %s', (id,)); registro = cursor.fetchone(); cursor.close()
    if registro is None: abort(404)
    return render_template('detalhes_obito.html', reg=registro)

@app.route('/casamento/<int:id>')
@login_required
def detalhes_casamento(id):
    db = get_db(); cursor = db.cursor()
    cursor.execute('SELECT * FROM casamentos WHERE id = %s', (id,)); registro = cursor.fetchone(); cursor.close()
    if registro is None: abort(404)
    return render_template('detalhes_casamento.html', reg=registro)

@app.route('/uploads/<path:subpasta>/<path:filename>')
@login_required
def uploaded_file(subpasta, filename):
    caminho = os.path.join(app.config['UPLOAD_FOLDER'], subpasta)
    return send_from_directory(caminho, filename)

# --- EXECUÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    app.run(debug=True)