import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
from register_window import RegisterWindow
from customtkinter import CTkFont

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.title("Bar System - Login")
        self.geometry("800x600")
        self.resizable(False, False)
        
        # Carregar imagem de fundo
        img_path = "img/painel2_800x600.png"
        if os.path.exists(img_path):
            self.bg_img = Image.open(img_path)
            self.bg_img = self.bg_img.resize((800, 600), Image.LANCZOS)
            self.bg_img_tk = ImageTk.PhotoImage(self.bg_img)

            self.bg_label = tk.Label(self, image=self.bg_img_tk, borderwidth=0)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Frame principal transparente
        self.main_frame = ctk.CTkFrame(self, fg_color="white")
        self.main_frame.place(relx=0.65, rely=0.5, anchor="center")
        """
        # Frame para a logo "Bem-vindo"
        self.main_frame_after = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame_after.place(relx=0.03, rely=0.15, anchor="nw")
        """

        # Logo com título em imagem PNG
        logo_path = "img/Logo_600x600.png" 
        if os.path.exists(logo_path):
            self.logo_img = Image.open(logo_path)
            self.logo_img = self.logo_img.resize((200, 200), Image.LANCZOS)
            self.logo_img_tk = ImageTk.PhotoImage(self.logo_img)
            logo_label = ctk.CTkLabel(self.main_frame, image=self.logo_img_tk, text="", fg_color="transparent")
            logo_label.pack(pady=20)
        """
        # Logo com título em imagem PNG (BEM VINDO)
        logo_b_path = "img/Bem_vindo_112,52.png"
        if os.path.exists(logo_b_path):
            self.logo_b_img = Image.open(logo_b_path)
            self.logo_b_img = self.logo_b_img.resize((178, 82), Image.LANCZOS)
            self.logo_b_img_tk = ImageTk.PhotoImage(self.logo_b_img)
            logo_b_label = ctk.CTkLabel(self.main_frame_after, image=self.logo_b_img_tk, text="", fg_color="transparent", bg_color="transparent")
            logo_b_label.pack(pady=20)
        """
        # Frame para os campos de login
        login_frame = ctk.CTkFrame(self.main_frame, fg_color="white")
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

        # Adicione o botão de cadastro na lateral esquerda
        register_button_lateral = ctk.CTkButton(
            self,
            text="CADASTRAR",
            width=180,
            height=40,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#404E96",
            hover_color="#5968d8",
            command=self.show_register_window,
            corner_radius=20
        )
        register_button_lateral.place(x=20, y=485)
    
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
        self.register_window.grab_set()
    
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