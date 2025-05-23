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
        img_path = "img/painel_500x400.png"
        if os.path.exists(img_path):
            self.bg_img = Image.open(img_path)
            self.bg_img = self.bg_img.resize((800, 600), Image.LANCZOS)
            self.bg_img_tk = ImageTk.PhotoImage(self.bg_img)

            self.bg_label = tk.Label(self, image=self.bg_img_tk, borderwidth=0)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Frame principal transparente
        self.main_frame = ctk.CTkFrame(self, fg_color="white")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Caminho para a fonte
        font_path = os.path.join("img/pixel_operator/PixelOperator8.ttf")

        # Registrar a fonte no sistema (apenas para a sessão do Tkinter)
        if os.path.exists(font_path):
            import tkinter.font as tkfont
            tkfont.Font(family="PixelOperator8", size=32, weight="bold")  # registra a família
            self.tk.call("font", "create", "PixelOperator8", "-family", "PixelOperator8", "-size", 32, "-weight", "bold")
            pixel_font = CTkFont(family="Pixel Operator 8", size=32, weight="bold")
        else:
            pixel_font = CTkFont(size=32, weight="bold")  # fallback

        # Logo com título em imagem PNG
        logo_path = "img/Logo_600x600.png"  # ajuste o caminho conforme o seu arquivo
        if os.path.exists(logo_path):
            self.logo_img = Image.open(logo_path)
            self.logo_img = self.logo_img.resize((200, 200), Image.LANCZOS)  # ajuste o tamanho se quiser
            self.logo_img_tk = ImageTk.PhotoImage(self.logo_img)
            logo_label = ctk.CTkLabel(self.main_frame, image=self.logo_img_tk, text="", fg_color="transparent")
            logo_label.pack(pady=20)

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