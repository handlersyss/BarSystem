import os
import json
import datetime
import shutil
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

class Produto:
    def __init__(self, id: int, nome: str, preco: float, categoria: str, estoque: int):
        self.id = id
        self.nome = nome
        self.preco = preco
        self.categoria = categoria
        self.estoque = estoque
    
    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "preco": self.preco,
            "categoria": self.categoria,
            "estoque": self.estoque
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            nome=data["nome"],
            preco=data["preco"],
            categoria=data["categoria"],
            estoque=data["estoque"]
        )


class ItemComanda:
    def __init__(self, produto_id: int, quantidade: int, nome_produto: str, preco_unitario: float):
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.nome_produto = nome_produto
        self.preco_unitario = preco_unitario
        self.subtotal = quantidade * preco_unitario
        
    def to_dict(self):
        return {
            "produto_id": self.produto_id,
            "quantidade": self.quantidade,
            "nome_produto": self.nome_produto,
            "preco_unitario": self.preco_unitario,
            "subtotal": self.subtotal
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            produto_id=data["produto_id"],
            quantidade=data["quantidade"],
            nome_produto=data["nome_produto"],
            preco_unitario=data["preco_unitario"]
        )


class Comanda:
    def __init__(self, id: int, mesa: int, status: str = "aberta", hora_abertura: Optional[str] = None):
        self.id = id
        self.mesa = mesa
        self.status = status
        self.hora_abertura = hora_abertura or datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.hora_fechamento = None
        self.itens: List[ItemComanda] = []
    
    def adicionar_item(self, item: ItemComanda):
        # Verifica se o item já existe na comanda
        for i, item_existente in enumerate(self.itens):
            if item_existente.produto_id == item.produto_id:
                # Atualiza a quantidade do item existente
                self.itens[i].quantidade += item.quantidade
                self.itens[i].subtotal = self.itens[i].quantidade * self.itens[i].preco_unitario
                return
        
        # Se o item não existir, adiciona à lista
        self.itens.append(item)
    
    def remover_item(self, produto_id: int, quantidade: int = 1):
        for i, item in enumerate(self.itens):
            if item.produto_id == produto_id:
                if item.quantidade <= quantidade:
                    # Remove o item completamente
                    self.itens.pop(i)
                else:
                    # Reduz a quantidade
                    self.itens[i].quantidade -= quantidade
                    self.itens[i].subtotal = self.itens[i].quantidade * self.itens[i].preco_unitario
                return True
        return False
    
    def calcular_total(self):
        return sum(item.subtotal for item in self.itens)
    
    def fechar_comanda(self):
        self.status = "fechada"
        self.hora_fechamento = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def to_dict(self):
        return {
            "id": self.id,
            "mesa": self.mesa,
            "status": self.status,
            "hora_abertura": self.hora_abertura,
            "hora_fechamento": self.hora_fechamento,
            "itens": [item.to_dict() for item in self.itens]
        }
    
    @classmethod
    def from_dict(cls, data):
        comanda = cls(
            id=data["id"],
            mesa=data["mesa"],
            status=data["status"],
            hora_abertura=data["hora_abertura"]
        )
        comanda.hora_fechamento = data.get("hora_fechamento")
        
        for item_data in data.get("itens", []):
            item = ItemComanda.from_dict(item_data)
            comanda.itens.append(item)
        
        return comanda


