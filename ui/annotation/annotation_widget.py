import subprocess
import os
import requests
from PyQt5.QtWidgets import QPushButton, QWidget, QFileDialog, QLineEdit, QComboBox, QLabel,  QGridLayout
from PyQt5.QtCore import pyqtSlot, QTimer
from schemas.user import UserModel
from ui.annotation.annotation_worker import WorkerThread
from ui.annotation.label_studio import create_and_upload_annotations, create_local_storage, create_segmentation_project, encode_image_url, get_existing_tasks, get_file_paths, get_local_storage_root_folder, get_local_storages, sync_local_storage, task_has_annotation
from database.operations.user.user_operation import UserOperation

LABEL_STUDIO_URL = 'http://localhost:8080'

class AnnotationWidget(QWidget):
    def __init__(self, user_operation:UserOperation, user_model:UserModel):
        super().__init__()
        self.user_operation = user_operation
        self.user_model = user_model
        self.project = None
        self.root_folder = None
        self.api_key = self.user_model.label_studio_api_key or None 
        self.initUI()

    def initUI(self):
        # Set the font size for the widget
        self.setStyleSheet("font-size: 18px;")
        layout = QGridLayout()

        self.api_key_input = QLineEdit(self)
        self.api_key_input.setPlaceholderText("Enter API key")
        if self.api_key:
            self.api_key_input.setText(self.api_key)
            self.api_key_input.setDisabled(True)

        self.save_api_key_button = QPushButton("Save API Key", self)
        self.save_api_key_button.clicked.connect(self.save_api_key)

        self.start_label_studio_button = QPushButton("Start Label Studio", self)
        self.start_label_studio_button.clicked.connect(self.select_root_folder)

        self.project_name_input = QLineEdit(self)
        self.project_name_input.setPlaceholderText("Enter project name (default: My Segmentation Project)")

        self.create_project_button = QPushButton("Create Project", self)
        self.create_project_button.clicked.connect(self.open_label_studio)

        self.existing_project_label = QLabel("Select Existing Project:")
        self.existing_project_dropdown = QComboBox(self)

        self.upload_images_masks_button = QPushButton("Upload Images and Masks", self)
        self.upload_images_masks_button.clicked.connect(self.upload_images_and_masks)

        layout.addWidget(QLabel("API Key:"), 0, 0)
        layout.addWidget(self.api_key_input, 0, 1)
        layout.addWidget(self.save_api_key_button, 0, 2)

        layout.addWidget(self.start_label_studio_button, 1, 0, 1, 3)

        layout.addWidget(QLabel("Project Name:"), 2, 0)
        layout.addWidget(self.project_name_input, 2, 1)
        layout.addWidget(self.create_project_button, 2, 2)

        layout.addWidget(self.existing_project_label, 3, 0)
        layout.addWidget(self.existing_project_dropdown, 3, 1)
        layout.addWidget(self.upload_images_masks_button, 3, 2)

        self.setLayout(layout)


    def load_existing_projects(self):
        if not self.api_key:
            print("API key not set. Please enter API key.")
            return
        try:
            headers = {'Authorization': f'Token {self.api_key}', 'Content-Type': 'application/json'}
            response = requests.get(f"{LABEL_STUDIO_URL}/api/projects", headers=headers)
            projects_data = response.json()
            
            if 'results' not in projects_data:
                print("Unexpected data format received from API")
                return
            
            projects = projects_data['results']
            self.existing_project_dropdown.clear()
            for project in projects:
                if isinstance(project, dict) and 'title' in project and 'id' in project:
                    self.existing_project_dropdown.addItem(project['title'], str(project['id']))
                else:
                    print(f"Unexpected project format: {project}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to load projects: {e}")


    @pyqtSlot()
    def save_api_key(self):
        self.api_key = self.api_key_input.text()
        if not self.api_key:
            print("API key cannot be empty.")
            return
        self.user_model.label_studio_api_key = self.api_key
        self.user_operation.update_api_key(self.user_model.id, self.api_key)
        self.api_key_input.setDisabled(True)

    @pyqtSlot()
    def select_root_folder(self):
        self.root_folder = QFileDialog.getExistingDirectory(self, "Select Root Folder")
        if self.root_folder:
            self.start_label_studio_thread = WorkerThread(self.start_label_studio, self.root_folder)
            self.start_label_studio_thread.finished.connect(lambda: QTimer.singleShot(5000, self.check_and_load_projects))
            self.start_label_studio_thread.start()

    def check_and_load_projects(self):
        if self.is_label_studio_running():
            self.load_existing_projects()
            return True
        else:
            print("Label Studio is not running. Please ensure the server is up and try again.")
            QTimer.singleShot(10000, self.check_and_load_projects)  # Retry after 5 seconds
            return False
        
    def is_label_studio_running(self):
        try:
            response = requests.get(LABEL_STUDIO_URL)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


    @pyqtSlot()
    def start_label_studio(self, root_folder):
        try:
            os.environ['LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT'] = root_folder
            os.environ['LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED'] = 'True'
            if os.name == 'nt':  # For Windows
                cmd = 'start cmd /k label-studio start --port 8080'
            elif os.name == 'posix':  # For Unix-based systems (Linux, MacOS)
                cmd = 'gnome-terminal -- bash -c "label-studio start --port 8080; exec bash"'
            else:
                print("Unsupported OS")
                return
            subprocess.Popen(cmd, shell=True)
            print("Starting Label Studio...")
        except Exception as e:
            print(f"Error: {e}")

    @pyqtSlot()
    def open_label_studio(self):
        try:
            project_name = self.project_name_input.text() or "My Segmentation Project"
            self.project = create_segmentation_project(project_name, self.api_key)
            #project_url = f"http://localhost:8080/projects/{self.project['id']}"
            #webbrowser.open(project_url)
            QTimer.singleShot(50, self.check_and_load_projects)
        except Exception as e:
            print(f"Error: {e}")

    @pyqtSlot()
    def upload_images_and_masks(self):
        try:

            # Get the selected project from the dropdown
            selected_project_id = self.existing_project_dropdown.currentData()
            if not selected_project_id:
                print("Project not selected. Please select a project first.")
                return
            
            local_storage_root_folder = get_local_storage_root_folder(selected_project_id, self.api_key)

            if local_storage_root_folder:
                self.root_folder = local_storage_root_folder
                im_index = self.root_folder.rfind("/")
                self.root_folder = self.root_folder[:im_index].replace('/', '\\')
                print(f"Using existing local storage root folder: {self.root_folder}")
            
            elif not self.root_folder:
                print("Root folder not selected. Please select a root folder first.")
                return
            
            # Get all images and masks
            images_folder = os.path.join(self.root_folder, 'images')
            masks_folder = os.path.join(self.root_folder, 'masks')

            images = get_file_paths(images_folder, ".jpg")
            masks = get_file_paths(masks_folder, ".tif")

            if len(images) != len(masks):
                raise ValueError("The number of images and masks does not match.")
            

             # Check if local storage already exists for this project
            storages = get_local_storages(selected_project_id, self.api_key)
            
            if storages:
                for storage in storages:
                    sync_local_storage(storage['id'], self.api_key)
            else:
                # Create and sync local storage if it doesn't exist
                storage = create_local_storage(selected_project_id, images_folder, self.api_key)
                sync_local_storage(storage['id'], self.api_key)

            # Check existing tasks in the project
            existing_tasks = get_existing_tasks(selected_project_id, self.api_key)

            # Filter out new images that are not in existing tasks
            new_images = []
            new_masks = []
            task_ids = []

            for image_path, mask_path in zip(images, masks):
                image_url = encode_image_url(image_path, self.root_folder)
                if image_url in existing_tasks:
                    task_id = existing_tasks[image_url]
                    if not task_has_annotation(task_id, self.api_key):
                        new_images.append(image_path)
                        new_masks.append(mask_path)
                        task_ids.append(task_id)

            if len(new_images) == 0:
                print("No new images to upload.")
                return
            
            print(f"Annotation upload started with : {len(new_masks)} new prediction masks..")
             # Start the upload thread
            self.upload_thread = WorkerThread(create_and_upload_annotations,
                                          new_images,
                                          new_masks,
                                          task_ids,
                                          "TWDamaged",
                                          "tag",
                                          "image",
                                          self.api_key)
            self.upload_thread.start()
        except Exception as e:
            print(f"Error: {e}")
