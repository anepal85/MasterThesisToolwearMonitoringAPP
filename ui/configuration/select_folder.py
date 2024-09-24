import os
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QMessageBox

class FolderSelectorWidget(QWidget):
    def __init__(self, label_name, default_value=None):
        super().__init__()
        self.label_name = label_name
        self.default_value = default_value
        self.init_ui()

    def init_ui(self):
        self.label = QLabel(self.label_name)
        self.input_widget = QLineEdit()
        if self.default_value is not None:
            self.input_widget.setText(self.default_value)
            self.folder_path = self.default_value
            self.create_subfolders(self.default_value)
        
        self.select_folder_button = QPushButton("Auswählen")
        self.select_folder_button.clicked.connect(self.select_folder)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_widget)
        layout.addWidget(self.select_folder_button)
        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:
            self.folder_path = folder
            self.create_subfolders(folder)
            self.input_widget.setText(folder)

    def create_subfolders(self, folder):
        images_folder = os.path.join(folder, "images")
        masks_folder = os.path.join(folder, "masks")

        try:
            if not os.path.exists(images_folder):
                os.makedirs(images_folder)
            if not os.path.exists(masks_folder):
                os.makedirs(masks_folder)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create subfolders: {e}")

    def get_folder_path(self):
        return self.folder_path
    
    def get_input(self):
        sanitized_label = 'images_folder'
        return sanitized_label, self.input_widget.text(), None













# import os
# from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox

# class FolderSelectorWidget(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.init_ui()

#     def init_ui(self):
#         self.layout = QVBoxLayout(self)

#         self.info_label = QLabel("Bildspeicherordner: ", self)
#         self.layout.addWidget(self.info_label)

#         self.select_folder_button = QPushButton("Auswählen", self)
#         self.select_folder_button.clicked.connect(self.select_folder)
#         self.layout.addWidget(self.select_folder_button)

#         self.selected_folder_label = QLabel("", self)
#         self.layout.addWidget(self.selected_folder_label)

#         self.folder_path = None

#     def select_folder(self):
#         folder = QFileDialog.getExistingDirectory(self, "Select Folder")

#         if folder:
#             self.folder_path = folder
#             self.create_subfolders(folder)
#             self.selected_folder_label.setText(f"Selected Folder: {folder}")

#     def create_subfolders(self, folder):
#         images_folder = os.path.join(folder, "images")
#         masks_folder = os.path.join(folder, "masks")

#         try:
#             if not os.path.exists(images_folder):
#                 os.makedirs(images_folder)
#             if not os.path.exists(masks_folder):
#                 os.makedirs(masks_folder)
#         except Exception as e:
#             QMessageBox.critical(self, "Error", f"Failed to create subfolders: {e}")

#     def get_folder_path(self):
#         return self.folder_path
