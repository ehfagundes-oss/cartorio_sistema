# ... (todo o código do início até a seção de ROTAS DE PROCESSAMENTO continua o mesmo)
# ... (a função salvar_arquivos também continua a mesma)

# --- ROTAS DE PROCESSAMENTO (FORMATADAS PARA CLAREZA) ---
@app.route('/enviar-nascimento', methods=['POST'])
def receber_nascimento():
    db = get_db()
    cursor = db.cursor()
    
    dados = dict(request.form)
    dados['arquivos_dnv'] = salvar_arquivos(request.files.getlist('doc_dnv[]'), 'nascimento')
    dados['arquivos_identidade'] = salvar_arquivos(request.files.getlist('doc_identidade[]'), 'nascimento')
    dados['arquivos_endereco'] = salvar_arquivos(request.files.getlist('doc_endereco[]'), 'nascimento')
    
    colunas = ', '.join(dados.keys())
    placeholders = ', '.join(['%s'] * len(dados))
    query = f"INSERT INTO nascimentos ({colunas}) VALUES ({placeholders})"
    
    try:
        cursor.execute(query, list(dados.values()))
        db.commit() # Confirma a transação
        print("COMMIT realizado com sucesso para NASCIMENTO.")
    except Exception as e:
        db.rollback() # Desfaz a transação em caso de erro
        print(f"ERRO ao salvar nascimento: {e}")

    cursor.close()
    return "<h1>Dados e documentos de Nascimento salvos com sucesso!</h1>"

@app.route('/enviar-obito', methods=['POST'])
def receber_obito():
    db = get_db()
    cursor = db.cursor()
    
    dados = dict(request.form)
    dados['arquivos_do'] = salvar_arquivos(request.files.getlist('doc_do[]'), 'obito')
    dados['arquivos_falecido'] = salvar_arquivos(request.files.getlist('doc_falecido[]'), 'obito')
    dados['arquivos_declarante'] = salvar_arquivos(request.files.getlist('doc_declarante[]'), 'obito')
    
    colunas = ', '.join(dados.keys())
    placeholders = ', '.join(['%s'] * len(dados))
    query = f"INSERT INTO obitos ({colunas}) VALUES ({placeholders})"
    
    try:
        cursor.execute(query, list(dados.values()))
        db.commit()
        print("COMMIT realizado com sucesso para ÓBITO.")
    except Exception as e:
        db.rollback()
        print(f"ERRO ao salvar óbito: {e}")
        
    cursor.close()
    return "<h1>Dados e documentos de Óbito salvos com sucesso!</h1>"

@app.route('/enviar-casamento', methods=['POST'])
def receber_casamento():
    db = get_db()
    cursor = db.cursor()
    
    dados = dict(request.form)
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

    try:
        cursor.execute(query, list(dados.values()))
        db.commit()
        print("COMMIT realizado com sucesso para CASAMENTO.")
    except Exception as e:
        db.rollback()
        print(f"ERRO ao salvar casamento: {e}")

    cursor.close()
    return "<h1>Dados e documentos de Casamento salvos com sucesso!</h1>"

# ... (o resto do app.py, com o painel de admin e detalhes, continua igual)
