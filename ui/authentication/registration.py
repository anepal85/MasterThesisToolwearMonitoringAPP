from database.db_session import DBSession
from database.operations.user.user_operation import UserOperation
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt5.QtCore import pyqtSignal
from schemas.user import UserModel

class RegisterWindow(QWidget):
    # Define a custom signal
    register_successful = pyqtSignal(bool)

    def __init__(self, user_operation: UserOperation, parent=None):
        super(RegisterWindow, self).__init__(parent)
        self.setWindowTitle("Register")
        self.user_operation = user_operation  # Create an instance of UserOperation
        layout = QVBoxLayout()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register)

        # Register the custom signal to emit after successful registration
        self.register_successful.connect(parent.show_login_window)

        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_edit)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_edit)
        layout.addWidget(register_button)
        self.setLayout(layout)

    def register(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required.")
            return
        # Check if the user already exists
        existing_user = self.user_operation.get_user_by_name(username)
        if existing_user:
            QMessageBox.warning(self, "Error", "Username already exists. Please choose a different one.")
            return
        
        try:
            # Convert user input to UserModel object
            user_data = UserModel(id=None, name=username, password=password, label_studio_api_key=None)  # Pass None for id
            # Create new user
            self.user_operation.create_user(user_data)
            QMessageBox.information(self, "Success", "User registered successfully.")
            self.register_successful.emit(True)
        except Exception as e:
            QMessageBox.warning(self, "Error", "An error occurred: {}".format(str(e)))       
