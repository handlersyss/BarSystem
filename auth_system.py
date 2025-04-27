import os
import json
import shutil
import getpass
from typing import Dict, Optional

class Usuario:
    def __init__(self, id: int, nome_usuario: str, senha: str, nome_empresa: str):
        self.id = id
        self.nome_usuario = nome_usuario
        self.senha = senha
        self.nome_empresa = nome_empresa
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome_usuario": self.nome_usuario,
            "senha": self.senha,
            "nome_empresa": self.nome_empresa
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            nome_usuario=data["nome_usuario"],
            senha=data["senha"],
            nome_empresa=data["nome_empresa"]
        )


class SistemaAutenticacao:
    def __init__(self):
        self.usuarios: Dict[int, Usuario] = {}
        self.proximo_id_usuario = 1
        self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega os dados de usuários a partir de arquivos JSON."""
        try:
            os.makedirs("dados", exist_ok=True)
            
            if os.path.exists("dados/usuarios.json"):
                with open("dados/usuarios.json", "r", encoding="utf-8") as f:
                    usuarios_dict = json.load(f)
                    self.usuarios = {int(uid): Usuario.from_dict(u) for uid, u in usuarios_dict.items()}
            
            if os.path.exists("dados/contador_usuario.json"):
                with open("dados/contador_usuario.json", "r", encoding="utf-8") as f:
                    contador = json.load(f)
                    self.proximo_id_usuario = contador.get("proximo_id_usuario", 1)
        
        except Exception as e:
            print(f"Erro ao carregar dados de usuários: {e}")
            print("Iniciando com dados vazios.")
    
    def salvar_dados(self):
        """Salva os dados de usuários em arquivos JSON."""
        os.makedirs("dados", exist_ok=True)
        
        # Salva usuários
        with open("dados/usuarios.json", "w", encoding="utf-8") as f:
            usuarios_dict = {str(uid): u.to_dict() for uid, u in self.usuarios.items()}
            json.dump(usuarios_dict, f, ensure_ascii=False, indent=2)
        
        # Salva contador
        with open("dados/contador_usuario.json", "w", encoding="utf-8") as f:
            json.dump({
                "proximo_id_usuario": self.proximo_id_usuario
            }, f, ensure_ascii=False, indent=2)
    
    def cadastrar_usuario(self, nome_usuario: str, senha: str, nome_empresa: str) -> Optional[Usuario]:
        """Cadastra um novo usuário no sistema."""
        # Verifica se o nome de usuário já existe
        for usuario in self.usuarios.values():
            if usuario.nome_usuario == nome_usuario:
                return None
        
        # Cria um novo usuário
        usuario = Usuario(
            id=self.proximo_id_usuario,
            nome_usuario=nome_usuario,
            senha=senha,
            nome_empresa=nome_empresa
        )
        
        self.usuarios[usuario.id] = usuario
        self.proximo_id_usuario += 1
        self.salvar_dados()
        return usuario
    
    def autenticar(self, nome_usuario: str, senha: str) -> Optional[Usuario]:
        """Autentica um usuário com base no nome de usuário e senha."""
        for usuario in self.usuarios.values():
            if usuario.nome_usuario == nome_usuario and usuario.senha == senha:
                return usuario
        return None


class AuthInterface:
    def __init__(self):
        self.sistema_auth = SistemaAutenticacao()
        self.running = True
        self.usuario_logado = None
    
    def linha_separadora(self):
        """Retorna uma linha separadora para melhorar a visualização do terminal."""
        colunas, _ = shutil.get_terminal_size()
        return "=" * colunas
    
    def imprimir_titulo(self, titulo):
        """Imprime um título centralizado."""
        colunas, _ = shutil.get_terminal_size()
        #Criar uma borda decorativa para o título
        borda = "=" * colunas

        # Arte ASCII para o título
        titulo_ascii = f"""
        ╔{'═' * (len(titulo) + 10)}╗
        ║     {titulo}     ║
        ╚{'═' * (len(titulo) + 10)}╝
        """
        print(borda)

        # Centralizar a arte ASCII do título
        for linha in titulo_ascii.split('\n'):
            espacos = (colunas - len(linha)) // 2
            print(" " * espacos + linha)
        
        print(borda)

    def limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def executar(self):
        while self.running and not self.usuario_logado:
            self.tela_autenticacao()
        
        return self.usuario_logado
    
    def tela_autenticacao(self):
        self.limpar_tela()
        self.imprimir_titulo("SISTEMA DE GESTÃO DE BAR")
        print("1. Cadastrar Novo Usuário")
        print("2. Login")
        print("0. Sair")
        print(self.linha_separadora())
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            self.cadastrar_usuario()
        elif opcao == "2":
            self.login()
        elif opcao == "0":
            self.running = False
        else:
            input("Opção inválida. Pressione Enter para continuar...")
    
    def cadastrar_usuario(self):
        self.limpar_tela()
        self.imprimir_titulo("CADASTRO DE USUÁRIO")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar.")
        
        nome_usuario_input = input("Nome de usuário: ")
        if nome_usuario_input.lower() in ["c", "cancelar"]:
            return
        
        if not nome_usuario_input:
            input("Nome de usuário não pode ser vazio. Pressione Enter para continuar...")
            return
        
        nome_empresa_input = input("Nome da empresa: ")
        if nome_empresa_input.lower() in ["c", "cancelar"]:
            return
        
        if not nome_empresa_input:
            input("Nome da empresa não pode ser vazio. Pressione Enter para continuar...")
            return
        
        senha_input = getpass.getpass("Senha: ")
        if senha_input.lower() in ["c", "cancelar"]:
            return
        
        if not senha_input:
            input("Senha não pode ser vazia. Pressione Enter para continuar...")
            return
        
        confirmar_senha = getpass.getpass("Confirme a senha: ")
        if confirmar_senha != senha_input:
            input("As senhas não coincidem. Pressione Enter para continuar...")
            return
        
        usuario = self.sistema_auth.cadastrar_usuario(nome_usuario_input, senha_input, nome_empresa_input)
        
        if usuario:
            input(f"Usuário cadastrado com sucesso! Seu ID é: {usuario.id}. Pressione Enter para continuar...")
        else:
            input("Erro ao cadastrar usuário. Nome de usuário já existe. Pressione Enter para continuar...")
    
    def login(self):
        self.limpar_tela()
        self.imprimir_titulo("LOGIN")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar.")
        
        nome_usuario_input = input("Nome de usuário: ")
        if nome_usuario_input.lower() in ["c", "cancelar"]:
            return
        
        senha_input = getpass.getpass("Senha: ")
        if senha_input.lower() in ["c", "cancelar"]:
            return
        
        usuario = self.sistema_auth.autenticar(nome_usuario_input, senha_input)
        
        if usuario:
            self.usuario_logado = usuario
            input(f"Bem-vindo, {usuario.nome_usuario}! Pressione Enter para continuar...")
        else:
            input("Nome de usuário ou senha incorretos. Pressione Enter para continuar...")