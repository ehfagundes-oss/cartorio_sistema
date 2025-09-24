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
    # COMANDOS SQL FORMATADOS CORRETAMENTE EM MÚLTIPLAS LINHAS
    schema = [
        "DROP TABLE IF EXISTS nascimentos;",
        "DROP TABLE IF EXISTS obitos;",
        "DROP TABLE IF EXISTS casamentos;",
        """
        CREATE TABLE nascimentos (
            id SERIAL PRIMARY KEY, data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP, nome_nascido TEXT, mae_nome TEXT, mae_naturalidade TEXT, mae_estado_civil TEXT, mae_profissao TEXT, mae_endereco TEXT, mae_cep TEXT, mae_telefone TEXT, mae_rg TEXT, mae_cpf TEXT, mae_cnh TEXT, mae_avos TEXT,
            pai_nome TEXT, pai_naturalidade TEXT, pai_estado_civil TEXT, pai_profissao TEXT, pai_endereco TEXT, pai_cep TEXT, pai_telefone TEXT, pai_rg TEXT, pai_cpf TEXT, pai_cnh TEXT, pai_avos TEXT,
            arquivos_dnv TEXT, arquivos_identidade TEXT, arquivos_endereco TEXT
        );
        """,
        """
        CREATE TABLE obitos (
            id SERIAL PRIMARY KEY, data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP, falecido_nome TEXT, falecido_dt_nasc TEXT, falecido_naturalidade TEXT, falecido_estado_civil TEXT, falecido_conjuge TEXT, falecido_profissao TEXT, falecido_rg TEXT, falecido_cpf TEXT, falecido_cnh TEXT, falecido_pais TEXT, falecido_endereco TEXT,
            do_numero TEXT, medico_nome TEXT, medico_crm TEXT, causa_morte TEXT, data_obito TEXT, hora_obito TEXT, local_obito TEXT, local_sepultamento TEXT, era_eleitor TEXT, deixou_testamento TEXT, deixou_bens TEXT, tinha_filhos TEXT, nomes_filhos TEXT,
            declarante_nome TEXT, declarante_profissao TEXT, declarante_estado_civil TEXT, declarante_naturalidade TEXT, declarante_dt_nasc TEXT, declarante_endereco TEXT, declarante_rg TEXT, declarante_cpf TEXT, declarante_cnh TEXT,
            arquivos_do TEXT, arquivos_falecido TEXT, arquivos_declarante TEXT
        );
        """,
        """