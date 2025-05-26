import subprocess
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt
from register_window import RegisterWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Bar System - Login')
        self.setFixedSize(800, 600)

        # Imagem de fundo
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap('img/painel2_800x600.png'))
        self.bg_label.setScaledContents(True)
        self.bg_label.resize(800, 600)

        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Espaço da esquerda (painel azul)
        left_spacer = QFrame()
        left_spacer.setFixedWidth(270)  # largura do painel azul
        main_layout.addWidget(left_spacer)

        # Painel de login (parte branca)
        login_frame = QFrame()
        login_frame.setStyleSheet('background-color: rgba(255,255,255,0.92); border-radius: 20px;')
        login_frame.setFixedWidth(500)
        login_frame.setFixedHeight(520)
        login_layout = QVBoxLayout(login_frame)
        login_layout.setAlignment(Qt.AlignCenter)
        login_layout.setContentsMargins(20, 20, 20, 20)
        login_layout.setSpacing(20)

        top_spacer = QSpacerItem(-35, -35, QSizePolicy.Minimum, QSizePolicy.Fixed)
        login_layout.addItem(top_spacer)

        # Logo (imagem real)
        logo_label = QLabel()
        logo_pixmap = QPixmap('img/Logo_600x600.png')
        logo_pixmap = logo_pixmap.scaled(210, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(logo_label)
        
        bar_label = QLabel('<span style="font-size:40px; color:#5A6DDF; font-family:rota black;">SIGN IN</span>')
        bar_label.setAlignment(Qt.AlignCenter)
        bar_label.setContentsMargins(0, 10, 0, 0)
        login_layout.addWidget(bar_label)
        
        # Campos de usuário e senha
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText('Usuário:')
        self.user_input.setFont(QFont('rota black', 12))
        self.user_input.setStyleSheet('background-color: transparent; color: #404E96; padding: 10px; border: 2px solid #5968D8; border-radius: 5px;')
        login_layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText('Senha:')
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFont(QFont('rota black', 12))
        self.pass_input.setStyleSheet('background-color: transparent; color: #404E96; padding: 10px; border: 2px solid #5968D8; border-radius: 5px;')
        login_layout.addWidget(self.pass_input)

        # Botão entrar
        login_btn = QPushButton('Entrar')
        login_btn.setFont(QFont('Arial', 14, QFont.Bold))
        login_btn.setStyleSheet('background-color: #5968D8; color: white; padding: 10px 0; border-radius: 20px;')
        login_layout.addWidget(login_btn)

        main_layout.addWidget(login_frame)

        # Espaço à direita
        right_spacer = QFrame()
        main_layout.addWidget(right_spacer)

        login_btn.clicked.connect(self.executar_sistema_terminal)
        login_layout.addWidget(login_btn)


        # Botão cadastrar no canto inferior esquerdo
        self.register_btn = QPushButton('Cadastrar', self)
        self.register_btn.setFont(QFont('Arial', 14, QFont.Bold))
        self.register_btn.setStyleSheet('background-color: #404E96; color: white; padding: 10px 0; border-radius: 20px;')
        self.register_btn.setFixedWidth(180)
        self.register_btn.setFixedHeight(45)
        self.register_btn.move(20, 490)
        self.register_btn.clicked.connect(self.abrir_cadastro)
        self.register_btn.raise_()  # Garante que o botão fique acima do fundo

    def abrir_cadastro(self):
        self.cadastro_window = RegisterWindow()
        self.cadastro_window.show()

    def resizeEvent(self, event):
        self.bg_label.resize(self.size())
        self.register_btn.raise_()
        super().resizeEvent(event)

    def executar_sistema_terminal(self):
        try:
            subprocess.Popen(['python3', 'barsystem.py'])
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao executar sistema: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_()) 