import os
import sqlite3

def get_db_conection():
    if not os.path.exists('database'):
        os.makedirs('database')

    if not os.path.exists('database/sqlite.db'):
        conn = sqlite3.connect('database/sqlite.db')
        create_tables(conn)
    else:
        conn = sqlite3.connect('database/sqlite.db')
        create_tables(conn)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS produtos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR NOT NULL,
            descricao TEXT,
            preco TEXT,
            img BLOB,
            imag BLOB,
            image BLOB,
            ativo INTEGER,
            id_categoria INTEGER,
            FOREIGN KEY(id_categoria) REFERENCES
            categorias(id)
        )
        
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS categorias(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR NOT NULL,
            descricao TEXT,
            ativo INTEGER
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR NOT NULL,
            email VARCHAR NOT NULL UNIQUE,
            senha VARCHAR NOT NULL,
            ativo TEXT DEFAULT 'usuario'
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS slides(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slide BLOB,
            status TEXT DEFAULT 'off'
        )
    ''')

        # Criação da tabela de tamanhos
    conn.execute('''
    CREATE TABLE IF NOT EXISTS tamanhos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tamanho TEXT NOT NULL
    )
    ''')

    # Criação da tabela de associação entre produtos e tamanhos
    conn.execute('''
    CREATE TABLE IF NOT EXISTS produto_tamanhos (
        produto_id INTEGER,
        tamanho_id INTEGER,
        FOREIGN KEY (produto_id) REFERENCES produtos (id),
        FOREIGN KEY (tamanho_id) REFERENCES tamanhos (id),
        PRIMARY KEY (produto_id, tamanho_id)
    )
    ''')



    insert(conn)
    conn.commit()

def insert(conn):

    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    if not usuarios:
        conn.execute('''
        INSERT INTO usuarios(nome, email, senha, ativo)
        values("ailson", "ailson@softpop.com.br", "1234", "administrador")
    ''')
        conn.execute('''
        INSERT INTO usuarios(nome, email, senha, ativo)
        values("joaquim", "joaquimpontes45@outlook.com", "5678","administrador")
    ''')