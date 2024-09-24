from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QComboBox, QRadioButton, QPushButton, QHBoxLayout, QButtonGroup, QGridLayout, QMessageBox 
from database.operations.userinput_toolwear.userinput_toolwear_operation import UserInputToolWearOperation
from schemas.userinput_toolwear import UserInputToolWearModel
from datetime import datetime
from pydantic import ValidationError

from ui.configuration.old_configs import OldConfigsWidget

class ToolWearEntryWidget(QWidget):
    def __init__(self, userinput_toolwear_operation: UserInputToolWearOperation):
        super().__init__()
        self.setStyleSheet("font-size: 18px;")
        self.old_configs_widget = None

        self.init_ui()
        self.userinput_toolwear_operation = userinput_toolwear_operation

    def init_ui(self):
        # Grid Layout
        grid_layout = QGridLayout()

        # Werkstoff
        grid_layout.addWidget(QLabel("Werkstoff:"), 0, 0)
        self.edit_werkstoff = QLineEdit()
        grid_layout.addWidget(self.edit_werkstoff, 0, 1)

        # Definierter VBmax
        grid_layout.addWidget(QLabel("Definierter VBmax:"), 1, 0)
        self.edit_vbmax = QLineEdit()
        grid_layout.addWidget(self.edit_vbmax, 1, 1)

        # Magnification
        grid_layout.addWidget(QLabel("Magnification:"), 2, 0)
        self.edit_magnification = QLineEdit()
        grid_layout.addWidget(self.edit_magnification, 2, 1)

        # Schnittgeschwindigkeit
        grid_layout.addWidget(QLabel("Schnittgeschwindigkeit:"), 3, 0)
        self.edit_schnittgeschwindigkeit = QLineEdit()
        grid_layout.addWidget(self.edit_schnittgeschwindigkeit, 3, 1)

        # Vorschub
        grid_layout.addWidget(QLabel("Vorschub:"), 4, 0)
        self.edit_vorschub = QLineEdit()
        grid_layout.addWidget(self.edit_vorschub, 4, 1)

        # Schnitttiefe
        grid_layout.addWidget(QLabel("Schnitttiefe:"), 5, 0)
        self.edit_schnitttiefe = QLineEdit()
        grid_layout.addWidget(self.edit_schnitttiefe, 5, 1)

        # Prozess
        grid_layout.addWidget(QLabel("Prozess:"), 6, 0)
        self.edit_prozess = QLineEdit()
        grid_layout.addWidget(self.edit_prozess, 6, 1)

        # grid_layout.addWidget(QLabel("Prozess:"), 6, 0)
        # self.combo_prozess = QComboBox()
        # self.combo_prozess.addItems(["Process 1", "Process 2", "Process 3"])
        # grid_layout.addWidget(self.combo_prozess, 6, 1)

        # Kühlung
        kühlung_layout = QHBoxLayout()
        self.radio_kühlung_ja = QRadioButton("Ja")
        self.radio_kühlung_nein = QRadioButton("Nein")
        kühlung_layout.addWidget(self.radio_kühlung_ja)
        kühlung_layout.addWidget(self.radio_kühlung_nein)
        grid_layout.addWidget(QLabel("Kühlung:"), 7, 0)
        grid_layout.addLayout(kühlung_layout, 7, 1)

        # Group Kühlung Radio Buttons
        self.kühlung_button_group = QButtonGroup(self)
        self.kühlung_button_group.addButton(self.radio_kühlung_ja)
        self.kühlung_button_group.addButton(self.radio_kühlung_nein)

        # Werkzeugtyp
        grid_layout.addWidget(QLabel("Werkzeugtyp:"), 8, 0)
        self.edit_werkzeugtyp = QLineEdit()
        grid_layout.addWidget(self.edit_werkzeugtyp, 8, 1)

        # Schneidstoff
        grid_layout.addWidget(QLabel("Schneidstoff:"), 9, 0)
        self.edit_schneidstoff = QLineEdit()
        grid_layout.addWidget(self.edit_schneidstoff, 9, 1)

        # Schneide
        grid_layout.addWidget(QLabel("Schneide:"), 10, 0)
        self.edit_schneide = QLineEdit()
        grid_layout.addWidget(self.edit_schneide, 10, 1)

        # Beschichtung
        grid_layout.addWidget(QLabel("Beschichtung:"), 11, 0)
        self.edit_beschichtung = QLineEdit()
        grid_layout.addWidget(self.edit_beschichtung, 11, 1)

        # Surface
        surface_layout = QHBoxLayout()
        self.radio_hff = QRadioButton("HFF")
        self.radio_nff = QRadioButton("NFF")
        self.radio_sf = QRadioButton("SF")
        surface_layout.addWidget(self.radio_hff)
        surface_layout.addWidget(self.radio_nff)
        surface_layout.addWidget(self.radio_sf)
        grid_layout.addWidget(QLabel("Surface:"), 12, 0)
        grid_layout.addLayout(surface_layout, 12, 1)

        # Group Surface Radio Buttons
        self.surface_button_group = QButtonGroup(self)
        self.surface_button_group.addButton(self.radio_hff)
        self.surface_button_group.addButton(self.radio_nff)
        self.surface_button_group.addButton(self.radio_sf)

        # Submit Button
        self.btn_submit = QPushButton("Abgabe")
        self.btn_submit.clicked.connect(self.submit_data)
        grid_layout.addWidget(self.btn_submit, 13, 0, 1, 2)

        # See Old Config Button
        self.btn_see_old_config = QPushButton("Ansehen")
        self.btn_see_old_config.clicked.connect(self.show_old_configs)
        grid_layout.addWidget(self.btn_see_old_config, 14, 0, 1, 2)

        self.setLayout(grid_layout)

    def submit_data(self):
        # Retrieve values from widgets
        werkstoff = self.edit_werkstoff.text()
        vbmax_text = self.edit_vbmax.text()
        magnification_text = self.edit_magnification.text()
        schnittgeschwindigkeit_text = self.edit_schnittgeschwindigkeit.text()
        vorschub_text = self.edit_vorschub.text()
        schnitttiefe_text = self.edit_schnitttiefe.text()
        prozess = self.edit_prozess.text()

        # Retrieve Kühlung selection from button group
        kühlung = "Ja" if self.kühlung_button_group.checkedButton() == self.radio_kühlung_ja else "Nein"
        surface = None
        if self.surface_button_group.checkedButton() == self.radio_hff:
            surface = "HFF"
        elif self.surface_button_group.checkedButton() == self.radio_nff:
            surface = "NFF"
        elif self.surface_button_group.checkedButton() == self.radio_sf:
            surface = "SF"

        # Additional fields
        werkzeugtyp = self.edit_werkzeugtyp.text()
        schneidstoff = self.edit_schneidstoff.text()
        schneide = self.edit_schneide.text()
        beschichtung = self.edit_beschichtung.text()
        hff = self.radio_hff.isChecked()
        nff = self.radio_nff.isChecked()
        sf = self.radio_sf.isChecked()

        # Get the current timestamp
        created_at = datetime.now()

        # Check if required fields are not empty
        if not all([werkstoff, vbmax_text, magnification_text, schnittgeschwindigkeit_text, 
                    vorschub_text, schnitttiefe_text, prozess, surface]):
            QMessageBox.critical(None, "Error", "Please fill in all required fields.")
            return

        # Convert text fields to float if they are not empty
        try:
            vbmax = float(vbmax_text)
            magnification = float(magnification_text)
            schnittgeschwindigkeit = float(schnittgeschwindigkeit_text)
            vorschub = float(vorschub_text)
            schnitttiefe = float(schnitttiefe_text)
        except ValueError:
            QMessageBox.critical(None, "Error", "Please enter valid numeric values for VBmax, Magnification, Schnittgeschwindigkeit, Vorschub, and Schnitttiefe.")
            return

        # Create a UserInputToolWearModel instance
        user_input_data = UserInputToolWearModel(
            werkstoff=werkstoff,
            definierter_vbmax=vbmax,
            magnification=magnification,
            schnittgeschwindigkeit=schnittgeschwindigkeit,
            vorschub=vorschub,
            schnitttiefe=schnitttiefe,
            prozess=prozess,
            kühlung=kühlung,
            werkzeugtyp=werkzeugtyp,
            schneidstoff=schneidstoff,
            schneide=schneide,
            beschichtung=beschichtung,
            hff=hff,
            nff=nff,
            sf=sf,
            created_at=created_at
        )

        # Call the create_user_input_data method of UserInputToolWearOperation to store the user input data
        self.userinput_toolwear_operation.create_user_input_data(user_input_data)
        QMessageBox.information(None, "Success", "Data submitted successfully.")

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

    