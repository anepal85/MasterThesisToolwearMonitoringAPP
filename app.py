import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5 import QtWidgets
from PyQt5 import QtWidgets
from database.db_session import DBSession
from database.operations.dino_image.dino_image_operation import DinoImageOperation
from database.operations.ml_model.ml_model_operation import MLModelOperation
from database.operations.process_number.process_number_operation import CompletedProcessNumberOperation
from database.operations.toolwear_damage.toolwear_damage_operation import ToolWearDamageOperation
from database.operations.user.user_operation import UserOperation
from database.operations.userinput_toolwear.userinput_toolwear_operation import UserInputToolWearOperation
from schemas.ml_model import MLModel
from schemas.user import UserModel
from ui.MainWindow_ui import Ui_MainWindow
from ui.annotation.annotation_widget import AnnotationWidget
from ui.authentication.login import LoginWindow
from ui.authentication.registration import RegisterWindow
from ui.configuration.input_tw_config import ToolEntryWidget
from ui.home.home import HomeWidget
from PyQt5.QtCore import pyqtSignal
import random , os 
from datetime import datetime
from ui.information.info_widget import SoftwareInfoWidget



class MainMenuWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    logout_signal = pyqtSignal()
    config_id_updated = pyqtSignal(int)

    def __init__(self, user_model: UserModel, mlmodel_operation: MLModelOperation, 
                    userinput_toolwear_operation : UserInputToolWearOperation, 
                    proces_number_operation: CompletedProcessNumberOperation,
                    toolwear_damage_operation : ToolWearDamageOperation,
                    dino_image_operation : DinoImageOperation, 
                    user_operation: UserOperation):
        
        super().__init__()
        self.setupUi(self)
        
        self.user_model = user_model 
        self.mlmodel_operation = mlmodel_operation
        self.userinput_toolwear_operation = userinput_toolwear_operation 

        # Set geometry to 1200x900
        #self.setMinimumSize(950, 650) 

        self.settings_btn.setText(f'@{self.user_model.name}')
        self.settings_btn.clicked.connect(self.logout)
        
        ## Menubuttons
        self.annotation_button.clicked.connect(self.show_config_input_page)

        self.training_button.clicked.connect(self.show_export_page)

        self.home_button.clicked.connect(self.show_home_page)

        self.visualization_button.clicked.connect(self.show_vizualization_page)
        
        # Create the QStackedWidget and add it to the container widget
        self.stacked_widget = QtWidgets.QStackedWidget(self.content_frame)
        self.horizontalLayout_8.addWidget(self.stacked_widget)
        
        self.home_widget = HomeWidget(self.mlmodel_operation, self.user_model,
                                      self.userinput_toolwear_operation, proces_number_operation, 
                                      toolwear_damage_operation, dino_image_operation)
        
        self.stacked_widget.addWidget(self.home_widget)

        self.toolwear_user_entry_widget = ToolEntryWidget(self.userinput_toolwear_operation, self.user_model, toolwear_damage_operation)
        self.stacked_widget.addWidget(self.toolwear_user_entry_widget)

        self.toolwear_user_entry_widget.config_id_changed.connect(self.handle_config_id_changed)
        self.config_id_updated.connect(self.home_widget.update_config_id)

        self.export_widget = AnnotationWidget(user_operation, self.user_model)
        self.stacked_widget.addWidget(self.export_widget)

        self.visualize_widget = SoftwareInfoWidget() #VisualizationWidget(self.userinput_toolwear_operation, toolwear_damage_operation)
        self.stacked_widget.addWidget(self.visualize_widget)

        self.stacked_widget.setCurrentIndex(0)

         # Connect hamburger menu button signal
        self.menu_btn.clicked.connect(self.toggle_menu)

        # Initialize menu state
        self.menu_opened = False

    def handle_config_id_changed(self, selected_id):
        if selected_id > 0:
            self.config_id_updated.emit(selected_id)
        
    def toggle_menu(self):
        if not self.menu_opened:
            # Show menu
            self.menu_frame.show()
            # Show icons but hide label
            #self.cockpiticonlabel.show()
        else:
            # Hide menu
            self.menu_frame.hide()
            # Show label but hide icons
            #self.cockpiticonlabel.hide()
        self.menu_opened = not self.menu_opened
    
    def logout(self):
        self.logout_signal.emit()
        self.close()
                                                                 
    def show_home_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_config_input_page(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_export_page(self):
        self.stacked_widget.setCurrentIndex(2)

    def show_vizualization_page(self):
        self.stacked_widget.setCurrentIndex(3)


class MainWindow(QWidget):
    def __init__(self, user_operation: UserOperation, mlmodel_operation: MLModelOperation, 
                 userinput_toolwear_operation: UserInputToolWearOperation, 
                 proces_number_operation: CompletedProcessNumberOperation, 
                 toolwear_damage_operation: ToolWearDamageOperation, 
                 dino_image_operation: DinoImageOperation):
        super(MainWindow, self).__init__()
        #self.setGeometry(100, 100, 300, 150)
        self.setWindowTitle("AdaptX Toolwear System")

        self.user_operation = user_operation 
        self.mlmodel_operation = mlmodel_operation 
        self.userinput_toolwear_operation = userinput_toolwear_operation
        self.proces_number_operation = proces_number_operation
        self.toolwear_damage_operation = toolwear_damage_operation
        self.dino_image_operation = dino_image_operation

        self.login_window = LoginWindow(parent = self, user_operation=self.user_operation)
        self.register_window = RegisterWindow(parent = self, user_operation=self.user_operation)

        # Initially show login window
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.login_window)
        self.setLayout(self.layout)

        # Connect the custom signal from RegisterWindow to a slot method
        self.register_window.register_successful.connect(self.handle_registration_successful)

    def show_register_window(self):
        register_window = RegisterWindow(parent = self, user_operation=self.user_operation)
        self.clear_layout()
        self.layout.addWidget(register_window)


    def show_login_window(self):
        login_window = LoginWindow(parent = self, user_operation=self.user_operation)
        self.clear_layout()
        self.layout.addWidget(login_window)

    def show_main_window(self, username):
        userModel = self.user_operation.get_user_by_name(username)
        main_menu_window = MainMenuWindow(userModel, self.mlmodel_operation, self.userinput_toolwear_operation,
                                          self.proces_number_operation, self.toolwear_damage_operation,
                                          self.dino_image_operation, self.user_operation)
        self.clear_layout()
        self.layout.addWidget(main_menu_window)
        # Connect the logout_signal to show_login_window method
        main_menu_window.logout_signal.connect(self.show_login_window)

    def clear_layout(self):
        # Clear the existing layout
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout()

    # Slot method to handle the action when registration is successful
    def handle_registration_successful(self, success):
        if success:
            self.show_login_window()


