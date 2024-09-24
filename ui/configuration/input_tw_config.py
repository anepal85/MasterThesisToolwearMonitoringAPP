from datetime import datetime
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from database.operations.toolwear_damage.toolwear_damage_operation import ToolWearDamageOperation
from database.operations.userinput_toolwear.userinput_toolwear_operation import UserInputToolWearOperation
from schemas.user import UserModel
from schemas.userinput_toolwear import UserInputToolWearModel
from ui.configuration.baseinput_widget import InputComboBoxWidget, InputLineEditWidget 
from ui.configuration.export.export_widget import ExportWidget
from ui.configuration.old_configs import OldConfigsWidget
from ui.configuration.select_folder import FolderSelectorWidget
from PyQt5.QtCore import pyqtSignal 


class ToolEntryWidget(QWidget):
    config_id_changed = pyqtSignal(int)

    def __init__(self, userinput_toolwear_operation: UserInputToolWearOperation, user_model: UserModel, toolwear_damage_operation: ToolWearDamageOperation):
        super().__init__()
        self.setStyleSheet("font-size: 18px;")
        self.old_configs_widget = None
        self.userinput_toolwear_operation = userinput_toolwear_operation
        self.toolwear_damage_operation = toolwear_damage_operation 
        self.old_cofigs_id_list = None 
        self.user_model = user_model 
        self.init_ui()

    def fetch_updated_ids(self):
        return [str(el.id) for el in self.userinput_toolwear_operation.get_all_configs_ordered()]
    
    def update_id_combobox(self, default:str = None):
        # Clear the existing items in the combobox
        self.id_combobox.clear()
        if default is not None:
            self.id_combobox.addItem(default)
        updated_ids = self.fetch_updated_ids()
        self.id_combobox.addItems(updated_ids)
        self.id_combobox.setCurrentIndex(0) 

    def update_combobox_selection(self, value:str):
        self.id_combobox.addItem(value)
        new_index = self.id_combobox.findText(value)
        if new_index != -1:
            self.id_combobox.setCurrentIndex(new_index)

    def init_ui(self):
        layout = QVBoxLayout()
        # Header row
        header_layout = QHBoxLayout()
        # Select ID dropdown
        self.select_id_label = QLabel("Wähle Configuration ID:")
        self.id_combobox = QComboBox()
        self.update_id_combobox("Neue Erstellen")       
        self.id_combobox.currentIndexChanged.connect(self.populate_widgets_by_id)
        self.id_combobox.currentIndexChanged.connect(self.notify_selected_id_to_homewidget)

        self.delete_button = QPushButton("Löschen")
        self.delete_button.clicked.connect(self.delete_by_id)

        # Ansehen button
        self.view_data_button = QPushButton("Ansehen")

        self.view_data_button.clicked.connect(self.show_old_configs)

        header_layout.addWidget(self.select_id_label, 0)
        header_layout.addWidget(self.id_combobox, 1)
        header_layout.addWidget(self.delete_button, 1)
        header_layout.addWidget(self.view_data_button, 1)
        header_layout.setContentsMargins(10,0,0,0)

        layout.addLayout(header_layout)

        # Columns for Werkzeug and Process
        self.columns_layout = QHBoxLayout()

        # Werkzeug column
        self.werkzeug_layout = self.populate_werkzeug_widgets(default_data=None, default_data_unit=None)#QVBoxLayout()
        self.werkzeug_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.columns_layout.addLayout(self.werkzeug_layout)

        # Process column
        self.process_layout = self.populate_process_widgets(default_data=None, default_data_unit=None)
        # self.process_layout = QVBoxLayout()
        self.process_layout.setAlignment(Qt.AlignTop)

        self.columns_layout.addLayout(self.process_layout)
        layout.addLayout(self.columns_layout)

        submit_button = QPushButton("Abgabe")
        submit_button.clicked.connect(self.submit_data)
        layout.addWidget(submit_button, alignment=Qt.AlignTop)
        
        # self.folder_selector = ExportWidget(self.userinput_toolwear_operation)
        # layout.addWidget(self.folder_selector, alignment=Qt.AlignTop)

        self.export =  ExportWidget(self.userinput_toolwear_operation, self.toolwear_damage_operation)
        layout.addWidget(self.export, alignment=Qt.AlignTop)

        self.setLayout(layout)

    def delete_by_id(self):
        try:
            if not self.user_model.is_admin:
                raise PermissionError("You do not have permission to delete records")
            
            user_input_data_id = int(self.id_combobox.currentText())
            
            # Check if the ID is valid
            if user_input_data_id is None:
                return
            # Retrieve user input data from the database
            self.userinput_toolwear_operation.delete_user_input_data(user_input_data_id)
            self.populate_widgets_by_id(0)
            self.update_id_combobox("Neue Erstellen")
            QMessageBox.information(self, "Success", f"Configuration with ID = {user_input_data_id} deleted successfully.")
        
        except PermissionError as pe:
            QMessageBox.critical(self, "Permission Error", str(pe))

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def set_process_and_werkzeug_layout(self, werkzeug_layout , process_layout):
         self.columns_layout.addLayout(werkzeug_layout)
         self.columns_layout.addLayout(process_layout)

    def clear_process_and_werkzeug_layout(self):
        self.clear_layout(self.columns_layout)
        self.clear_layout(self.process_layout)
        self.clear_layout(self.werkzeug_layout)

    def populate_werkzeug_widgets(self, default_data, default_data_unit):
        werkzeug_layout =  QVBoxLayout()
        werkzeug_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        werkzeug_header_label = QLabel("Werkzeug")
        werkzeug_header_label.setAlignment(Qt.AlignCenter)
        werkzeug_layout.addWidget(werkzeug_header_label)
        werkzeug_input_widgets = []

        if default_data is not None:
            werkzeug_input_widgets = [
                InputLineEditWidget("Definierter VBmax:", default_value=default_data[0], units_list=["mm", "inch", "µm"], default_unit_value=default_data_unit[0] if default_data_unit else None, numerical_input=True),
                InputLineEditWidget("Werkzeugtyp:", default_value=default_data[1]),
                InputLineEditWidget("Schneidstoff:", default_value=default_data[2]),
                InputLineEditWidget("Schneide:", default_value=default_data[3]),
                InputLineEditWidget("Beschichtung:", default_value=default_data[4]),
                InputComboBoxWidget("Surface:", ["HFF", "NFF", "SF"], default_value=default_data[5])
            ]
        else:
            werkzeug_input_widgets = [
                InputLineEditWidget("Definierter VBmax:", units_list=["mm", "inch", "µm"], default_unit_value=default_data_unit[0] if default_data_unit else None, numerical_input=True),
                InputLineEditWidget("Werkzeugtyp:"),
                InputLineEditWidget("Schneidstoff:"),
                InputLineEditWidget("Schneide:"),
                InputLineEditWidget("Beschichtung:"),
                InputComboBoxWidget("Surface:", ["HFF", "NFF", "SF"])
            ]
        for input_widget in werkzeug_input_widgets:
            werkzeug_layout.addWidget(input_widget)
        return werkzeug_layout 

    def populate_process_widgets(self, default_data, default_data_unit):
        # Process column
        process_layout = QVBoxLayout()
        process_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        process_layout.setAlignment(Qt.AlignTop)

        process_header_label = QLabel("Prozess")
        process_header_label.setAlignment(Qt.AlignCenter)
        process_layout.addWidget(process_header_label)
        process_input_widgets = []

        if default_data is not None:
            process_input_widgets = [
                InputComboBoxWidget("Werkstoff:", self.unique_valuesfrom_user_toolwear("werkstoff"), True, default_value=default_data[0]),
                InputLineEditWidget("Schnittgeschwindigkeit:", default_value=default_data[1], units_list=["m/s", "m/min"], default_unit_value=default_data_unit[1] if default_data_unit else None, numerical_input=True),
                InputLineEditWidget("Vorschub:", default_value=default_data[2], units_list=["mm"], default_unit_value=default_data_unit[2] if default_data_unit else None, numerical_input=True),
                InputLineEditWidget("Schnitttiefe:", default_value=default_data[3], units_list=["mm"], default_unit_value=default_data_unit[3] if default_data_unit else None, numerical_input=True),
                InputComboBoxWidget("Kühlung:", self.unique_valuesfrom_user_toolwear("kühlung"), True, default_value=default_data[4]),
                FolderSelectorWidget("Bildspeicherordner: ", default_value=default_data[5])
            ]
        else:
            process_input_widgets = [
                InputComboBoxWidget("Werkstoff:", self.unique_valuesfrom_user_toolwear("werkstoff"), True),
                InputLineEditWidget("Schnittgeschwindigkeit:", units_list=["m/s", "m/min"], default_unit_value=default_data_unit[1] if default_data_unit else None, numerical_input=True),
                InputLineEditWidget("Vorschub:", units_list=["mm"], default_unit_value=default_data_unit[2] if default_data_unit else None, numerical_input=True),
                InputLineEditWidget("Schnitttiefe:", units_list=["mm"], default_unit_value=default_data_unit[3] if default_data_unit else None, numerical_input=True),
                InputComboBoxWidget("Kühlung:", self.unique_valuesfrom_user_toolwear("kühlung"), True),
                FolderSelectorWidget("Bildspeicherordner: ")
            ]

        for input_widget in process_input_widgets:
            process_layout.addWidget(input_widget)

        return process_layout 

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    self.clear_layout(sub_layout)

    def unique_valuesfrom_user_toolwear(self, column_name:str)-> list[str]:
        return self.userinput_toolwear_operation.get_unique_column_values(column_name)
    
    def notify_selected_id_to_homewidget(self, index):
        if index <= 0:
            ## this will be default id 
            self.config_id_changed.emit(0)
            return 
        user_input_data_id = int(self.id_combobox.currentText())            
        if user_input_data_id is None:
            return
        
        self.config_id_changed.emit(user_input_data_id)
        

        
    def populate_widgets_by_id(self, index):
        if index <= 0:
            self.clear_process_and_werkzeug_layout()
            # # Add Werkzeug input widgets
            self.werkzeug_layout = self.populate_werkzeug_widgets(default_data=None, default_data_unit=None)
            self.process_layout = self.populate_process_widgets(default_data=None, default_data_unit=None)
            self.set_process_and_werkzeug_layout(self.werkzeug_layout, self.process_layout)
            return

        try:
            user_input_data_id = int(self.id_combobox.currentText())            
            # Check if the ID is valid
            if user_input_data_id is None:
                return
            # Retrieve user input data from the database
            user_input_data = self.userinput_toolwear_operation.get_user_input_data(int(user_input_data_id))
            
            # Extract default data and default data unit
            default_data_werkzeug = [user_input_data.definierter_vbmax_value, 
                                    user_input_data.werkzeugtyp, 
                                    user_input_data.schneidstoff, 
                                    user_input_data.schneide, 
                                    user_input_data.beschichtung, 
                                    user_input_data.surface]
            
            default_data_process = [user_input_data.werkstoff, 
                                    user_input_data.schnittgeschwindigkeit_value, 
                                    user_input_data.vorschub_value, 
                                    user_input_data.schnitttiefe_value, 
                                    user_input_data.kühlung,
                                    user_input_data.images_folder]
            
            default_data_unit_process = [user_input_data.definierter_vbmax_unit, 
                                        user_input_data.schnittgeschwindigkeit_unit, 
                                        user_input_data.vorschub_unit, 
                                        user_input_data.schnitttiefe_unit]
            
            default_data_unit_werkzeug = [user_input_data.definierter_vbmax_unit] 
            self.clear_process_and_werkzeug_layout()

            # Populate process widgets
            self.process_layout = self.populate_process_widgets(default_data_process, default_data_unit_process)
            
            # Populate werkzeug widgets
            self.werkzeug_layout = self.populate_werkzeug_widgets(default_data_werkzeug, default_data_unit_werkzeug)
            
            self.set_process_and_werkzeug_layout(self.werkzeug_layout, self.process_layout)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    
    def get_input_from_layout(self, layout):
        # Extract user input from Werkzeug widgets
        widgets_values = []
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, InputLineEditWidget) or isinstance(widget, InputComboBoxWidget) or isinstance(widget, FolderSelectorWidget):
                label, value, unit = widget.get_input()
                widgets_values.append((label, value, unit))
        return widgets_values 
    
    def show_old_configs(self):
        old_configs = self.userinput_toolwear_operation.get_all_configs_ordered()
        if old_configs:
            self.show_table(old_configs)
        else:
            QMessageBox.information(None, "Info", "No old configurations found.")

    def show_table(self, configs):
        if not self.old_configs_widget:
            self.old_configs_widget = OldConfigsWidget(configs)
        else:
            self.old_configs_widget.populate_table(configs)
        self.old_configs_widget.show()
        
    def retrieve_data(self, data, values):
        for label, value, unit in values:
            if label in data:
                if unit:
                    data[label] = {"value": value, "unit": unit}
                else:
                    data[label] = value
        return data 

    def submit_data(self):

        # Check if required fields are not empty
        required_fields = [
            "werkstoff", "definierter_vbmax", "images_folder", "schnittgeschwindigkeit", "schneide",
            "vorschub", "schnitttiefe", "prozess", "werkzeugtyp", "schneidstoff", "beschichtung"
        ]

        # Retrieve values from input widgets
        werkzeug_values = [(label, value, unit) for label, value, unit in self.get_input_from_layout(self.werkzeug_layout)]
        process_values = [(label, value, unit) for label, value, unit in self.get_input_from_layout(self.process_layout)]

        # Check if required fields are not empty
        for label, value, unit in werkzeug_values + process_values:
            if label in required_fields and (not value.strip() if isinstance(value, str) else not value):
                QMessageBox.critical(self, "Error", f"Please fill in {label}.")
                return
            
        # Initialize variables for values
        data = {
            "werkstoff": None,
            "definierter_vbmax": {"value": None, "unit": None},
            "schnittgeschwindigkeit": {"value": None, "unit": None},
            "vorschub": {"value": None, "unit": None},
            "schnitttiefe": {"value": None, "unit": None},
            "kühlung": None,
            "werkzeugtyp": None,
            "schneidstoff": None,
            "schneide": None,
            "beschichtung": None,
            "surface":None,  
            "images_folder":None,
            "created_by" : self.user_model.id, 
            "created_at": datetime.now()
        }

        # Process values
        data = self.retrieve_data(data, werkzeug_values + process_values)

        # Validate numerical values
        numerical_fields = ["definierter_vbmax", "schnittgeschwindigkeit", "vorschub", "schnitttiefe"]
        for field in numerical_fields:
            value = data[field]["value"] if isinstance(data[field], dict) else None
            if value is not None:
                try:
                    data[field]["value"] = float(value)
                except ValueError:
                    QMessageBox.critical(None, "Error", f"{field.capitalize()} must be a numerical value.")
                    return None
                
        formatted_data = self.format_data(data)
        user_input_data = UserInputToolWearModel(**formatted_data)
        
        # Call the create_user_input_data method of UserInputToolWearOperation to store the user input data
        created = self.userinput_toolwear_operation.create_user_input_data(user_input_data)
        if created:
            latest_id = str(created.id)
            self.populate_widgets_by_id(created.id)
            self.update_combobox_selection(latest_id)
            QMessageBox.information(self, "Success", "Data submitted successfully.")

    def format_data(self, data):
        formatted_data = {}

        for key, value in data.items():
            if isinstance(value, dict):
                formatted_data[key + "_value"] = value["value"]
                if "unit" in value:
                    formatted_data[key + "_unit"] = value["unit"]
            else:
                formatted_data[key] = value
        
        return formatted_data


