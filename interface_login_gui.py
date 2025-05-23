import customtkinter as ctk
import os
from register_window import RegisterWindow

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.title("Bar System - Login")
        self.geometry("800x600")
        self.resizable(False, False)
        
        # Configurar tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="Bar System",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Frame para os campos de login
        login_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        login_frame.pack(pady=20)
        
        # Campos de login
        self.username_input = ctk.CTkEntry(
            login_frame,
            placeholder_text="Usuário",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.username_input.pack(pady=10)
        
        self.password_input = ctk.CTkEntry(
            login_frame,
            placeholder_text="Senha",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            show="•"
        )
        self.password_input.pack(pady=10)
        
        # Botões
        login_button = ctk.CTkButton(
            login_frame,
            text="Entrar",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.try_login
        )
        login_button.pack(pady=10)
        
        register_button = ctk.CTkButton(
            login_frame,
            text="Cadastrar",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2196F3",
            hover_color="#1976D2",
            command=self.show_register_window
        )
        register_button.pack(pady=10)
    
    def try_login(self):
        username = self.username_input.get()
        password = self.password_input.get()
        
        if not username or not password:
            self.show_error("Por favor, preencha todos os campos!")
            return
        
        # TODO: Implementar verificação de login
        self.show_success("Funcionalidade de login será implementada!")
    
    def show_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.grab_set()  # Torna a janela modal
    
    def show_error(self, message):
        dialog = ctk.CTkInputDialog(
            text=message,
            title="Erro",
            button_text="OK"
        )
        dialog.get_input()
    
    def show_success(self, message):
        dialog = ctk.CTkInputDialog(
            text=message,
            title="Sucesso",
            button_text="OK"
        )
        dialog.get_input()

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop() 