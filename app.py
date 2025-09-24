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

# --- LÓGICA DE AUTENTICAÇÃO ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session: return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'senha123':
            session['logged_in'] = True; return redirect(url_for('admin_panel'))
        else:
            flash('Usuário ou senha inválidos.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None); return redirect(url_for('login'))

# --- ROTAS DA INTERFACE ---
@app.route('/')
def homepage(): 
    return render_template('homepage.html')
@app.route('/nascimento')
def form_nascimento(): 
    return render_template('formulario_nascimento.html')
@app.route('/obito')
def form_obito(): 
    return render_template('formulario_obito.html')
@app.route('/casamento')
def form_casamento(): 
    return render_template('formulario_casamento.html')

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
    conn = None
    try:
        print("--- INICIANDO TESTE COM AUTOCOMMIT ---")
        conn = psycopg2.connect(app.config['DATABASE_URL'])
        conn.autocommit = True
        
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

@app.route('/enviar-obito', methods=['POST'])
def receber_obito():
    return "<h1>Função de Óbito temporariamente desabilitada para teste.</h1>"

@app.route('/enviar-casamento', methods=['POST'])
def receber_casamento():
    return "<h1>Função de Casamento temporariamente desabilitada para teste.</h1>"

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
    db=get_db();cursor=db.cursor();cursor.execute('SELECT * FROM nascimentos WHERE id = %s',(id,));registro=cursor.fetchone();cursor.close()
    if registro is None: abort(404)
    return render_template('detalhes_nascimento.html',reg=registro)

@app.route('/obito/<int:id>')
@login_required
def detalhes_obito(id):
    db=get_db();cursor=db.cursor();cursor.execute('SELECT * FROM obitos WHERE id = %s',(id,));registro=cursor.fetchone();cursor.close()
    if registro is None: abort(404)
    return render_template('detalhes_obito.html',reg=registro)

@app.route('/casamento/<int:id>')
@login_required
def detalhes_casamento(id):
    db=get_db();cursor=db.cursor();cursor.execute('SELECT * FROM casamentos WHERE id = %s',(id,));registro=cursor.fetchone();cursor.close()
    if registro is None: abort(404)
    return render_template('detalhes_casamento.html',reg=registro)

@app.route('/uploads/<path:subpasta>/<path:filename>')
@login_required
def uploaded_file(subpasta, filename):
    caminho = os.path.join(app.config['UPLOAD_FOLDER'], subpasta)
    return send_from_directory(caminho, filename)

if __name__ == '__main__':
    app.run(debug=True)