class SistemaBar:
    def __init__(self):
        self.produtos: Dict[int, Produto] = {}
        self.comandas: Dict[int, Comanda] = {}
        self.mesas: Dict[int, Optional[int]] = {}  # mesa_id -> comanda_id (None se mesa livre)
        self.proximo_id_produto = 1
        self.proximo_id_comanda = 1
        
        # Inicializa o sistema com algumas mesas
        for i in range(1, 11):
            self.mesas[i] = None
        
        # Carrega dados se existirem
        self.carregar_dados()

    def atualizar_estoque(self, produto_id, estoque):
        return self.editar_produto(produto_id, estoque=estoque)
        
    def salvar_dados(self):
        """Salva os dados do sistema em arquivos JSON."""
        os.makedirs("dados", exist_ok=True)
        
        # Salva produtos
        with open("dados/produtos.json", "w", encoding="utf-8") as f:
            produtos_dict = {str(pid): p.to_dict() for pid, p in self.produtos.items()}
            json.dump(produtos_dict, f, ensure_ascii=False, indent=2)
        
        # Salva comandas
        with open("dados/comandas.json", "w", encoding="utf-8") as f:
            comandas_dict = {str(cid): c.to_dict() for cid, c in self.comandas.items()}
            json.dump(comandas_dict, f, ensure_ascii=False, indent=2)
        
        # Salva mesas
        with open("dados/mesas.json", "w", encoding="utf-8") as f:
            json.dump(self.mesas, f, ensure_ascii=False, indent=2)
        
        # Salva contadores
        with open("dados/contadores.json", "w", encoding="utf-8") as f:
            json.dump({
                "proximo_id_produto": self.proximo_id_produto,
                "proximo_id_comanda": self.proximo_id_comanda
            }, f, ensure_ascii=False, indent=2)

    def carregar_dados(self):
        """Carrega os dados do sistema a partir de arquivos JSON."""
        try:
            # Carrega produtos
            if os.path.exists("dados/produtos.json"):
                with open("dados/produtos.json", "r", encoding="utf-8") as f:
                    produtos_dict = json.load(f)
                    self.produtos = {int(pid): Produto.from_dict(p) for pid, p in produtos_dict.items()}
            
            # Carrega comandas
            if os.path.exists("dados/comandas.json"):
                with open("dados/comandas.json", "r", encoding="utf-8") as f:
                    comandas_dict = json.load(f)
                    self.comandas = {int(cid): Comanda.from_dict(c) for cid, c in comandas_dict.items()}
            
            # Carrega mesas
            if os.path.exists("dados/mesas.json"):
                with open("dados/mesas.json", "r", encoding="utf-8") as f:
                    mesas_dict = json.load(f)
                    self.mesas = {int(mid): cid for mid, cid in mesas_dict.items()}
            
            # Carrega contadores
            if os.path.exists("dados/contadores.json"):
                with open("dados/contadores.json", "r", encoding="utf-8") as f:
                    contadores = json.load(f)
                    self.proximo_id_produto = contadores.get("proximo_id_produto", 1)
                    self.proximo_id_comanda = contadores.get("proximo_id_comanda", 1)
        
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            print("Iniciando com dados vazios.")
    
    def adicionar_produto(self, nome: str, preco: float, categoria: str, estoque: int) -> Produto:
        """Adiciona um novo produto ao sistema."""
        # Encontrar o menor ID disponível

        id_disponivel = 1
        while id_disponivel in self.produtos:
            id_disponivel += 1

        produto = Produto(
            id=id_disponivel,
            nome=nome,
            preco=preco,
            categoria=categoria,
            estoque=estoque
        )
        
        self.produtos[produto.id] = produto
        self.proximo_id_produto = max(self.proximo_id_produto, id_disponivel + 1)
        self.salvar_dados()
        return produto
    
    def editar_produto(self, id: int, nome: str = None, preco: float = None, 
                     categoria: str = None, estoque: int = None) -> bool:
        """Edita um produto existente."""
        if id not in self.produtos:
            return False
        
        produto = self.produtos[id]
        
        if nome is not None:
            produto.nome = nome
        
        if preco is not None:
            produto.preco = preco
        
        if categoria is not None:
            produto.categoria = categoria
        
        if estoque is not None:
            produto.estoque = estoque
        
        self.salvar_dados()
        return True
    
    def remover_produto(self, id: int) -> bool:
        """Remove um produto do sistema."""
        if id not in self.produtos:
            return False
        
        del self.produtos[id]
        self.salvar_dados()
        return True
    
    def abrir_comanda(self, mesa: int) -> Optional[Comanda]:
        """Abre uma nova comanda para uma mesa."""
        if mesa not in self.mesas:
            return None
        
        if self.mesas[mesa] is not None:
            return None  # Mesa já tem uma comanda aberta
        
        comanda = Comanda(
            id=self.proximo_id_comanda,
            mesa=mesa
        )
        
        self.comandas[comanda.id] = comanda
        self.mesas[mesa] = comanda.id
        self.proximo_id_comanda += 1
        self.salvar_dados()
        return comanda
    
    def adicionar_item_comanda(self, comanda_id: int, produto_id: int, quantidade: int) -> bool:
        """Adiciona um item a uma comanda existente."""
        if comanda_id not in self.comandas or produto_id not in self.produtos:
            return False
        
        comanda = self.comandas[comanda_id]
        produto = self.produtos[produto_id]
        
        if comanda.status != "aberta":
            return False  # Não pode adicionar itens a uma comanda fechada
        
        if produto.estoque < quantidade:
            return False  # Estoque insuficiente
        
        # Atualiza o estoque
        produto.estoque -= quantidade
        
        # Adiciona o item à comanda
        item = ItemComanda(
            produto_id=produto_id,
            quantidade=quantidade,
            nome_produto=produto.nome,
            preco_unitario=produto.preco
        )
        
        comanda.adicionar_item(item)
        self.salvar_dados()
        return True
    
    def remover_item_comanda(self, comanda_id: int, produto_id: int, quantidade: int) -> bool:
        """Remove um item de uma comanda existente."""
        if comanda_id not in self.comandas or produto_id not in self.produtos:
            return False
        
        comanda = self.comandas[comanda_id]
        
        if comanda.status != "aberta":
            return False  # Não pode remover itens de uma comanda fechada
        
        # Procura o item na comanda
        for item in comanda.itens:
            if item.produto_id == produto_id:
                # Devolve ao estoque
                self.produtos[produto_id].estoque += min(quantidade, item.quantidade)
                
                # Remove o item da comanda
                resultado = comanda.remover_item(produto_id, quantidade)
                self.salvar_dados()
                return resultado
        
        return False
    
    def fechar_comanda(self, comanda_id: int) -> Optional[float]:
        """Fecha uma comanda e retorna o valor total."""
        if comanda_id not in self.comandas:
            return None
        
        comanda = self.comandas[comanda_id]
        
        if comanda.status != "aberta":
            return None  # Comanda já está fechada
        
        # Fecha a comanda
        comanda.fechar_comanda()
        
        # Libera a mesa
        self.mesas[comanda.mesa] = None
        
        total = comanda.calcular_total()
        self.salvar_dados()
        return total
    
    def consultar_produtos(self, categoria: str = None) -> List[Produto]:
        """Lista os produtos disponíveis, opcionalmente filtrando por categoria."""
        if categoria:
            return [p for p in self.produtos.values() if p.categoria == categoria]
        return list(self.produtos.values())
    
    def listar_comandas_abertas(self) -> List[Comanda]:
        """Lista as comandas abertas."""
        return [c for c in self.comandas.values() if c.status == "aberta"]
    
    def listar_mesas_livres(self) -> List[int]:
        """Lista as mesas sem comandas abertas."""
        return [mesa for mesa, comanda_id in self.mesas.items() if comanda_id is None]
    
    def listar_mesas_ocupadas(self) -> List[int]:
        """Lista as mesas com comandas abertas."""
        return [mesa for mesa, comanda_id in self.mesas.items() if comanda_id is not None]
    
    def obter_comanda_por_mesa(self, mesa: int) -> Optional[Comanda]:
        """Retorna a comanda associada a uma mesa, se existir."""
        if mesa not in self.mesas or self.mesas[mesa] is None:
            return None
        
        comanda_id = self.mesas[mesa]
        return self.comandas.get(comanda_id)
    
    def adicionar_mesa(self, numero_mesa: int) -> bool:
        """Adiciona uma nova mesa ao sistema."""
        if numero_mesa in self.mesas:
            return False
        
        """Adiciona a nova mesa (Inicialmente livre)"""
        self.mesas[numero_mesa] = None
        self.salvar_dados()
        return True
    
    def remover_mesa(self, numero_mesa: int) -> bool:
        """Remover uma mesa existente do sistema."""
        if numero_mesa not in self.mesas:
            return False
        
        del self.mesas[numero_mesa]
        self.salvar_dados()
        return True

