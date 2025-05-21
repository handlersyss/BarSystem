import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os

class BarSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Bar")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")

        # Configuração do estilo
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#2196F3")
        self.style.configure("TLabel", padding=6, background="#f0f0f0")
        self.style.configure("TFrame", background="#f0f0f0")

        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        self.title_label = ttk.Label(
            self.main_frame,
            text="Sistema de Gerenciamento de Bar",
            font=("Helvetica", 24, "bold")
        )
        self.title_label.pack(pady=20)

        # Frame para os botões principais
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(pady=20)

        # Botões principais
        self.create_main_buttons()

    def create_main_buttons(self):
        # Botão de Vendas
        self.vendas_btn = ttk.Button(
            self.buttons_frame,
            text="Vendas",
            command=self.abrir_vendas,
            width=20
        )
        self.vendas_btn.grid(row=0, column=0, padx=10, pady=10)

        # Botão de Estoque
        self.estoque_btn = ttk.Button(
            self.buttons_frame,
            text="Estoque",
            command=self.abrir_estoque,
            width=20
        )
        self.estoque_btn.grid(row=0, column=1, padx=10, pady=10)

        # Botão de Relatórios
        self.relatorios_btn = ttk.Button(
            self.buttons_frame,
            text="Relatórios",
            command=self.abrir_relatorios,
            width=20
        )
        self.relatorios_btn.grid(row=0, column=2, padx=10, pady=10)

        # Botão de Configurações
        self.config_btn = ttk.Button(
            self.buttons_frame,
            text="Configurações",
            command=self.abrir_configuracoes,
            width=20
        )
        self.config_btn.grid(row=0, column=3, padx=10, pady=10)

    def abrir_vendas(self):
        messagebox.showinfo("Vendas", "Módulo de Vendas em desenvolvimento")

    def abrir_estoque(self):
        messagebox.showinfo("Estoque", "Módulo de Estoque em desenvolvimento")

    def abrir_relatorios(self):
        messagebox.showinfo("Relatórios", "Módulo de Relatórios em desenvolvimento")

    def abrir_configuracoes(self):
        messagebox.showinfo("Configurações", "Módulo de Configurações em desenvolvimento")

def main():
    root = tk.Tk()
    app = BarSystemGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 