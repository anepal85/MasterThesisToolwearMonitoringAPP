from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem
from typing import List
from models.model import UserInputToolWearDB

class OldConfigsWidget(QWidget):
    def __init__(self, configs: List[UserInputToolWearDB]):
        super().__init__()
        self.configs = configs
        self.setWindowTitle("Vorhandene Configs")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Populate table
        self.populate_table(self.configs)

    def populate_table(self, configs):
        # Define headers
        headers = ["ID", "Werkstoff", "Definierter VBmax Value", "Definierter VBmax Unit", 
                "Schnittgeschwindigkeit Value", "Schnittgeschwindigkeit Unit",
                "Vorschub Value", "Vorschub Unit", "Schnitttiefe Value", "Schnitttiefe Unit",
                "Kühlung", "Werkzeugtyp", "Schneidstoff", "Schneide",
                "Beschichtung", "Surface", "Created At"]
        
        # Set column count and headers
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Set row count
        self.table.setRowCount(len(configs))
        
        # Populate table with data
        for row, config in enumerate(configs):
            for col, header in enumerate(headers):
                # Check if the header ends with "_value"
                if header.endswith("_value"):
                    # Get the base attribute name without "_value"
                    base_attr_name = header[:-len("_value")]
                    # Check if the base attribute exists in config
                    if hasattr(config, base_attr_name):
                        # Get the value of the base attribute
                        value = getattr(config, base_attr_name)
                    else:
                        value = ""  # Set an empty string if attribute doesn't exist
                else:
                    # Get attribute value dynamically using getattr
                    value = getattr(config, header.lower().replace(" ", "_"))
                # Create QTableWidgetItem with the attribute value
                item = QTableWidgetItem(str(value))
                # Set the item in the table
                self.table.setItem(row, col, item)

        # Resize columns and rows to contents
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
