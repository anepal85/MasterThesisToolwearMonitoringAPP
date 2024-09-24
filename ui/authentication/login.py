from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from database.db_session import DBSession
from database.operations.user.user_operation import UserOperation
from models.model import check_password_hash
from PyQt5.QtGui import QIcon

class LoginWindow(QWidget):
    def __init__(self, user_operation: UserOperation,  parent=None):
        super(LoginWindow, self).__init__(parent)
        self.setWindowTitle("Login")

        self.user_operation = user_operation
        # Apply style sheet to set background color
        #self.setStyleSheet("background-color: purple;")

        layout = QVBoxLayout()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        login_button = QPushButton("Login")
        login_button.setIcon(QIcon(":/icons/Icons/log-in.svg"))  
    
        login_button.clicked.connect(self.login)
        register_button = QPushButton("Register")
        register_button.clicked.connect(self.show_register_window)
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_edit)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_edit)
        layout.addWidget(login_button)
        layout.addWidget(register_button)
        
        self.setLayout(layout)

    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        user = self.user_operation.get_user_by_name(username)
        try:
            if user and check_password_hash(user.password_hash, password):
                # Successful login, open main application window
                self.parent().show_main_window(username)
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
        # except AttributeError:
        #     QMessageBox.warning(self, "User Not Found", "User with username '{}' not found.".format(username))
        except AttributeError as e:
            QMessageBox.warning(self, "Attribute Error", str(e))
    
    def show_register_window(self):
        self.parent().show_register_window()