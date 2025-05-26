from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Bar System - Cadastro')
        self.setFixedSize(800, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel('Cadastro')
        title_label.setFont(QFont('Arial', 32, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Nome do Usuário')
        self.username_input.setFont(QFont('Arial', 14))
        form_layout.addRow('Usuário:', self.username_input)

        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText('Nome da Empresa')
        self.company_input.setFont(QFont('Arial', 14))
        form_layout.addRow('Empresa:', self.company_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Senha')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont('Arial', 14))
        form_layout.addRow('Senha:', self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('Confirmar Senha')
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setFont(QFont('Arial', 14))
        form_layout.addRow('Confirmar:', self.confirm_password_input)

        main_layout.addLayout(form_layout)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        register_btn = QPushButton('Cadastrar')
        register_btn.setFont(QFont('Arial', 14, QFont.Bold))
        register_btn.setStyleSheet('background-color: #2471A3; color: white; padding: 10px 0; border-radius: 8px;')
        register_btn.clicked.connect(self.try_register)
        btn_layout.addWidget(register_btn)

        back_btn = QPushButton('Voltar')
        back_btn.setFont(QFont('Arial', 14, QFont.Bold))
        back_btn.setStyleSheet('background-color: #f44336; color: white; padding: 10px 0; border-radius: 8px;')
        back_btn.clicked.connect(self.close)
        btn_layout.addWidget(back_btn)

        main_layout.addLayout(btn_layout)

    def try_register(self):
        username = self.username_input.text()
        company = self.company_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not all([username, company, password, confirm_password]):
            self.show_message('Erro', 'Por favor, preencha todos os campos!', QMessageBox.Critical)
            return
        if password != confirm_password:
            self.show_message('Erro', 'As senhas não coincidem!', QMessageBox.Critical)
            return
        # TODO: Implementar cadastro no banco de dados
        self.show_message('Sucesso', 'Cadastro realizado com sucesso!', QMessageBox.Information)
        self.close()

    def show_message(self, title, message, icon):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        msg.exec_()

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec_()) 