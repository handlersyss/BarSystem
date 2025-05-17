import sqlite3
import json
import os

def create_database():
    """Cria o banco de dados e as tabelas necessárias."""
    if os.path.exists('bar_system.db'):
        os.remove('bar_system.db')
        
    conn = sqlite3.connect('bar_system.db')
    cursor = conn.cursor()

    # Criar tabelas
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nome_usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            nome_empresa TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            categoria TEXT NOT NULL,
            estoque INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS mesas (
            id INTEGER PRIMARY KEY,
            comanda_id INTEGER,
            FOREIGN KEY (comanda_id) REFERENCES comandas(id)
        );

        CREATE TABLE IF NOT EXISTS comandas (
            id INTEGER PRIMARY KEY,
            mesa INTEGER NOT NULL,
            status TEXT NOT NULL,
            hora_abertura TEXT NOT NULL,
            hora_fechamento TEXT,
            nome_cliente TEXT,
            FOREIGN KEY (mesa) REFERENCES mesas(id)
        );

        CREATE TABLE IF NOT EXISTS itens_comanda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comanda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            nome_produto TEXT NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (comanda_id) REFERENCES comandas(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );

        CREATE TABLE IF NOT EXISTS contadores (
            nome TEXT PRIMARY KEY,
            valor INTEGER NOT NULL
        );

        -- Inserir contadores iniciais
        INSERT OR IGNORE INTO contadores (nome, valor) VALUES 
            ('proximo_id_usuario', 1),
            ('proximo_id_produto', 1),
            ('proximo_id_comanda', 1);
    ''')

    conn.commit()
    conn.close()

def migrate_data():
    conn = sqlite3.connect('bar_system.db')
    cursor = conn.cursor()

    # Migrate usuarios.json
    if os.path.exists('dados/usuarios.json'):
        with open('dados/usuarios.json', 'r', encoding='utf-8') as f:
            usuarios = json.load(f)
            for user_id, user in usuarios.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO usuarios (id, nome_usuario, senha, nome_empresa)
                    VALUES (?, ?, ?, ?)
                ''', (int(user_id), user['nome_usuario'], user['senha'], user['nome_empresa']))

    # Migrate produtos.json
    if os.path.exists('dados/produtos.json'):
        with open('dados/produtos.json', 'r', encoding='utf-8') as f:
            produtos = json.load(f)
            for prod_id, prod in produtos.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO produtos (id, nome, preco, categoria, estoque)
                    VALUES (?, ?, ?, ?, ?)
                ''', (int(prod_id), prod['nome'], prod['preco'], prod['categoria'], prod['estoque']))

    # Migrate mesas.json
    if os.path.exists('dados/mesas.json'):
        with open('dados/mesas.json', 'r', encoding='utf-8') as f:
            mesas = json.load(f)
            for mesa_id, comanda_id in mesas.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO mesas (id, comanda_id)
                    VALUES (?, ?)
                ''', (int(mesa_id), comanda_id))

    # Migrate comandas.json
    if os.path.exists('dados/comandas.json'):
        with open('dados/comandas.json', 'r', encoding='utf-8') as f:
            comandas = json.load(f)
            for comanda_id, comanda in comandas.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO comandas (id, mesa, status, hora_abertura, hora_fechamento, nome_cliente)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (int(comanda_id), comanda['mesa'], comanda['status'], comanda['hora_abertura'], comanda['hora_fechamento'], comanda.get('nome_cliente')))
                
                # Migrate itens_comanda
                for item in comanda.get('itens', []):
                    cursor.execute('''
                        INSERT INTO itens_comanda (comanda_id, produto_id, quantidade, nome_produto, preco_unitario, subtotal)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (int(comanda_id), item['produto_id'], item['quantidade'], item['nome_produto'], item['preco_unitario'], item['subtotal']))

    # Migrate contadores
    if os.path.exists('dados/contadores.json'):
        with open('dados/contadores.json', 'r', encoding='utf-8') as f:
            contadores = json.load(f)
            for nome, valor in contadores.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO contadores (nome, valor)
                    VALUES (?, ?)
                ''', (nome, valor))

    if os.path.exists('dados/contador_usuario.json'):
        with open('dados/contador_usuario.json', 'r', encoding='utf-8') as f:
            contador_usuario = json.load(f)
            cursor.execute('''
                INSERT OR REPLACE INTO contadores (nome, valor)
                VALUES (?, ?)
            ''', ('proximo_id_usuario', contador_usuario.get('proximo_id_usuario', 1)))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    migrate_data()
    print("Banco de dados criado e dados migrados com sucesso!")