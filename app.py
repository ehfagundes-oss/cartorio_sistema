import os
import psycopg2
import psycopg2.extras
import uuid
from datetime import datetime
from flask import Flask, render_template, request, g, send_from_directory, abort, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from functools import wraps
from dotenv import load_dotenv

# --- CONFIGURAÇÃO E CRIAÇÃO DO APP (sem mudanças) ---
# ...

# --- BANCO DE DADOS POSTGRESQL (sem mudanças) ---
# ...

# --- LÓGICA DE AUTENTICAÇÃO (sem mudanças) ---
# ...

# --- ROTAS DA INTERFACE (sem mudanças) ---
# ...

# --- FUNÇÃO AUXILIAR PARA SALVAR ARQUIVOS (sem mudanças) ---
# ...

# --- ROTAS DE PROCESSAMENTO (COM A MUDANÇA NO NASCIMENTO) ---

@app.route('/enviar-nascimento', methods=['POST'])
def receber_nascimento():
    # TESTE FINAL: SALVANDO APENAS DADOS DE TEXTO
    conn = None
    try:
        print("--- INICIANDO TESTE SEM UPLOAD DE ARQUIVOS ---")
        conn = psycopg2.connect(app.config['DATABASE_URL'])
        cursor = conn.cursor()
        
        # Pega apenas alguns dados de texto do formulário
        nome_nascido = request.form.get('nome_nascido')
        mae_nome = request.form.get('mae_nome')
        pai_nome = request.form.get('pai_nome')

        print(f"Tentando inserir: {nome_nascido}, {mae_nome}, {pai_nome}")
        
        # Query SQL simplificada
        query = "INSERT INTO nascimentos (nome_nascido, mae_nome, pai_nome) VALUES (%s, %s, %s)"
        
        cursor.execute(query, (nome_nascido, mae_nome, pai_nome))
        conn.commit() # Commit
        
        print("!!! SUCESSO NO COMMIT SEM ARQUIVOS !!!")
        
    except Exception as e:
        print(f"!!!!!!!!!! ERRO CRÍTICO NO TESTE SEM ARQUIVOS !!!!!!!!!!")
        print(str(e))
        if conn:
            conn.rollback()
        return "<h1>Ocorreu um erro. Verifique os logs.</h1>", 500
    finally:
        if conn:
            conn.close()
            
    return "<h1>Teste SEM arquivos executado! Verifique o painel /admin.</h1>"


# As outras funções de recebimento permanecem como estavam
@app.route('/enviar-obito', methods=['POST'])
def receber_obito():
    # ... (código original)
    db_conn = get_db(); cursor = db_conn.cursor()
    dados = dict(request.form)
    dados['arquivos_do'] = salvar_arquivos(request.files.getlist('doc_do[]'), 'obito')
    dados['arquivos_falecido'] = salvar_arquivos(request.files.getlist('doc_falecido[]'), 'obito')
    dados['arquivos_declarante'] = salvar_arquivos(request.files.getlist('doc_declarante[]'), 'obito')
    colunas = ', '.join(dados.keys()); placeholders = ', '.join(['%s'] * len(dados))
    query = f"INSERT INTO obitos ({colunas}) VALUES ({placeholders})"
    try:
        cursor.execute(query, list(dados.values())); db_conn.commit()
    except Exception as e:
        db_conn.rollback(); print(f"ERRO ao salvar óbito: {e}")
    finally:
        cursor.close()
    return "<h1>Dados e documentos de Óbito salvos com sucesso!</h1>"


@app.route('/enviar-casamento', methods=['POST'])
def receber_casamento():
    # ... (código original)
    db_conn = get_db(); cursor = db_conn.cursor()
    dados = dict(request.form)
    dados['arquivos_noivo1_id'] = salvar_arquivos(request.files.getlist('doc_noivo1_id[]'), 'casamento'); dados['arquivos_noivo1_end'] = salvar_arquivos(request.files.getlist('doc_noivo1_end[]'), 'casamento')
    dados['arquivos_noivo2_id'] = salvar_arquivos(request.files.getlist('doc_noivo2_id[]'), 'casamento'); dados['arquivos_noivo2_end'] = salvar_arquivos(request.files.getlist('doc_noivo2_end[]'), 'casamento')
    dados['arquivos_test1_id'] = salvar_arquivos(request.files.getlist('doc_test1_id[]'), 'casamento'); dados['arquivos_test1_end'] = salvar_arquivos(request.files.getlist('doc_test1_end[]'), 'casamento')
    dados['arquivos_test2_id'] = salvar_arquivos(request.files.getlist('doc_test2_id[]'), 'casamento'); dados['arquivos_test2_end'] = salvar_arquivos(request.files.getlist('doc_test2_end[]'), 'casamento')
    colunas = ', '.join(dados.keys()); placeholders = ', '.join(['%s'] * len(dados))
    query = f"INSERT INTO casamentos ({colunas}) VALUES ({placeholders})"
    try:
        cursor.execute(query, list(dados.values())); db_conn.commit()
    except Exception as e:
        db_conn.rollback(); print(f"ERRO ao salvar casamento: {e}")
    finally:
        cursor.close()
    return "<h1>Dados e documentos de Casamento salvos com sucesso!</h1>"

# --- O RESTO DO ARQUIVO (ROTAS DE LOGIN, ADMIN, DETALHES, ETC) CONTINUA IGUAL ---
# ...