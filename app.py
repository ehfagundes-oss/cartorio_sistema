import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, flash, url_for, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_mail import Mail, Message

# --- CONFIGURAÇÃO ---
load_dotenv() 
app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'default-secret-key'),
    UPLOAD_FOLDER='uploads',
    MAIL_SERVER='smtp.sendgrid.net',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='apikey',
    MAIL_PASSWORD=os.environ.get('SENDGRID_API_KEY'),
    MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER')
)

mail = Mail(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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
            nome_original = secure_filename(file.filename)
            extensao = nome_original.rsplit('.', 1)[1].lower()
            nome_unico = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.{extensao}"
            caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], subpasta)
            if not os.path.exists(caminho_salvar):
                os.makedirs(caminho_salvar)
            file.save(os.path.join(caminho_salvar, nome_unico))
            nomes_salvos.append(nome_unico)
    return nomes_salvos

# --- FUNÇÃO PARA FORMATAR E ENVIAR O E-MAIL ---
def enviar_email_registro(titulo, dados_formulario, arquivos_salvos):
    try:
        destinatario = os.environ.get('RECIPIENT_EMAIL')
        if not destinatario:
            print("ERRO: E-mail do destinatário não configurado.")
            return

        msg = Message(titulo, recipients=[destinatario])
        
        html_body = f"<h1>{titulo}</h1>"
        html_body += "<h2>Dados do Formulário:</h2>"
        html_body += "<table border='1' cellpadding='5' style='border-collapse: collapse;'>"
        for chave, valor in dados_formulario.items():
            html_body += f"<tr><td style='background-color: #f2f2f2;'><strong>{chave.replace('_', ' ').title()}</strong></td><td>{valor}</td></tr>"
        html_body += "</table>"
        
        if arquivos_salvos:
            html_body += "<h2>Links para os Documentos:</h2><ul>"
            for subpasta, nomes in arquivos_salvos.items():
                for nome_arquivo in nomes:
                    link = url_for('uploaded_file', subpasta=subpasta, filename=nome_arquivo, _external=True)
                    html_body += f"<li><a href='{link}'>{subpasta.replace('_', ' ').title()} - Arquivo</a></li>"
            html_body += "</ul>"
            
        msg.html = html_body
        mail.send(msg)
        print(f"E-mail '{titulo}' enviado para {destinatario}")
    except Exception as e:
        print(f"!!!!!!!!!! FALHA AO ENVIAR E-MAIL !!!!!