class InterfaceTerminal:

    def linha_simples(self):
        colunas, _= shutil.get_terminal_size()
        return "-" * colunas

    def linha_separadora(self):
        """Retorna uma linha separadora para melhorar a visualização do terminal."""
        colunas, _ = shutil.get_terminal_size()
        return "=" * colunas
    
    def imprimir_titulo(self, titulo):
        """Imprime um título centralizado."""
        colunas, _ = shutil.get_terminal_size()
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

    def menu_relatorios(self):
        self.limpar_tela()
        self.imprimir_titulo("RELATÓRIOS")
        print("1. Produtos com Estoque Baixo")
        print("2. Comandas do Dia")
        print("3. Total de Vendas do Dia")
        print("4. Exportar Todos os Relatórios para Excel")
        print("0. Voltar")
        print(self.linha_separadora())

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            self.relatorio_estoque_baixo()
        elif opcao == "2":
            self.relatorio_comandas_dia()
        elif opcao == "3":
            self.relatorio_vendas_dia()
        elif opcao == "4":
            self.exportar_todos_relatorios()
        elif opcao == "0":
            pass
        else:
            input("Opção inválida. Pressione Enter para continuar...")

    def cadastrar_mesa(self):
        self.limpar_tela()
        self.imprimir_titulo("CADASTRO DE MESA")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar.")

        try:
            
            #Listar mesas atuais
            print("Mesas atuais:", ", ".join(map(str, sorted(self.sistema.mesas.keys()))))

            numero_input = input("\nDigite o número da nova mesa: ")
            if numero_input.lower() in ['c', 'cancelar']:
                print("Operação cancelada.")
                print("Pressione Enter para continuar...")
                return 
            
            numero_mesa = int(numero_input)

            if numero_mesa <= 0:
                print("O numero da mesa deve ser positivo.")
                input("Pressione Enter para continuar...")
                return
            
            #Confirmar adição
            confirmar = input(f"Confirma a adição da mesa {numero_mesa}? (s/n): ")
            if confirmar.lower() != 's':
                print("Operacao cancelada.")
                print("Pressione Enter para continuar...")
                return
            
            resultado = self.sistema.adicionar_mesa(numero_mesa)

            if resultado:
                print(f"Mesa {numero_mesa} adicionada com sucesso.") 
            else:
                print(f"Erro, a mesa  {numero_mesa} já existe.")
            
            input("Pressione Enter para continuar...")

        except ValueError:
            print("Entrada inválida. Por favor, digite um número válido.")
            input("Pressione Enter para continuar...")

    def remover_mesa(self):
        self.limpar_tela()
        self.imprimir_titulo("REMOVER MESA")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar.")

        try:
            #Listar mesas atuais
            print("Mesas atuais:", ", ".join(map(str, sorted(self.sistema.mesas.keys()))))

            numero_input = input("\nDigite o número da mesa a ser removida: ")
            if numero_input.lower() in ['c', 'cancelar']:
                print("Operação cancelada.")
                input("Pressione Enter para continuar...")
                return
            
            numero_mesa = int(numero_input)

            if numero_mesa <= 0:
                print("O numero da mesa deve ser positivo.")
                input("Pressione Enter para continuar...")
                return
            
            #Confirmar remoção
            confirmar = input(f"Confirma a remoção da mesa {numero_mesa}? (s/n): ")
            if confirmar.lower() != 's':
                print("Operacao cancelada.")
                print("Pressione Enter para continuar...")
                return
            
            resultado = self.sistema.remover_mesa(numero_mesa)

            if resultado:
                print(f"Mesa {numero_mesa} removida com sucesso.")
            else:
                print(f"Erro, a mesa {numero_mesa} não existe.")
            input("Pressione Enter para continuar...")

        except ValueError:
            print("Entrada inválida. Por favor, digite um número válido.")
            input("Pressione Enter para continuar...")
                

    def relatorio_estoque_baixo(self):
        self.limpar_tela()
        self.imprimir_titulo("RELATÓRIO DE ESTOQUE BAIXO")

        # Define um limite para estoque baixo (por exemplo, menos de 10 unidades)
        limite = 10

        produtos_baixo_estoque = [produto for produto in self.sistema.produtos.values() if produto.estoque < limite]

        if not produtos_baixo_estoque:
            print(f"Não há produtos com estoque baixo de {limite} unidades.")
            input("Pressione Enter para continuar...")
            return
    
        print(f"Produtos com estoque baixo de {limite} unidades:")
        print(f"{'ID':<5} {'Nome':<20} {'Categoria':<15} {'Estoque':<10}")
        print(self.linha_separadora())

        for produto in produtos_baixo_estoque:
            print(f"{produto.id:<15} {produto.nome:<20} {produto.categoria:<15} {produto.estoque:<10}")

        print(self.linha_separadora())
        input("Pressione Enter para continuar...")

    def relatorio_comandas_dia(self):
        self.limpar_tela()
        self.imprimir_titulo("RELATÓRIO DE COMANDAS DO DIA")

        # Obtém a data atual
        hoje = datetime.now().strftime("%d/%m/%y")
        print(f"Data de hoje: {hoje}")

        # Debug - Mostrar todas as comandas e suas datas
        print("Comandas registradas:")
        for comanda_id, comanda in self.sistema.comandas.items():
            print(f"ID: {comanda_id}, Data: {comanda.hora_abertura}, Status: {comanda.status}")

        # Filtra as comandas do dia - criterio mais simples
        Comandas_dia = []
        for comanda in self.sistema.comandas.values():
            if hoje[:5] in comanda.hora_abertura:
                Comandas_dia.append(comanda)

        if not Comandas_dia:
            print(f"Não há comandas registradas hoje ({hoje}).")
            input("Pressione Enter para continuar...")
            return

        print(f"Comandas registradas hoje ({hoje}):")
        print(f"{'ID':<5} {'Nome':<20} {'Hora Abertura':<20} {'Hora Fechamento':<20} {'Total':<10}")
        print(self.linha_separadora())

        for comanda in Comandas_dia:
            total = comanda.calcular_total()
            status = comanda.status
            hora_fechamento = comanda.hora_fechamento or "_"

            print(f"{comanda.id:<5} {comanda.mesa:<5} {status:<10} {comanda.hora_abertura:<20} {hora_fechamento:<20} R${total:<8.2f}")

        print(self.linha_separadora())
        input("Pressione Enter para continuar...")


    def relatorio_vendas_dia(self):
        self.limpar_tela()
        self.imprimir_titulo("RELATÓRIO DE VENDAS DO DIA")

        #Obtém a data atual
        hoje = datetime.now().strftime("%d/%m/%y")
        print(f"Data de hoje: {hoje}")

        #Degub - Mostrar todas as vendas e suas datas
        print("Todas as comandas fechadas:")
        for comanda_id, comanda in self.sistema.comandas.items():
            print(f"ID: {comanda_id}, Data: {comanda.hora_fechamento}, Status: {comanda.status}")

        # Filtra as comandas fechada do dia 
        comandas_fechadas = []
        for comanda in self.sistema.comandas.values():
            if comanda.status == "fechada" and comanda.hora_fechamento and hoje[:5] in comanda.hora_fechamento:
                comandas_fechadas.append(comanda)

        if not comandas_fechadas:
            print(f"Não há comandas fechadas registradas hoje ({hoje}).")
            input("Pressione Enter para continuar...")
            return
    
        # Calcula o total de vendas do dia
        total_vendas = sum(comanda.calcular_total() for c in comandas_fechadas)
        quantidade_comandas = len(comandas_fechadas)
        ticket_medio = total_vendas / quantidade_comandas if quantidade_comandas > 0 else 0

        print(f"Data: {hoje}")
        print(f"Quantidade de comandas fechadas: {quantidade_comandas}")
        print(f"Total de vendas ({hoje}): R${total_vendas:.2f}")
        print(f"Ticket médio ({hoje}): R${ticket_medio:.2f}")

        # Lista as produtos mais vendidos
        produtos_vendidos = {}
        for comanda in comandas_fechadas:
            for item in comanda.itens:
                if item.produto_id not in produtos_vendidos:
                    produtos_vendidos[item.produto_id] = {
                        "nome": item.nome_produto,
                        "quantidade": 0,
                        "total": 0
                    }

                produtos_vendidos[item.produto_id]["quantidade"] += item.quantidade
                produtos_vendidos[item.produto_id]["total"] += item.subtotal

        if produtos_vendidos:
            print("\nProdutos mais vendidos:")
            print(f"{'Nome':<20} {'Quantidade':<10} {'Total':<10}")
            print(self.linha_separadora())

            # Oderna por quantidade
            produtos_odernados = sorted(
                produtos_vendidos.items(),
                key=lambda x: x[1]["quantidade"],
                reverse=True
            )

            for _, produto in produtos_odernados:
                print(f"{produto['nome']:<20}{produto['quantidade']:<10} R${produto['total']:<8.2f}")

        print(self.linha_separadora())
        input("Pressione Enter para continuar...")

    def atualizar_estoque(self):
        self.limpar_tela()
        self.imprimir_titulo("ATUALIZAR ESTOQUE")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar ou digite 'l' ou 'listar' para visualizar os produtos.")

        try:
            produto_id_input = input("Digite o ID do produto: ")

            if produto_id_input.lower() in ["l", "listar"]:
                self.consultar_produtos()
                self.atualizar_estoque()
                return

            if produto_id_input.lower() in ["c", "cancelar"]:
                print("Operação cancelada.")
                input("Pressione Enter para continuar...")
                return
        
            produto_id = int(produto_id_input)
        
            if produto_id not in self.sistema.produtos:
                print("Produto não encotrado.")
                input("Pressione Enter para continuar...")
                return

            produto = self.sistema.produtos[produto_id]

            print(f"Produto: {produto.nome}")
            print(f"Estoque atual: {produto.estoque}")

            novo_estoque_input = input("Digite o novo valor de estoque: ")

            if novo_estoque_input.lower() in ["c", "cancelar"]:
                print("Operação cancelada.")
                input("Pressione Enter para continuar...")
                return
            
            novo_estoque = int(novo_estoque_input)

            if novo_estoque < 0:
                print("O estoque não pode ser negativo.")
                input("Pressione Enter para continuar...")
                return

            confirmar = input(f"Confirma a atualização do estoque de {produto.estoque} para {novo_estoque}? (s/n): ")

            if confirmar.lower() != "s":
                print("Operação cancelada.")
                input("Pressione Enter para continuar...")
                return

            resultado = self.sistema.atualizar_estoque(produto_id, estoque=novo_estoque)

            if resultado:
                print(f"Estoque atualizado para {novo_estoque} unidades.")
            else:
                print("Erro ao atualizar estoque.")

            input("Pressione Enter para continuar...")

        except ValueError:
            print("Valor inválido. Digite um número inteiro.")
            input("Pressione Enter para continuar...")

    def remover_produto(self):
        self.limpar_tela()
        self.imprimir_titulo("REMOVER PRODUTO")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar ou digite 'l' ou 'listar' para visualizar os produtos.")


        try:
            produto_id_input = (input("Digite o ID do produto: "))

            if produto_id_input.lower() in ["l", "listar"]:
                self.consultar_produtos()
                self.remover_produto()
                return

            if produto_id_input.lower() in ["c", "cancelar"]:
                print("Operação cancelada.")
                input("Pressione Enter para continuar...")
                return
            
            Produto_id = int(produto_id_input)

            if Produto_id not in self.sistema.produtos:
                print("Produto não encontrado.")
                input("Pressione Enter para continuar...")
                return
        
            produto = self.sistema.produtos[Produto_id]

            print(f"Produto: {produto.nome}")
            print(f"Estoque atual: {produto.estoque}")
            print(f"Preço: R${produto.preco:.2f}")
            print(f"Categoria: {produto.categoria}")

            confirmar = input("Tem certeza que deseja remover este produto? (s/n): ")

            if confirmar.lower() == "s":
                resultado = self.sistema.remover_produto(Produto_id)

                if resultado:
                    print("Produto removido com sucesso.")
                else:
                    print("Erro ao remover produto.")

            else:
                print("Remoção cancelada.")

            input("Pressione Enter para continuar...")

        except ValueError:
            print("Valor inválido.")
            input("Pressione Enter para continuar...")
            return
        
    def remover_item_comanda(self):
        self.limpar_tela()
        self.imprimir_titulo("REMOVER ITEM DA COMANDA")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar.")

        try:
            # Lista mesas ocupadas
            mesas_ocupadas = self.sistema.listar_mesas_ocupadas()
            if not mesas_ocupadas:
                input("Não há mesas ocupadas. Pressione Enter para continuar...")
                return
            
            print("Mesas Ocupadas:", ", ".join(map(str, mesas_ocupadas)))

            mesa_id_input = input("Digite o número da mesa: ")
            if mesa_id_input.lower() in ["c", "cancelar"]:
                print("Operação cancelada.")
                input("Pressione Enter para continuar...")
                return
            
            mesa_id = int(mesa_id_input)
            comanda = self.sistema.obter_comanda_por_mesa(mesa_id)
            
            if not comanda:
                print("Mesa não encontrada ou sem comanda.")
                input("Pressione Enter para continuar...")
                return

            # Mostra os itens da comanda
            self.limpar_tela()
            print(self.linha_separadora())
            print(f"Comanda #{comanda.id} - Mesa {comanda.mesa}")
            print(f"Aberta em: {comanda.hora_abertura}")
            print(self.linha_separadora())
            
            if not comanda.itens:
                print("Não há itens na comanda.")
                input("Pressione Enter para continuar...")
                return
            
            print(f"{'ID':<5} {'Qtd':<5} {'Produto':<30} {'Preço Unit.':<15} {'Subtotal':<15}")
            print(self.linha_simples())
            
            for i, item in enumerate(comanda.itens, 1):
                print(f"{i:<5} {item.quantidade:<5} {item.nome_produto:<30} R${item.preco_unitario:<13.2f} R${item.subtotal:<13.2f}")
            
            print(self.linha_simples())
            print(f"{'TOTAL:':<36} R${comanda.calcular_total():<13.2f}")
            print(self.linha_separadora())

            item_id_input = input("Digite o número do item a ser removido: ")
            if item_id_input.lower() in ["c", "cancelar"]:
                print("Operação cancelada.")
                input("Pressione Enter para continuar...")
                return
            
            item_id = int(item_id_input)
            if item_id < 1 or item_id > len(comanda.itens):
                print("Item não encontrado na comanda.")
                input("Pressione Enter para continuar...")
                return

            item = comanda.itens[item_id - 1]
            quantidade_input = input(f"Digite a quantidade a remover (máx: {item.quantidade}): ")
            if quantidade_input.lower() in ["c", "cancelar"]:
                print("Operação cancelada.")
                input("Pressione Enter para continuar...")
                return
            
            quantidade = int(quantidade_input)
            if quantidade <= 0 or quantidade > item.quantidade:
                print("Quantidade inválida.")
                input("Pressione Enter para continuar...")
                return

            confirmar = input(f"Confirma a remoção de {quantidade}x {item.nome_produto}? (s/n): ")
            if confirmar.lower() != "s":
                print("Operação cancelada.")
                input("Pressione Enter para continuar...")
                return

            resultado = self.sistema.remover_item_comanda(comanda.id, item.produto_id, quantidade)
            
            if resultado:
                print(f"{quantidade}x {item.nome_produto} removido(s) com sucesso.")
            else:
                print("Erro ao remover item da comanda.")
            
            input("Pressione Enter para continuar...")

        except ValueError:
            print("Valor inválido.")
            input("Pressione Enter para continuar...")

    def executar(self):
        while self.running:
            self.menu_principal()

    def __init__(self):
        self.sistema = SistemaBar()
        self.running = True

    def limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def menu_principal(self):
        self.limpar_tela()
        self.imprimir_titulo("SISTEMA DE BAR")
        print("1. Gestão de Mesas")
        print("2. Gestão de Produtos e Estoque")
        print("3. Relatórios")
        print("0. Sair")
        print(self.linha_separadora())
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            self.menu_mesas()
        elif opcao == "2":
            self.menu_produtos()
        elif opcao == "3":
            self.menu_relatorios()
        elif opcao == "0":
            self.running = False
        else:
            input("Opção inválida. Pressione Enter para continuar...")
    
    def menu_mesas(self):
        while True:
            self.limpar_tela()
            self.imprimir_titulo("GESTÃO DE MESAS")
            
            # Lista mesas livres e ocupadas
            mesas_livres = self.sistema.listar_mesas_livres()
            mesas_ocupadas = self.sistema.listar_mesas_ocupadas()
            
            print("Mesas Livres:", ", ".join(map(str, mesas_livres)) if mesas_livres else "Nenhuma")
            print("Mesas Ocupadas:", ", ".join(map(str, mesas_ocupadas)) if mesas_ocupadas else "Nenhuma")
            print("\n1. Abrir Comanda")
            print("2. Adicionar Produtos a uma Comanda")
            print("3. Visualizar Comanda")
            print("4. Fechar Comanda")
            print("5. Cadastrar Nova Mesa")
            print("6. Remover Mesa")
            print("7. Remover Item da Comanda")
            print("0. Voltar")
            print(self.linha_separadora())
            
            opcao = input("Escolha uma opção: ")
            
            if opcao == "1":
                self.abrir_comanda()
            elif opcao == "2":
                self.adicionar_produtos_comanda()
            elif opcao == "3":
                self.visualizar_comanda()
            elif opcao == "4":
                self.fechar_comanda()
            elif opcao == "5":
                self.cadastrar_mesa()
            elif opcao == "6":
                self.remover_mesa()
            elif opcao == "7":
                self.remover_item_comanda()
            elif opcao == "0":
                break
            else:
                input("Opção inválida. Pressione Enter para continuar...")
    
    def abrir_comanda(self):
        self.limpar_tela()
        self.imprimir_titulo("ABRIR COMANDA")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar.")

        # Lista mesas livres
        mesas_livres = self.sistema.listar_mesas_livres()

        if not mesas_livres:
            input("Não há mesas livres. Pressione Enter para continuar...")
            return
        
        print("Mesas Livres:", ", ".join(map(str, mesas_livres)))
        
        mesas_livres_input = input("Digite o número da mesa: ")
        if mesas_livres_input in ['c', 'cancelar']:
            print("Operação cancelada.")
            input("Pressione Enter para continuar...")
            return

        mesa = int(mesas_livres_input)
        
        if mesa not in mesas_livres:
            input("Mesa inválida ou ocupada. Pressione Enter para continuar...")
            return
        
        comanda = self.sistema.abrir_comanda(mesa)
        
        if comanda:
            print(f"Comanda {comanda.id} aberta para a mesa {mesa}.")
        else:
            print("Erro ao abrir comanda.")
        
        input("Pressione Enter para continuar...")
    
    def adicionar_produtos_comanda(self):
        self.limpar_tela()
        self.imprimir_titulo("ADICIONAR PRODUTOS À COMANDA")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar.")
        
        # Lista mesas ocupadas
        mesas_ocupadas = self.sistema.listar_mesas_ocupadas()
        if not mesas_ocupadas:
            input("Não há mesas ocupadas. Pressione Enter para continuar...")
            return
        
        print("Mesas Ocupadas:", ", ".join(map(str, mesas_ocupadas)))

        mesa_input = input("Digite o número da mesa: ").strip().lower()
        if mesa_input in ['c', 'cancelar']:
            print("Operação cancelada")
            input("Pressione Enter para continuar...")
            return
        
        mesa = int(mesa_input)
        
        if mesa not in mesas_ocupadas:
            input("Mesa inválida ou não ocupada. Pressione Enter para continuar...")
            return
        
        
        comanda = self.sistema.obter_comanda_por_mesa(mesa)
        
        if not comanda:
            input("Comanda não encontrada. Pressione Enter para continuar...")
            return
        
        # Listar produtos disponíveis
        produtos = self.sistema.consultar_produtos()
        
        if not produtos:
            input("Não há produtos cadastrados. Pressione Enter para continuar...")
            return
        
        print("\nProdutos disponíveis:")
        print("-" * 50)
        print(f"{'ID':<5} {'Nome':<20} {'Preço':<10} {'Categoria':<15} {'Estoque':<10}")
        print("-" * 50)
        
        for produto in produtos:
            print(f"{produto.id:<5} {produto.nome:<20} R${produto.preco:<8.2f} {produto.categoria:<15} {produto.estoque:<10}")
        
        print("-" * 50)
        
        # Adicionar produtos à comanda
        while True:
            produto_id = input("\nDigite o ID do produto (ou 0 para finalizar): ")
            
            if produto_id == "0":
                break
            
            try:
                produto_id = int(produto_id)
                
                if produto_id not in self.sistema.produtos:
                    print("Produto não encontrado.")
                    continue
                
                quantidade = int(input("Digite a quantidade: "))
                
                if quantidade <= 0:
                    print("Quantidade deve ser maior que zero.")
                    continue
                
                if self.sistema.produtos[produto_id].estoque < quantidade:
                    print("Estoque insuficiente.")
                    continue
                
                resultado = self.sistema.adicionar_item_comanda(comanda.id, produto_id, quantidade)
                
                if resultado:
                    print(f"{quantidade}x {self.sistema.produtos[produto_id].nome} adicionado(s) à comanda.")
                else:
                    print("Erro ao adicionar item à comanda.")
            
            except ValueError:
                print("Valor inválido.")
        
        input("Pressione Enter para continuar...")
    
    def visualizar_comanda(self):
        self.limpar_tela()
        self.imprimir_titulo("VISUALIZAR COMANDA")

        # Lista mesas ocupadas
        mesas_ocupadas = self.sistema.listar_mesas_ocupadas()
        if not mesas_ocupadas:
            input("Não há mesas ocupadas. Pressione Enter para continuar...")
            return
        
        print("Mesas Ocupadas:", ", ".join(map(str, mesas_ocupadas)))

        mesa = int(input("Digite o número da mesa: "))
        
        if mesa not in mesas_ocupadas:
            input("Mesa inválida ou não ocupada. Pressione Enter para continuar...")
            return
        
        comanda = self.sistema.obter_comanda_por_mesa(mesa)
        
        if not comanda:
            input("Comanda não encontrada. Pressione Enter para continuar...")
            return
        
        self.limpar_tela()
        print (self.linha_separadora())
        print(f"Comanda #{comanda.id} - Mesa {comanda.mesa}")
        print(f"Aberta em: {comanda.hora_abertura}")
        print (self.linha_separadora())
        
        if not comanda.itens:
            print("Não há itens na comanda.")
        else:
            print(f"{'Qtd':<5} {'Produto':<30} {'Preço Unit.':<15} {'Subtotal':<15}")
            print(self.linha_simples())
            
            for item in comanda.itens:
                print(f"{item.quantidade:<5} {item.nome_produto:<30} R${item.preco_unitario:<13.2f} R${item.subtotal:<13.2f}")
            
            print(self.linha_simples())
            print(f"{'TOTAL:':<36} R${comanda.calcular_total():<13.2f}")
        
        print(self.linha_separadora())
        input("Pressione Enter para continuar...")

 

    def fechar_comanda(self):
        self.limpar_tela()
        self.imprimir_titulo("FECHAR COMANDA")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar.")

        # Lista mesas ocupadas
        mesas_ocupadas = self.sistema.listar_mesas_ocupadas()
        if not mesas_ocupadas:
            input("Não há mesas ocupadas. Pressione Enter para continuar...")
            return
        
        print("Mesas Ocupadas:", ", ".join(map(str, mesas_ocupadas)))

        comandas_input = input("Digite o número da mesa: ").strip().lower()
        if comandas_input in ['c', 'cancelar']:
            print("Operação cancelada.")
            input("Pressione Enter para continuar...")
            return

        try:
            mesa = int(comandas_input)
        except ValueError:
            input("Entrada inválida! Digite o número da mesa corretamente. Pressione Enter para continuar...")
            return
        
        if mesa not in mesas_ocupadas:
            input("Mesa inválida ou não ocupada. Pressione Enter para continuar...")
            return
        
        comanda = self.sistema.obter_comanda_por_mesa(mesa)
        
        if not comanda:
            input("Comanda não encontrada. Pressione Enter para continuar...")
            return
        
        # Exibe os detalhes da comanda antes de fechar
        self.limpar_tela()
        print(self.linha_separadora())
        print(f"Comanda #{comanda.id} - Mesa {comanda.mesa}")
        print(f"Aberta em: {comanda.hora_abertura}")
        print(self.linha_separadora())
        
        if not comanda.itens:
            print("Não há itens na comanda.")
            
            confirmar = input("Deseja realmente fechar esta comanda vazia? (s/n): ")
            
            if confirmar.lower() != "s":
                input("Operação cancelada. Pressione Enter para continuar...")
                return
        else:
            print(f"{'Qtd':<5} {'Produto':<30} {'Preço Unit.':<15} {'Subtotal':<15}")
            print("-" * 65)
            
            for item in comanda.itens:
                print(f"{item.quantidade:<5} {item.nome_produto:<30} R${item.preco_unitario:<13.2f} R${item.subtotal:<13.2f}")
            
            print("-" * 65)
            print(f"{'TOTAL:':<36} R${comanda.calcular_total():<13.2f}")
        
        print("=" * 50)
        confirmar = input("Confirma o fechamento da comanda? (s/n): ")
        
        if confirmar.lower() == "s":
            total = self.sistema.fechar_comanda(comanda.id)
            
            if total is not None:
                print(f"Comanda fechada com sucesso. Total: R${total:.2f}")
            else:
                print("Erro ao fechar comanda.")
        else:
            print("Operação cancelada.")
        
        input("Pressione Enter para continuar...")
    
    def menu_produtos(self):
        while True:
            self.limpar_tela()
            self.imprimir_titulo("GESTÃO DE PRODUTOS E ESTOQUE")
            print("1. Cadastrar Novo Produto")
            print("2. Consultar Produtos")
            print("3. Editar Produto")
            print("4. Atualizar Estoque")
            print("5. Remover Produto")
            print("0. Voltar")
            print(self.linha_separadora())
            
            opcao = input("Escolha uma opção: ")
            
            if opcao == "1":
                self.cadastrar_produto()
            elif opcao == "2":
                self.consultar_produtos()
            elif opcao == "3":
                self.editar_produto()
            elif opcao == "4":
                self.atualizar_estoque()
            elif opcao == "5":
                self.remover_produto()
            elif opcao == "0":
                break
            else:
                input("Opção inválida. Pressione Enter para continuar...")
    
    def cadastrar_produto(self):
        self.limpar_tela()
        self.imprimir_titulo("CADASTRO DE PRODUTO")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar.")
        
        try:
            nome_input = input("Nome do produto: ")
            if nome_input.lower() in ["c", "cancelar"]:
                print("Operação cancelada.")
                input("Pressione Enter para continuar...")
                return
  
            nome = nome_input
            
            if not nome:
                print("Nome não pode ser vazio.")
                input("Pressione Enter para continuar...")
                return
            
            preco = float(input("Preço (R$): "))
            
            if preco <= 0:
                print("Preço deve ser maior que zero.")
                input("Pressione Enter para continuar...")
                return
            
            categoria = input("Categoria: ")
            estoque = int(input("Quantidade em estoque: "))
            
            if estoque < 0:
                print("Estoque não pode ser negativo.")
                input("Pressione Enter para continuar...")
                return
            
            produto = self.sistema.adicionar_produto(nome, preco, categoria, estoque)
            
            print(f"Produto '{produto.nome}' cadastrado com ID {produto.id}.")
            input("Pressione Enter para continuar...")
        
        except ValueError:
            print("Valor inválido.")
            input("Pressione Enter para continuar...")
    
    def consultar_produtos(self):
        self.limpar_tela()
        self.imprimir_titulo("LISTAGEM DE PRODUTOS")
        
        # Pedir categoria opcional
        categoria = input("Filtrar por categoria (deixe em branco para listar todos): ")
        
        produtos = self.sistema.consultar_produtos(categoria if categoria else None)
        
        if not produtos:
            print("Nenhum produto encontrado.")
            input("Pressione Enter para continuar...")
            return
        
        # Define as larguras das colunas
        colunas = {
            'id': 5,
            'nome': 30,
            'preco': 12,
            'categoria': 20,
            'estoque': 10
        }
        
        # Cria o cabeçalho
        cabecalho = (
            f"{'ID':<{colunas['id']}} "
            f"{'Nome':<{colunas['nome']}} "
            f"{'Preço':<{colunas['preco']}} "
            f"{'Categoria':<{colunas['categoria']}} "
            f"{'Estoque':<{colunas['estoque']}}"
        )
        
        # Cria a linha separadora
        separador = "-" * (sum(colunas.values()) + 4)  # +4 para os espaços entre colunas
        
        # Imprime o cabeçalho
        print(separador)
        print(cabecalho)
        print(separador)
        
        # Imprime os produtos
        for produto in produtos:
            # Trunca o nome se for muito longo
            nome = produto.nome
            if len(nome) > colunas['nome']:
                nome = nome[:colunas['nome']-3] + "..."
            
            # Formata a linha do produto
            linha = (
                f"{produto.id:<{colunas['id']}} "
                f"{nome:<{colunas['nome']}} "
                f"R${produto.preco:<{colunas['preco']-2}.2f} "
                f"{produto.categoria:<{colunas['categoria']}} "
                f"{produto.estoque:<{colunas['estoque']}}"
            )
            print(linha)
        
        print(separador)
        input("Pressione Enter para continuar...")
    
    def editar_produto(self):
        self.limpar_tela()
        self.imprimir_titulo("EDITAR PRODUTO")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar ou digite 'l' ou 'listar' para visualizar os produtos.")
        
        try:
            produto_id_input = input("Digite o ID do produto a ser editado: ")
            
            if produto_id_input.lower() in ["l", "listar"]:
                self.consultar_produtos()
                self.editar_produto()
                return

            if produto_id_input.lower() in ["c", "cancelar"]:
                print("Operação cancelada.")
                input("Pressione Enter para continuar...")
                return
            
            produto_id = int(produto_id_input)
            
            if produto_id not in self.sistema.produtos:
                print("Produto não encontrado.")
                input("Pressione Enter para continuar...")
                return
            
            produto = self.sistema.produtos[produto_id]
            
            print(f"Editando produto: {produto.nome}")
            print(f"Deixe em branco para manter o valor atual.")
            
            nome = input(f"Novo nome [{produto.nome}]: ")
            if nome == "":
                nome = produto.nome
            
            preco_str = input(f"Novo preço [R${produto.preco:.2f}]: ")
            preco = float(preco_str) if preco_str else None
            
            categoria = input(f"Nova categoria [{produto.categoria}]: ")
            if categoria == "":
                categoria = produto.categoria
            
            estoque_str = input(f"Novo estoque [{produto.estoque}]: ")
            estoque = int(estoque_str) if estoque_str else None
            
            resultado = self.sistema.editar_produto(produto_id, nome, preco, categoria, estoque)   
            
            if resultado:
                print("Produto editado com sucesso.")
            else:
                print("Erro ao editar produto.")
            
            input("Pressione Enter para continuar...")

        except ValueError:
            print("Valor inválido.")
            input("Pressione Enter para continuar...")

    def exportar_todos_relatorios(self):
        self.limpar_tela()
        self.imprimir_titulo("EXPORTAR TODOS RELATÓRIOS")

        try:
            # Verificar se o pandas está disponível
            data_atual = datetime.now().strftime("%d-%m-%y")
            nome_arquivo = f"relatorios_bar_{data_atual}.xlsx"

            # Cria um objeto ExcelWriter para salvar múltiplas planilhas
            with pd.ExcelWriter(nome_arquivo) as writer:
                # 1. Relatório de Estoque Baixo
                limite = 10
                produtos_baixo_estoque = []
                for produto in self.sistema.produtos.values():
                    if produto.estoque < limite:
                        produto_dict = {
                            "ID": produto.id,
                            "Nome": produto.nome,
                            "Categoria": produto.categoria,
                            "Preço": f"R$ {produto.preco:.2f}",
                            "Estoque": produto.estoque
                        }
                        produtos_baixo_estoque.append(produto_dict)

                if produtos_baixo_estoque:
                    df_estoque_baixo = pd.DataFrame(produtos_baixo_estoque)
                    df_estoque_baixo.to_excel(writer, sheet_name='Estoque Baixo', index=False)
                else:
                    df_estoque = pd.DataFrame({"Mensagem": [f"Não há produtos com estoque abaixo de {limite} unidades."]})
                    df_estoque.to_excel(writer, sheet_name='Estoque Baixo', index=False)

                # 2. Relatório de comandas do dia
                hoje = datetime.now().strftime("%d/%m/%y")
                comandas_dia = []
                for comanda in self.sistema.comandas.values():
                    if hoje[:5] in comanda.hora_abertura:
                        comanda_dict = {
                            "ID": comanda.id,
                            "Mesa": comanda.mesa,
                            "Status": comanda.status,
                            "Hora Abertura": comanda.hora_abertura,
                            "Hora Fechamento": comanda.hora_fechamento,
                            "Total": f"R$ {comanda.calcular_total():.2f}"
                        }
                        comandas_dia.append(comanda_dict)

                if comandas_dia:
                    df_comandas = pd.DataFrame(comandas_dia)
                    df_comandas.to_excel(writer, sheet_name='Comandas do Dia', index=False)

                    # 2.1 Itens das comandas do dia
                    itens_comandas = []
                    for comanda in self.sistema.comandas.values():
                        if hoje[:5] in comanda.hora_abertura:
                            for item in comanda.itens:
                                item_dict = {
                                    "Comanda ID": comanda.id,
                                    "Mesa": comanda.mesa,
                                    "Produto": item.nome_produto,
                                    "Quantidade": item.quantidade,
                                    "Preço Unitário": f"R$ {item.preco_unitario:.2f}",
                                    "Subtotal": f"R$ {item.subtotal:.2f}"
                                }
                                itens_comandas.append(item_dict)

                    if itens_comandas:
                        df_itens = pd.DataFrame(itens_comandas)
                        df_itens.to_excel(writer, sheet_name='Itens das Comandas', index=False)
                else:
                    df_comandas = pd.DataFrame({"Mensagem": [f"Não há comandas registradas hoje ({hoje})."]})
                    df_comandas.to_excel(writer, sheet_name='Comandas do Dia', index=False)

                # 3. Relatório de vendas do dia
                comandas_fechadas = []
                for comanda in self.sistema.comandas.values():
                    if comanda.status == "fechada" and comanda.hora_fechamento and hoje[:5] in comanda.hora_fechamento:
                        comanda_dict = {
                            "ID": comanda.id,
                            "Mesa": comanda.mesa,
                            "Hora Abertura": comanda.hora_abertura,
                            "Hora Fechamento": comanda.hora_fechamento,
                            "Total": f"R$ {comanda.calcular_total():.2f}"
                        }
                        comandas_fechadas.append(comanda_dict)

                if comandas_fechadas:
                    df_vendas = pd.DataFrame(comandas_fechadas)
                    df_vendas.to_excel(writer, sheet_name='Vendas do Dia', index=False)

                    # 3.1 Resumo de vendas
                    total_vendas = sum(comanda.calcular_total() for comanda in self.sistema.comandas.values()
                                     if comanda.status == "fechada" and comanda.hora_fechamento and hoje[:5] in comanda.hora_fechamento)
                    quantidade_comandas = len(comandas_fechadas)
                    ticket_medio = total_vendas / quantidade_comandas if quantidade_comandas > 0 else 0

                    df_resumo = pd.DataFrame({
                        "Métrica": ["Total de Vendas", "Quantidade de Comandas", "Ticket Médio"],
                        "Valor": [f"R$ {total_vendas:.2f}", quantidade_comandas, f"R$ {ticket_medio:.2f}"]
                    })
                    df_resumo.to_excel(writer, sheet_name='Resumo de Vendas', index=False)

                    # 3.2 Produtos mais vendidos
                    produtos_vendidos = {}
                    for comanda in self.sistema.comandas.values():
                        if comanda.status == "fechada" and comanda.hora_fechamento and hoje[:5] in comanda.hora_fechamento:
                            for item in comanda.itens:
                                if item.produto_id not in produtos_vendidos:
                                    produtos_vendidos[item.produto_id] = {
                                        "nome": item.nome_produto,
                                        "quantidade": 0,
                                        "total": 0
                                    }
                                produtos_vendidos[item.produto_id]["quantidade"] += item.quantidade
                                produtos_vendidos[item.produto_id]["total"] += item.subtotal

                    if produtos_vendidos:
                        produtos_lista = []
                        for pid, p in produtos_vendidos.items():
                            produtos_lista.append({
                                "ID": pid,
                                "Produto": p["nome"],
                                "Quantidade": p["quantidade"],
                                "Total": f"R$ {p['total']:.2f}"
                            })

                        df_produtos = pd.DataFrame(produtos_lista)
                        df_produtos = df_produtos.sort_values(by="Quantidade", ascending=False)
                        df_produtos.to_excel(writer, sheet_name='Produtos Vendidos', index=False)
                else:
                    df_vendas = pd.DataFrame({"Mensagem": [f"Não há comandas fechadas registradas hoje ({hoje})."]})
                    df_vendas.to_excel(writer, sheet_name='Vendas do Dia', index=False)
                    df_resumo = pd.DataFrame({"Mensagem": ["Sem dados de venda para hoje."]})
                    df_resumo.to_excel(writer, sheet_name='Resumo de Vendas', index=False)

            print(f"Relatórios exportados com sucesso para o arquivo: {nome_arquivo}")
            print(f"Local do arquivo: {os.path.abspath(nome_arquivo)}")

        except ImportError:
            print("Erro: A biblioteca pandas não está instalada.")
            print("Por favor, instale-a usando o comando: pip install pandas")
        except Exception as e:
            print(f"Erro ao exportar relatórios: {e}")

        input("Pressione Enter para continuar...")

if __name__ == "__main__":
    # Inicializar e executa a inteface do terminal

    interface = InterfaceTerminal()
    interface.executar()