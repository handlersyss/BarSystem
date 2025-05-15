import os
import json
import sqlite3
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
        self.nome_cliente: Optional[str] = None
    
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
            "itens": [item.to_dict() for item in self.itens],
            "nome_cliente": self.nome_cliente
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
        comanda.nome_cliente = data.get("nome_cliente")
        for item_data in data.get("itens", []):
            item = ItemComanda.from_dict(item_data)
            comanda.itens.append(item)
        return comanda


class VendaRapida:
    def __init__(self):
        self.itens: List[ItemComanda] = []
        self.hora_venda = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def adicionar_item(self, item: ItemComanda):
        # Verifica se o item já existe na venda
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


class SistemaBar:
    def __init__(self):
        self.db_path = 'bar_system.db'
        self.produtos: Dict[int, Produto] = {}
        self.comandas: Dict[int, Comanda] = {}
        self.mesas: Dict[int, Optional[int]] = {}  # mesa_id -> comanda_id (None se mesa livre)
        self.proximo_id_produto = 1
        self.proximo_id_comanda = 1
        self.carregar_dados()
        
        # Inicializa o sistema com algumas mesas
        for i in range(1, 11):
            self.mesas[i] = None

    def _get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def carregar_dados(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Carregar produtos
                cursor.execute('SELECT id, nome, preco, categoria, estoque FROM produtos')
                for row in cursor.fetchall():
                    produto = Produto(id=row[0], nome=row[1], preco=row[2], categoria=row[3], estoque=row[4])
                    self.produtos[produto.id] = produto
                
                # Carregar comandas
                cursor.execute('SELECT id, mesa, status, hora_abertura, hora_fechamento, nome_cliente FROM comandas')
                for row in cursor.fetchall():
                    comanda = Comanda(id=row[0], mesa=row[1], status=row[2], hora_abertura=row[3])
                    comanda.hora_fechamento = row[4]
                    comanda.nome_cliente = row[5]
                    self.comandas[comanda.id] = comanda
                
                # Carregar itens das comandas
                cursor.execute('SELECT comanda_id, produto_id, quantidade, nome_produto, preco_unitario, subtotal FROM itens_comanda')
                for row in cursor.fetchall():
                    item = ItemComanda(produto_id=row[1], quantidade=row[2], nome_produto=row[3], preco_unitario=row[4])
                    if row[0] in self.comandas:
                        self.comandas[row[0]].itens.append(item)
                
                # Carregar mesas
                cursor.execute('SELECT id, comanda_id FROM mesas')
                for row in cursor.fetchall():
                    self.mesas[row[0]] = row[1]
                
                # Carregar contadores
                cursor.execute('SELECT nome, valor FROM contadores')
                for row in cursor.fetchall():
                    if row[0] == 'proximo_id_produto':
                        self.proximo_id_produto = row[1]
                    elif row[0] == 'proximo_id_comanda':
                        self.proximo_id_comanda = row[1]
                
                # Inicializar mesas se não existirem
                if not self.mesas:
                    for i in range(1, 11):
                        self.mesas[i] = None
                        cursor.execute('INSERT OR IGNORE INTO mesas (id, comanda_id) VALUES (?, ?)', (i, None))
                    conn.commit()
        
        except sqlite3.Error as e:
            print(f"Erro ao carregar dados: {e}")
            print("Iniciando com dados vazios.")

    def salvar_dados(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Salvar contadores
                cursor.execute('''
                    INSERT OR REPLACE INTO contadores (nome, valor)
                    VALUES (?, ?)
                ''', ('proximo_id_produto', self.proximo_id_produto))
                cursor.execute('''
                    INSERT OR REPLACE INTO contadores (nome, valor)
                    VALUES (?, ?)
                ''', ('proximo_id_comanda', self.proximo_id_comanda))
                
                conn.commit()
        
        except sqlite3.Error as e:
            print(f"Erro ao salvar dados: {e}")
    
    def adicionar_produto(self, nome: str, preco: float, categoria: str, estoque: int) -> Produto:
        id_disponivel = self.proximo_id_produto
        while id_disponivel in self.produtos:
            id_disponivel += 1
        
        produto = Produto(
            id=id_disponivel,
            nome=nome,
            preco=preco,
            categoria=categoria,
            estoque=estoque
        )
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO produtos (id, nome, preco, categoria, estoque)
                    VALUES (?, ?, ?, ?, ?)
                ''', (produto.id, produto.nome, produto.preco, produto.categoria, produto.estoque))
                conn.commit()
                
                self.produtos[produto.id] = produto
                self.proximo_id_produto = max(self.proximo_id_produto, id_disponivel + 1)
                self.salvar_dados()
                return produto
        
        except sqlite3.Error as e:
            print(f"Erro ao adicionar produto: {e}")
            return None
    
    def editar_produto(self, id: int, nome: str = None, preco: float = None, 
                     categoria: str = None, estoque: int = None) -> bool:
        """Edita um produto existente."""
        if id not in self.produtos:
            return False
        
        produto = self.produtos[id]
        updates = {}
        
        if nome is not None:
            produto.nome = nome
            updates['nome'] = nome
        
        if preco is not None:
            produto.preco = preco
            updates['preco'] = preco
        
        if categoria is not None:
            produto.categoria = categoria
            updates['categoria'] = categoria
        
        if estoque is not None:
            produto.estoque = estoque
            updates['estoque'] = estoque
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = 'UPDATE produtos SET ' + ', '.join(f'{k} = ?' for k in updates) + ' WHERE id = ?'
                cursor.execute(query, list(updates.values()) + [id])
                conn.commit()
                return True
        
        except sqlite3.Error as e:
            print(f"Erro ao editar produto: {e}")
            return False
    
    def remover_produto(self, id: int) -> bool:
        """Remove um produto do sistema."""
        if id not in self.produtos:
            return False
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM produtos WHERE id = ?', (id,))
                conn.commit()
                del self.produtos[id]
                return True
        
        except sqlite3.Error as e:
            print(f"Erro ao remover produto: {e}")
            return False
    
    def abrir_comanda(self, mesa: int, nome_cliente: str) -> Optional[Comanda]:
        """Abre uma nova comanda para uma mesa."""
        if mesa not in self.mesas or self.mesas[mesa] is not None:
            return None
        
        comanda = Comanda(id=self.proximo_id_comanda, mesa=mesa)
        comanda.nome_cliente = nome_cliente

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO comandas (id, mesa, status, hora_abertura, nome_cliente)
                    VALUES (?, ?, ?, ?, ?)
                ''', (comanda.id, comanda.mesa, comanda.status, comanda.hora_abertura, comanda.nome_cliente))
                cursor.execute('UPDATE mesas SET comanda_id = ? WHERE id = ?', (comanda.id, mesa))
                conn.commit()
                
                self.comandas[comanda.id] = comanda
                self.mesas[mesa] = comanda.id
                self.proximo_id_comanda += 1
                self.salvar_dados()
                return comanda
        
        except sqlite3.Error as e:
            print(f"Erro ao abrir comanda: {e}")
            return None
    
    def adicionar_item_comanda(self, comanda_id: int, produto_id: int, quantidade: int) -> bool:
        if comanda_id not in self.comandas or produto_id not in self.produtos:
            return False
        
        comanda = self.comandas[comanda_id]
        produto = self.produtos[produto_id]
        
        if comanda.status != "aberta" or produto.estoque < quantidade:
            return False
        
        item = ItemComanda(
            produto_id=produto_id,
            quantidade=quantidade,
            nome_produto=produto.nome,
            preco_unitario=produto.preco
        )
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO itens_comanda (comanda_id, produto_id, quantidade, nome_produto, preco_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (comanda_id, item.produto_id, item.quantidade, item.nome_produto, item.preco_unitario, item.subtotal))
                cursor.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', (quantidade, produto_id))
                conn.commit()
                
                produto.estoque -= quantidade
                comanda.adicionar_item(item)
                return True
        
        except sqlite3.Error as e:
            print(f"Erro ao adicionar item à comanda: {e}")
            return False
    
    def remover_item_comanda(self, comanda_id: int, produto_id: int, quantidade: int) -> bool:
        if comanda_id not in self.comandas or produto_id not in self.produtos:
            return False
        
        comanda = self.comandas[comanda_id]
        if comanda.status != "aberta":
            return False
        
        for item in comanda.itens:
            if item.produto_id == produto_id:
                try:
                    with self._get_connection() as conn:
                        cursor = conn.cursor()
                        if item.quantidade <= quantidade:
                            cursor.execute('DELETE FROM itens_comanda WHERE comanda_id = ? AND produto_id = ?', (comanda_id, produto_id))
                        else:
                            cursor.execute('''
                                UPDATE itens_comanda
                                SET quantidade = quantidade - ?, subtotal = (quantidade - ?) * preco_unitario
                                WHERE comanda_id = ? AND produto_id = ?
                            ''', (quantidade, quantidade, comanda_id, produto_id))
                        cursor.execute('UPDATE produtos SET estoque = estoque + ? WHERE id = ?', (min(quantidade, item.quantidade), produto_id))
                        conn.commit()
                        
                        self.produtos[produto_id].estoque += min(quantidade, item.quantidade)
                        return comanda.remover_item(produto_id, quantidade)
                
                except sqlite3.Error as e:
                    print(f"Erro ao remover item da comanda: {e}")
                    return False
        return False
    
    def fechar_comanda(self, comanda_id: int) -> Optional[float]:
        if comanda_id not in self.comandas or self.comandas[comanda_id].status != "aberta":
            return None
        
        comanda = self.comandas[comanda_id]
        comanda.fechar_comanda()
        total = comanda.calcular_total()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE comandas
                    SET status = ?, hora_fechamento = ?
                    WHERE id = ?
                ''', (comanda.status, comanda.hora_fechamento, comanda_id))
                cursor.execute('UPDATE mesas SET comanda_id = NULL WHERE comanda_id = ?', (comanda_id,))
                conn.commit()
                
                self.mesas[comanda.mesa] = None
                return total
        
        except sqlite3.Error as e:
            print(f"Erro ao fechar comanda: {e}")
            return None
    
    def consultar_produtos(self, categoria: str = None) -> List[Produto]:
        if categoria:
            return [p for p in self.produtos.values() if p.categoria == categoria]
        return list(self.produtos.values())
    
    def listar_comandas_abertas(self) -> List[Comanda]:
        return [c for c in self.comandas.values() if c.status == "aberta"]
    
    def listar_mesas_livres(self) -> List[int]:
        return [mesa for mesa, comanda_id in self.mesas.items() if comanda_id is None]
    
    def listar_mesas_ocupadas(self) -> List[int]:
        return [mesa for mesa, comanda_id in self.mesas.items() if comanda_id is not None]
    
    def obter_comanda_por_mesa(self, mesa: int) -> Optional[Comanda]:
        if mesa not in self.mesas or self.mesas[mesa] is None:
            return None
        comanda_id = self.mesas[mesa]
        return self.comandas.get(comanda_id)
    
    def adicionar_mesa(self, numero_mesa: int) -> bool:
        if numero_mesa in self.mesas:
            return False
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO mesas (id, comanda_id) VALUES (?, ?)', (numero_mesa, None))
                conn.commit()
                
                self.mesas[numero_mesa] = None
                return True
        
        except sqlite3.Error as e:
            print(f"Erro ao adicionar mesa: {e}")
            return False
    
    def remover_mesa(self, numero_mesa: int) -> bool:
        if numero_mesa not in self.mesas:
            return False
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM mesas WHERE id = ?', (numero_mesa,))
                conn.commit()
                
                del self.mesas[numero_mesa]
                return True
        
        except sqlite3.Error as e:
            print(f"Erro ao remover mesa: {e}")
            return False

    def registrar_venda_rapida(self, venda: VendaRapida) -> bool:
        """Registra uma venda rápida no sistema."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Cria uma comanda temporária para registrar a venda
                comanda_id = self.proximo_id_comanda
                cursor.execute('''
                    INSERT INTO comandas (id, mesa, status, hora_abertura, hora_fechamento)
                    VALUES (?, ?, ?, ?, ?)
                ''', (comanda_id, 0, "fechada", venda.hora_venda, venda.hora_venda))
                
                # Registra os itens da venda
                for item in venda.itens:
                    cursor.execute('''
                        INSERT INTO itens_comanda (comanda_id, produto_id, quantidade, nome_produto, preco_unitario, subtotal)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (comanda_id, item.produto_id, item.quantidade, item.nome_produto, item.preco_unitario, item.subtotal))
                    
                    # Atualiza o estoque no banco de dados
                    cursor.execute('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', 
                                 (item.quantidade, item.produto_id))
                    
                    # Atualiza o estoque na memória
                    if item.produto_id in self.produtos:
                        self.produtos[item.produto_id].estoque -= item.quantidade
                
                conn.commit()
                self.proximo_id_comanda += 1
                self.salvar_dados()
                return True
                
        except sqlite3.Error as e:
            print(f"Erro ao registrar venda rápida: {e}")
            return False

    def atualizar_nome_cliente(self, comanda_id: int, nome_cliente: str) -> bool:
        """Atualiza o nome do cliente em uma comanda."""
        if comanda_id not in self.comandas:
            return False
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE comandas
                    SET nome_cliente = ?
                    WHERE id = ?
                ''', (nome_cliente, comanda_id))
                conn.commit()
                
                self.comandas[comanda_id].nome_cliente = nome_cliente
                return True
        
        except sqlite3.Error as e:
            print(f"Erro ao atualizar nome do cliente: {e}")
            return False

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
        print(f"{'ID':<5} {'Mesa':<5} {'Cliente':<20} {'Status':<10} {'Hora Abertura':<20} {'Hora Fechamento':<20} {'Total':<10}")
        print(self.linha_separadora())

        for comanda in Comandas_dia:
            total = comanda.calcular_total()
            status = comanda.status
            hora_fechamento = comanda.hora_fechamento or "_"
            nome_cliente = comanda.nome_cliente or "N/A"

            print(f"{comanda.id:<5} {comanda.mesa:<5} {nome_cliente:<20} {status:<10} {comanda.hora_abertura:<20} {hora_fechamento:<20} R${total:<8.2f}")

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
        self.venda_atual = None

    def limpar_tela(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def menu_principal(self):
        self.limpar_tela()
        self.imprimir_titulo("SISTEMA DE BAR")
        print("1. Gestão de Mesas")
        print("2. Gestão de Produtos e Estoque")
        print("3. Relatórios")
        print("4. Venda Rápida")
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
            self.venda_rapida()
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

        nome_cliente = input("Digite o nome do cliente: ")
        if nome_cliente.lower() in ['c', 'cancelar']:
            print("Operação cancelada.")
            input("Pressione Enter para continuar...")
            return
        
        if not nome_cliente:
            print("Nome do cliente não pode ser vazio.")
            input("Pressione Enter para continuar...")
            return
        
        comanda = self.sistema.abrir_comanda(mesa, nome_cliente)
        
        if comanda:
            print(f"Comanda {comanda.id} aberta para a mesa {mesa}.")
            print(f"Nome do cliente: {comanda.nome_cliente}")
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
        print(self.linha_separadora())
        print(f"Comanda #{comanda.id} - Mesa {comanda.mesa}")
        print(f"Aberta em: {comanda.hora_abertura}")
        print(f"Nome do cliente: {comanda.nome_cliente}")
        print(self.linha_separadora())
        
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
        print(f"Nome do cliente: {comanda.nome_cliente}")
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

    def venda_rapida(self):
        self.limpar_tela()
        self.imprimir_titulo("VENDA RÁPIDA")
        print("Digite 'c' ou 'cancelar' a qualquer momento para voltar.")
        
        if not self.venda_atual:
            self.venda_atual = VendaRapida()
        
        while True:
            self.limpar_tela()
            print(self.linha_separadora())
            print("VENDA ATUAL:")
            print(self.linha_simples())
            
            if not self.venda_atual.itens:
                print("Nenhum item adicionado.")
            else:
                print(f"{'Qtd':<5} {'Produto':<30} {'Preço Unit.':<15} {'Subtotal':<15}")
                print(self.linha_simples())
                
                for item in self.venda_atual.itens:
                    print(f"{item.quantidade:<5} {item.nome_produto:<30} R${item.preco_unitario:<13.2f} R${item.subtotal:<13.2f}")
                
                print(self.linha_simples())
                print(f"{'TOTAL:':<36} R${self.venda_atual.calcular_total():<13.2f}")
            
            print(self.linha_separadora())
            print("\n1. Adicionar Produto")
            print("2. Remover Produto")
            print("3. Finalizar Venda")
            print("0. Cancelar Venda")
            
            opcao = input("\nEscolha uma opção: ")
            
            if opcao == "1":
                self.adicionar_item_venda_rapida()
            elif opcao == "2":
                self.remover_item_venda_rapida()
            elif opcao == "3":
                self.finalizar_venda_rapida()
                break
            elif opcao == "0":
                self.venda_atual = None
                break
            else:
                input("Opção inválida. Pressione Enter para continuar...")

    def adicionar_item_venda_rapida(self):
        self.limpar_tela()
        print(self.linha_separadora())
        print("ADICIONAR PRODUTO")
        print(self.linha_separadora())
        
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
        
        try:
            produto_id = int(input("\nDigite o ID do produto: "))
            
            if produto_id not in self.sistema.produtos:
                print("Produto não encontrado.")
                input("Pressione Enter para continuar...")
                return
            
            quantidade = int(input("Digite a quantidade: "))
            
            if quantidade <= 0:
                print("Quantidade deve ser maior que zero.")
                input("Pressione Enter para continuar...")
                return
            
            if self.sistema.produtos[produto_id].estoque < quantidade:
                print("Estoque insuficiente.")
                input("Pressione Enter para continuar...")
                return
            
            produto = self.sistema.produtos[produto_id]
            item = ItemComanda(
                produto_id=produto_id,
                quantidade=quantidade,
                nome_produto=produto.nome,
                preco_unitario=produto.preco
            )
            
            self.venda_atual.adicionar_item(item)
            print(f"{quantidade}x {produto.nome} adicionado(s) à venda.")
            
        except ValueError:
            print("Valor inválido.")
        
        input("Pressione Enter para continuar...")

    def remover_item_venda_rapida(self):
        if not self.venda_atual.itens:
            input("Não há itens para remover. Pressione Enter para continuar...")
            return
        
        self.limpar_tela()
        print(self.linha_separadora())
        print("REMOVER PRODUTO")
        print(self.linha_separadora())
        
        print("\nItens na venda:")
        print("-" * 50)
        print(f"{'ID':<5} {'Qtd':<5} {'Produto':<30} {'Preço Unit.':<15} {'Subtotal':<15}")
        print("-" * 50)
        
        for i, item in enumerate(self.venda_atual.itens, 1):
            print(f"{i:<5} {item.quantidade:<5} {item.nome_produto:<30} R${item.preco_unitario:<13.2f} R${item.subtotal:<13.2f}")
        
        print("-" * 50)
        
        try:
            item_id = int(input("\nDigite o número do item a remover: "))
            
            if item_id < 1 or item_id > len(self.venda_atual.itens):
                print("Item não encontrado.")
                input("Pressione Enter para continuar...")
                return
            
            item = self.venda_atual.itens[item_id - 1]
            quantidade = int(input(f"Digite a quantidade a remover (máx: {item.quantidade}): "))
            
            if quantidade <= 0 or quantidade > item.quantidade:
                print("Quantidade inválida.")
                input("Pressione Enter para continuar...")
                return
            
            self.venda_atual.remover_item(item.produto_id, quantidade)
            print(f"{quantidade}x {item.nome_produto} removido(s) da venda.")
            
        except ValueError:
            print("Valor inválido.")
        
        input("Pressione Enter para continuar...")

    def finalizar_venda_rapida(self):
        if not self.venda_atual.itens:
            print("Não há itens na venda.")
            input("Pressione Enter para continuar...")
            return
        
        self.limpar_tela()
        print(self.linha_separadora())
        print("FINALIZAR VENDA")
        print(self.linha_separadora())
        
        print("\nResumo da venda:")
        print("-" * 50)
        print(f"{'Qtd':<5} {'Produto':<30} {'Preço Unit.':<15} {'Subtotal':<15}")
        print("-" * 50)
        
        for item in self.venda_atual.itens:
            print(f"{item.quantidade:<5} {item.nome_produto:<30} R${item.preco_unitario:<13.2f} R${item.subtotal:<13.2f}")
        
        print("-" * 50)
        print(f"{'TOTAL:':<36} R${self.venda_atual.calcular_total():<13.2f}")
        print(self.linha_separadora())
        
        confirmar = input("Confirma a finalização da venda? (s/n): ")
        
        if confirmar.lower() == "s":
            if self.sistema.registrar_venda_rapida(self.venda_atual):
                print(f"Venda finalizada com sucesso! Total: R${self.venda_atual.calcular_total():.2f}")
            else:
                print("Erro ao finalizar venda.")
        else:
            print("Venda cancelada.")
        
        self.venda_atual = None
        input("Pressione Enter para continuar...")

if __name__ == "__main__":
    # Inicializar e executa a inteface do terminal

    interface = InterfaceTerminal()
    interface.executar()