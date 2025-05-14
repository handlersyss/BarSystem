import os
import json
import shutil
import getpass
import sqlite3
import bcrypt
from typing import Dict, Optional

class Usuario:
    def __init__(self, id: int, nome_usuario: str, senha_hash: str, nome_empresa: str):
        self.id = id
        self.nome_usuario = nome_usuario
        self.senha_hash = senha_hash
        self.nome_empresa = nome_empresa
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome_usuario": self.nome_usuario,
            "senha_hash": self.senha_hash,
            "nome_empresa": self.nome_empresa
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            nome_usuario=data["nome_usuario"],
            senha_hash=data["senha_hash"],
            nome_empresa=data["nome_empresa"]
        )


class SistemaAutenticacao:
    def __init__(self):
        self.db_path = 'bar_system.db'
        self.usuarios: Dict[int, Usuario] = {}
        self.proximo_id_usuario = 1
        self.carregar_dados()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def _hash_senha(self, senha: str) -> str:
        """Gera um hash da senha usando bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')
    
    def _verificar_senha(self, senha: str, senha_hash: str) -> bool:
        """Verifica se a senha corresponde ao hash."""
        return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))
    
    def carregar_dados(self):
        """Carrega os dados de usuários a partir do banco de dados."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Carregar usuarios
                cursor.execute('SELECT id, nome_usuario, senha_hash, nome_empresa FROM usuarios')
                for row in cursor.fetchall():
                    usuario = Usuario(id=row[0], nome_usuario=row[1], senha_hash=row[2], nome_empresa=row[3])
                    self.usuarios[usuario.id] = usuario

                # Carregar contador
                cursor.execute('SELECT valor FROM contadores WHERE nome = ?', ('proximo_id_usuario',))
                result = cursor.fetchone()
                if result:
                    self.proximo_id_usuario = result[0]

        except sqlite3.Error as e:
            print(f"Erro ao carregar dados de usuários: {e}")
            print("Iniciando com dados vazios.")
    
    def salvar_dados(self):
        """Salva o contador de usuários no banco SQLite."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO contadores (nome, valor)
                    VALUES (?, ?)
                ''', ('proximo_id_usuario', self.proximo_id_usuario))
                conn.commit()
        
        except sqlite3.Error as e:
            print(f"Erro ao salvar dados: {e}")
    
    def cadastrar_usuario(self, nome_usuario: str, senha: str, nome_empresa: str) -> Optional[Usuario]:
        """Cadastra um novo usuário no sistema."""
        # Verifica se o nome de usuário já existe
        for usuario in self.usuarios.values():
            if usuario.nome_usuario == nome_usuario:
                return None
        
        # Gera o hash da senha
        senha_hash = self._hash_senha(senha)
        
        # Cria um novo usuário
        usuario = Usuario(
            id=self.proximo_id_usuario,
            nome_usuario=nome_usuario,
            senha_hash=senha_hash,
            nome_empresa=nome_empresa
        )
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO usuarios (id, nome_usuario, senha_hash, nome_empresa)
                    VALUES (?, ?, ?, ?)
                ''', (usuario.id, usuario.nome_usuario, usuario.senha_hash, usuario.nome_empresa))
                conn.commit()
                
                self.usuarios[usuario.id] = usuario
                self.proximo_id_usuario += 1
                self.salvar_dados()
                return usuario
        
        except sqlite3.Error as e:
            print(f"Erro ao cadastrar usuário: {e}")
            return None
        
    def autenticar(self, nome_usuario: str, senha: str) -> Optional[Usuario]:
        """Autentica um usuário com base no nome de usuário e senha."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, nome_usuario, senha_hash, nome_empresa
                    FROM usuarios
                    WHERE nome_usuario = ?
                ''', (nome_usuario,))
                row = cursor.fetchone()
                
                if row and self._verificar_senha(senha, row[2]):
                    return Usuario(id=row[0], nome_usuario=row[1], senha_hash=row[2], nome_empresa=row[3])
                return None
        
        except sqlite3.Error as e:
            print(f"Erro ao autenticar usuário: {e}")
            return None

class AuthInterface:
    def __init__(self):
        self.sistema = SistemaAutenticacao()
        self.running = True
        self.usuario_logado = None

    def limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def linha_separadora(self):
        colunas, _ = os.get_terminal_size()
        return "=" * colunas

    def imprimir_titulo(self, titulo):
        colunas, _ = os.get_terminal_size()
        borda = "=" * colunas
        titulo_ascii = f"""
        ╔{'═' * (len(titulo) + 10)}╗
        ║     {titulo}     ║
        ╚{'═' * (len(titulo) + 10)}╝
        """
        print(borda)
        for linha in titulo_ascii.split('\n'):
            espacos = (colunas - len(linha)) // 2
            print(" " * espacos + linha)
        print(borda)

    def menu_principal(self):
        self.limpar_tela()
        self.imprimir_titulo("SISTEMA DE AUTENTICAÇÃO")
        print("1. Login")
        print("2. Cadastrar Novo Usuário")
        print("0. Sair")
        print(self.linha_separadora())
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            self.login()
        elif opcao == "2":
            self.cadastrar_usuario()
        elif opcao == "0":
            self.running = False
        else:
            input("Opção inválida. Pressione Enter para continuar...")
    
    def login(self):
        self.limpar_tela()
        self.imprimir_titulo("LOGIN")
        print("Digite 'c' ou 'cancelar' para voltar.")
        
        nome_usuario = input("Nome de usuário: ")
        if nome_usuario.lower() in ['c', 'cancelar']:
            return
        
        senha = input("Senha: ")
        if senha.lower() in ['c', 'cancelar']:
            return
        
        usuario = self.sistema.autenticar(nome_usuario, senha)
        if usuario:
            print(f"Login bem-sucedido! Bem-vindo, {usuario.nome_usuario}.")
            self.usuario_logado = usuario
            self.running = False
        else:
            print("Nome de usuário ou senha incorretos.")
        input("Pressione Enter para continuar...")
    
    def cadastrar_usuario(self):
        self.limpar_tela()
        self.imprimir_titulo("CADASTRO DE USUÁRIO")
        print("Digite 'c' ou 'cancelar' para voltar.")
        
        nome_usuario = input("Nome de usuário: ")
        if nome_usuario.lower() in ['c', 'cancelar']:
            return
        
        senha = input("Senha: ")
        if senha.lower() in ['c', 'cancelar']:
            return
        
        nome_empresa = input("Nome da empresa: ")
        if nome_empresa.lower() in ['c', 'cancelar']:
            return
        
        usuario = self.sistema.cadastrar_usuario(nome_usuario=nome_usuario, senha=senha, nome_empresa=nome_empresa)
        if usuario:
            print(f"Usuário {nome_usuario} cadastrado com sucesso!")
        else:
            print("Erro ao cadastrar usuário. Nome de usuário já existe ou erro no banco de dados.")
        input("Pressione Enter para continuar...")
    
    def executar(self):
        self.running = True
        self.usuario_logado = None
        while self.running:
            self.menu_principal()
        return self.usuario_logado