def create_ml_model(model_path: str, ml_model_operation: MLModelOperation)-> MLModel:

    # # Assuming you have loaded your .hdf model into a variable called "loaded_model"
    # with open(os.path.join(model_path, 'res34_backbone_200epochs_512_v3.hdf5'), 'rb') as file:
    #     loaded_model_bytes = file.read()



    # Create an MLModel instance with the loaded model data
    ml_model_data = MLModel(name="AttentionResNet34", 
                            ml_model_path=os.path.join(model_path, 'with_more_data','attention_res34_backbone_200epochs_256_v6.hdf5'),
                            epochs_trained=200, input_im_height=256, input_im_width=256,created_at= datetime.now()
                            )
    return ml_model_operation.create_ml_model(ml_model_data)


if __name__ == "__main__":
    # Global DBSession instance
    db_session = DBSession("sqlite")
    app = QApplication(sys.argv)
    user_operation = UserOperation(db_session)
    mlmodel_operation = MLModelOperation(db_session)
    userinput_toolwear_operation = UserInputToolWearOperation(db_session)
    proces_number_operation = CompletedProcessNumberOperation(db_session)
    toolwear_damage_operation = ToolWearDamageOperation(db_session)
    dino_image_operation = DinoImageOperation(db_session)
    main_window = MainWindow(user_operation, mlmodel_operation, userinput_toolwear_operation,
                              proces_number_operation, toolwear_damage_operation, dino_image_operation)
    #ml_model = create_ml_model(r"D:\MA\App\model_output\resnet34", mlmodel_operation)
    #user_model = user_operation.get_user_by_name("admin")
    #main_window = MainMenuWindow(user_model, mlmodel_operation, userinput_toolwear_operation,
    #                             proces_number_operation, toolwear_damage_operation,
    #                             dino_image_operation, user_operation)
    main_window.show()
    sys.exit(app.exec_())


