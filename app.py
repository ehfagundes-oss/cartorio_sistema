import os
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, render_template, request, g, send_from_directory, abort
from werkzeug.utils import secure_filename

# --- CONFIGURAÇÃO E BANCO DE DADOS (sem alterações) ---
app = Flask(__name__)
DATABASE = 'cartorio.db'
app.config.update(SECRET_KEY='uma-chave-secreta-muito-segura-12345', UPLOAD_FOLDER='uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']): os.makedirs(app.config['UPLOAD_FOLDER'])
def get_db():
    db = getattr(g, '_database', None)
    if db is None: db = g._database = sqlite3.connect(DATABASE); db.row_factory = sqlite3.Row
    return db
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None: db.close()
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f: db.cursor().executescript(f.read())
        db.commit()
    print("Banco de dados inicializado.")

# --- ROTAS DA INTERFACE (sem alterações) ---
@app.route('/')
def homepage(): return render_template('homepage.html') # Usaremos um template para a homepage
@app.route('/nascimento')
def form_nascimento(): return render_template('formulario_nascimento.html')
@app.route('/obito')
def form_obito(): return render_template('formulario_obito.html')
@app.route('/casamento')
def form_casamento(): return render_template('formulario_casamento.html')

# --- FUNÇÃO AUXILIAR PARA SALVAR ARQUIVOS (sem alterações) ---
def salvar_arquivos(file_storage, subpasta):
    #... (código sem alterações)
    nomes_salvos = []
    for file in file_storage:
        if file and file.filename != '':
            nome_original = secure_filename(file.filename)
            extensao = nome_original.rsplit('.', 1)[1].lower()
            nome_unico = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.{extensao}"
            caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], subpasta)
            if not os.path.exists(caminho_salvar): os.makedirs(caminho_salvar)
            file.save(os.path.join(caminho_salvar, nome_unico))
            nomes_salvos.append(nome_unico)
    return ','.join(nomes_salvos)

# --- ROTAS DE PROCESSAMENTO (Nascimento e Óbito sem alterações) ---
@app.route('/enviar-nascimento', methods=['POST'])
def receber_nascimento():
    # ... (código sem alterações)
    nomes_dnv=salvar_arquivos(request.files.getlist('doc_dnv[]'),'nascimento');nomes_identidade=salvar_arquivos(request.files.getlist('doc_identidade[]'),'nascimento');nomes_endereco=salvar_arquivos(request.files.getlist('doc_endereco[]'),'nascimento')
    dados=dict(request.form);dados['arquivos_dnv']=nomes_dnv;dados['arquivos_identidade']=nomes_identidade;dados['arquivos_endereco']=nomes_endereco
    db=get_db();colunas=', '.join(dados.keys());placeholders=', '.join(['?']*len(dados));query=f"INSERT INTO nascimentos ({colunas}) VALUES ({placeholders})";db.execute(query,list(dados.values()));db.commit()
    return "<h1>Dados e documentos de Nascimento salvos com sucesso!</h1>"

@app.route('/enviar-obito', methods=['POST'])
def receber_obito():
    # ... (código sem alterações)
    nomes_do=salvar_arquivos(request.files.getlist('doc_do[]'),'obito');nomes_falecido=salvar_arquivos(request.files.getlist('doc_falecido[]'),'obito');nomes_declarante=salvar_arquivos(request.files.getlist('doc_declarante[]'),'obito')
    dados=dict(request.form);dados['arquivos_do']=nomes_do;dados['arquivos_falecido']=nomes_falecido;dados['arquivos_declarante']=nomes_declarante
    db=get_db();colunas=', '.join(dados.keys());placeholders=', '.join(['?']*len(dados));query=f"INSERT INTO obitos ({colunas}) VALUES ({placeholders})";db.execute(query,list(dados.values()));db.commit()
    return "<h1>Dados e documentos de Óbito salvos com sucesso!</h1>"

# ROTA DE PROCESSAMENTO DO CASAMENTO (ATUALIZADA)
@app.route('/enviar-casamento', methods=['POST'])
def receber_casamento():
    dados = dict(request.form)
    # Salva todos os arquivos e adiciona ao dicionário
    dados['arquivos_noivo1_id'] = salvar_arquivos(request.files.getlist('doc_noivo1_id[]'), 'casamento')
    dados['arquivos_noivo1_end'] = salvar_arquivos(request.files.getlist('doc_noivo1_end[]'), 'casamento')
    dados['arquivos_noivo2_id'] = salvar_arquivos(request.files.getlist('doc_noivo2_id[]'), 'casamento')
    dados['arquivos_noivo2_end'] = salvar_arquivos(request.files.getlist('doc_noivo2_end[]'), 'casamento')
    dados['arquivos_test1_id'] = salvar_arquivos(request.files.getlist('doc_test1_id[]'), 'casamento')
    dados['arquivos_test1_end'] = salvar_arquivos(request.files.getlist('doc_test1_end[]'), 'casamento')
    dados['arquivos_test2_id'] = salvar_arquivos(request.files.getlist('doc_test2_id[]'), 'casamento')
    dados['arquivos_test2_end'] = salvar_arquivos(request.files.getlist('doc_test2_end[]'), 'casamento')
    
    db = get_db()
    colunas = ', '.join(dados.keys())
    placeholders = ', '.join(['?'] * len(dados))
    query = f"INSERT INTO casamentos ({colunas}) VALUES ({placeholders})"
    db.execute(query, list(dados.values()))
    db.commit()
    return "<h1>Dados e documentos de Casamento salvos com sucesso!</h1>"

# --- PAINEL ADMINISTRATIVO E DETALHES (sem alterações) ---
@app.route('/admin')
def admin_panel():
    # ... (código sem alterações)
    db = get_db();nascimentos=db.execute('SELECT id, nome_nascido, mae_nome, pai_nome FROM nascimentos ORDER BY id DESC').fetchall();obitos=db.execute('SELECT id, falecido_nome, declarante_nome FROM obitos ORDER BY id DESC').fetchall();casamentos=db.execute('SELECT id, noivo1_nome, noivo2_nome FROM casamentos ORDER BY id DESC').fetchall()
    return render_template('admin.html', nascimentos=nascimentos, obitos=obitos, casamentos=casamentos)

@app.route('/nascimento/<int:id>')
def detalhes_nascimento(id):
    # ... (código sem alterações)
    db=get_db();registro=db.execute('SELECT * FROM nascimentos WHERE id = ?',(id,)).fetchone();
    if registro is None:abort(404)
    return render_template('detalhes_nascimento.html',reg=registro)

@app.route('/obito/<int:id>')
def detalhes_obito(id):
    # ... (código sem alterações)
    db=get_db();registro=db.execute('SELECT * FROM obitos WHERE id = ?',(id,)).fetchone();
    if registro is None:abort(404)
    return render_template('detalhes_obito.html',reg=registro)

@app.route('/casamento/<int:id>')
def detalhes_casamento(id):
    # ... (código sem alterações)
    db=get_db();registro=db.execute('SELECT * FROM casamentos WHERE id = ?',(id,)).fetchone();
    if registro is None:abort(404)
    return render_template('detalhes_casamento.html',reg=registro)

@app.route('/uploads/<path:subpasta>/<path:filename>')
def uploaded_file(subpasta, filename):
    caminho = os.path.join(app.config['UPLOAD_FOLDER'], subpasta)
    return send_from_directory(caminho, filename)

# --- EXECUÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    # init_db() 
    app.run(debug=True)