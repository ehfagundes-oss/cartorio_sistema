DROP TABLE IF EXISTS nascimentos;
DROP TABLE IF EXISTS obitos;
DROP TABLE IF EXISTS casamentos;

CREATE TABLE nascimentos (
    id SERIAL PRIMARY KEY, data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP, nome_nascido TEXT, mae_nome TEXT, mae_naturalidade TEXT, mae_estado_civil TEXT, mae_profissao TEXT, mae_endereco TEXT, mae_cep TEXT, mae_telefone TEXT, mae_rg TEXT, mae_cpf TEXT, mae_cnh TEXT, mae_avos TEXT,
    pai_nome TEXT, pai_naturalidade TEXT, pai_estado_civil TEXT, pai_profissao TEXT, pai_endereco TEXT, pai_cep TEXT, pai_telefone TEXT, pai_rg TEXT, pai_cpf TEXT, pai_cnh TEXT, pai_avos TEXT,
    arquivos_dnv TEXT, arquivos_identidade TEXT, arquivos_endereco TEXT
);

CREATE TABLE obitos (
    id SERIAL PRIMARY KEY, data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP, falecido_nome TEXT, falecido_dt_nasc TEXT, falecido_naturalidade TEXT, falecido_estado_civil TEXT, falecido_conjuge TEXT, falecido_profissao TEXT, falecido_rg TEXT, falecido_cpf TEXT, falecido_cnh TEXT, falecido_pais TEXT, falecido_endereco TEXT,
    do_numero TEXT, medico_nome TEXT, medico_crm TEXT, causa_morte TEXT, data_obito TEXT, hora_obito TEXT, local_obito TEXT, local_sepultamento TEXT, era_eleitor TEXT, deixou_testamento TEXT, deixou_bens TEXT, tinha_filhos TEXT, nomes_filhos TEXT,
    declarante_nome TEXT, declarante_profissao TEXT, declarante_estado_civil TEXT, declarante_naturalidade TEXT, declarante_dt_nasc TEXT, declarante_endereco TEXT, declarante_rg TEXT, declarante_cpf TEXT, declarante_cnh TEXT,
    arquivos_do TEXT, arquivos_falecido TEXT, arquivos_declarante TEXT
);

CREATE TABLE casamentos (
    id SERIAL PRIMARY KEY, data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP, noivo1_nome TEXT, noivo1_cpf TEXT, noivo1_rg TEXT, noivo1_cnh TEXT, noivo1_dt_nasc TEXT, noivo1_profissao TEXT, noivo1_naturalidade TEXT, noivo1_estado_civil TEXT, noivo1_endereco TEXT, noivo1_pai TEXT, noivo1_mae TEXT, noivo1_nome_futuro TEXT,
    noivo2_nome TEXT, noivo2_cpf TEXT, noivo2_rg TEXT, noivo2_cnh TEXT, noivo2_dt_nasc TEXT, noivo2_profissao TEXT, noivo2_naturalidade TEXT, noivo2_estado_civil TEXT, noivo2_endereco TEXT, noivo2_pai TEXT, noivo2_mae TEXT, noivo2_nome_futuro TEXT,
    test1_nome TEXT, test1_cpf TEXT, test1_rg TEXT, test1_profissao TEXT, test1_estado_civil TEXT, test1_endereco TEXT,
    test2_nome TEXT, test2_cpf TEXT, test2_rg TEXT, test2_profissao TEXT, test2_estado_civil TEXT, test2_endereco TEXT,
    arquivos_noivo1_id TEXT, arquivos_noivo1_end TEXT, arquivos_noivo2_id TEXT, arquivos_noivo2_end TEXT, arquivos_test1_id TEXT, arquivos_test1_end TEXT, arquivos_test2_id TEXT, arquivos_test2_end TEXT
);