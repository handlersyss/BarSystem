from barsystem import SistemaBar, InterfaceTerminal
from auth_system import AuthInterface

class InterfaceBarPersonalizada(InterfaceTerminal):
    def __init__(self, usuario=None):
        super().__init__()
        self.usuario = usuario
        self.nome_sistema = usuario.nome_empresa if usuario else "SISTEMA DE BAR"
    
    def menu_principal(self):
        self.limpar_tela()
        self.imprimir_titulo(self.nome_sistema)
        print("1. Gestão de Mesas")
        print("2. Gestão de Produtos e Estoque")
        print("3. Relatórios")
        print("4. Logout")
        print("0. Sair")
        print(self.linha_separadora())
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            self.menu_mesas()
        elif opcao == "2":
            self.menu_produtos()
        elif opcao == "3":
            self.menu_relatorios()
        elif opcao == "4":
            self.running = False
            return "logout"  # Sinaliza que o usuário deseja fazer logout
        elif opcao == "0":
            self.running = False
        else:
            input("Opção inválida. Pressione Enter para continuar...")
        
        return None

def main():
    auth_interface = AuthInterface()
    
    while True:
        # Iniciar processo de autenticação
        usuario = auth_interface.executar()
        
        # Se o usuário fechou o programa na tela de login
        if not usuario:
            print("Programa encerrado.")
            break
        
        # Iniciar o sistema com o usuário logado
        interface_bar = InterfaceBarPersonalizada(usuario)
        
        resultado = None
        while interface_bar.running:
            resultado = interface_bar.menu_principal()
            
            # Se o resultado for "logout", volta para a tela de login
            if resultado == "logout":
                auth_interface.usuario_logado = None
                auth_interface.running = True
                break
        
        # Se saiu do loop sem logout, então o usuário quer encerrar o programa
        if resultado != "logout":
            break

if __name__ == "__main__":
    main()