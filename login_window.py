import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QFrame
)
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt
from register_window import RegisterWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Bar System - Login')
        self.setFixedSize(800, 600)
        self.init_ui()

    def init_ui(self):
        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Lado esquerdo (bem-vindo)
        left_frame = QFrame()
        left_frame.setStyleSheet('background-color: #5A6DDF;')
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignCenter)

        welcome_label = QLabel('BEM\nVINDO!')
        welcome_label.setFont(QFont('Arial', 36, QFont.Bold))
        welcome_label.setStyleSheet('color: white;')
        welcome_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(welcome_label)

        left_layout.addStretch(1)

        create_label = QLabel('Crie um\nNovo Usuário!')
        create_label.setFont(QFont('Arial', 14))
        create_label.setStyleSheet('color: white;')
        create_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(create_label)

        register_btn = QPushButton('CADASTRAR')
        register_btn.setFont(QFont('Arial', 14, QFont.Bold))
        register_btn.setStyleSheet('background-color: #3B4371; color: white; padding: 10px 0; border-radius: 12px;')
        register_btn.clicked.connect(self.abrir_cadastro)
        left_layout.addWidget(register_btn)

        left_layout.addStretch(2)

        # Lado direito (login)
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignCenter)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(120, 120)
        logo_pixmap.fill(QColor('#B3B7F7'))  # Placeholder para logo
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(logo_label)

        bar_label = QLabel('<span style="font-size:32px; color:#5A6DDF; font-family:monospace;">Bar</span> <span style="font-size:24px; color:#5A6DDF; font-family:monospace;">System</span>')
        bar_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(bar_label)

        right_layout.addSpacing(30)

        # Campos de usuário e senha
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText('Usuário')
        self.user_input.setFont(QFont('Arial', 12))
        self.user_input.setStyleSheet('background-color: #393939; color: white; padding: 10px; border-radius: 5px;')
        right_layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText('Senha')
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFont(QFont('Arial', 12))
        self.pass_input.setStyleSheet('background-color: #393939; color: white; padding: 10px; border-radius: 5px;')
        right_layout.addWidget(self.pass_input)

        # Botão entrar
        login_btn = QPushButton('Entrar')
        login_btn.setFont(QFont('Arial', 14, QFont.Bold))
        login_btn.setStyleSheet('background-color: #2471A3; color: white; padding: 10px 0;')
        right_layout.addWidget(login_btn)

        right_layout.addStretch(2)

        # Adiciona os frames ao layout principal
        main_layout.addWidget(left_frame, 2)
        main_layout.addWidget(right_frame, 3)

    def abrir_cadastro(self):
        self.cadastro_window = RegisterWindow()
        self.cadastro_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_()) 