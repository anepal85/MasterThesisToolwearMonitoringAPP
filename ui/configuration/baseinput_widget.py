# from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QComboBox, QHBoxLayout
# from PyQt5.QtGui import QDoubleValidator

# class InputWidget(QWidget):
#     def __init__(self, label_name, input_type, default_value = None, items=None, units_list=None, numerical_input=False):
#         super().__init__()
#         self.label = QLabel(label_name)
#         self.input_type = input_type
#         self.items = items
#         self.units_list = units_list
#         self.numerical_input = numerical_input

#         if self.input_type == "line_edit":
#             self.input_widget = QLineEdit()
#             if self.numerical_input:
#                 self.input_widget.setValidator(QDoubleValidator())
#             if default_value is not None:
#                 self.input_widget.setText(str(default_value))

#         elif self.input_type == "combo_box":
#             self.input_widget = QComboBox()
#             if self.items:
#                 self.input_widget.addItems(self.items)
                
#             if default_value is not None:
#                 index = self.input_widget.findText(default_value)
#                 if index != -1:
#                     self.input_widget.setCurrentIndex(index)


#         if self.units_list:
#             self.units_combo = QComboBox()
#             self.units_combo.addItems(self.units_list)

#         layout = QHBoxLayout()
#         layout.addWidget(self.label)
#         layout.addWidget(self.input_widget)
#         if self.units_list:
#             layout.addWidget(self.units_combo)
#         self.setLayout(layout)
    

#     def get_input(self):
#         # Sanitize label name
#         sanitized_label = self.label.text().replace(':', '').replace(' ', '_').lower()

#         if self.input_type == "line_edit":
#             return sanitized_label, self.input_widget.text(), self.units_combo.currentText() if self.units_list else None
#         elif self.input_type == "combo_box":
#             return sanitized_label, self.input_widget.currentText(), None
    
#     def set_input(self, value, unit_combo_value=None):
#         if self.input_type == "line_edit":
#             self.input_widget.setText(str(value))
#         elif self.input_type == "combo_box":
#             index = self.input_widget.findText(str(value))
#             if index != -1:
#                 self.input_widget.setCurrentIndex(index)
#             if unit_combo_value and self.units_list:
#                 index = self.units_combo.findText(str(unit_combo_value))
#                 if index != -1:
#                     self.units_combo.setCurrentIndex(index)


from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QComboBox, QHBoxLayout
from PyQt5.QtGui import QDoubleValidator

class InputLineEditWidget(QWidget):
    def __init__(self, label_name, default_value=None, units_list=None, default_unit_value=None, numerical_input=False):
        super().__init__()
        self.label = QLabel(label_name)
        self.units_list = units_list
        self.numerical_input = numerical_input

        self.input_widget = QLineEdit()
        if self.numerical_input:
            self.input_widget.setValidator(QDoubleValidator())
        if default_value is not None:
            self.input_widget.setText(str(default_value))

        self.units_combo = QComboBox()
        if self.units_list:
            self.units_combo.addItems(self.units_list)
            if default_unit_value is not None:
                index = self.units_combo.findText(default_unit_value)
                if index != -1:
                    self.units_combo.setCurrentIndex(index)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_widget)
        if self.units_list:
            layout.addWidget(self.units_combo)
        self.setLayout(layout)

    def get_input(self):
        sanitized_label = self.label.text().replace(':', '').replace(' ', '_').lower()
        return sanitized_label, self.input_widget.text(), self.units_combo.currentText() if self.units_list else None

    def set_value(self, value, unit=None):
        self.input_widget.setText(str(value))
        if self.units_list and unit is not None:
            index = self.units_combo.findText(str(unit))
            if index != -1:
                self.units_combo.setCurrentIndex(index)


class InputComboBoxWidget(QWidget):
    def __init__(self, label_name, items, editable = False, default_value=None):
        super().__init__()
        self.label = QLabel(label_name)
        if editable:
            self.input_widget = CustomComboBox(label_name)
        else:
            self.input_widget = QComboBox()
        self.input_widget.addItems(items)

        # If default_value is provided and not already in items, add it as an option
        if default_value and default_value not in items:
            self.input_widget.addItem(default_value)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_widget)
        self.setLayout(layout)

        if default_value is not None:
            self.set_input(default_value)

    def get_input(self):
        sanitized_label = self.label.text().replace(':', '').replace(' ', '_').lower()
        return sanitized_label, self.input_widget.currentText(), None

    def set_input(self, value):
        # Check if the value exists in the items, if not, add it
        if value not in [self.input_widget.itemText(i) for i in range(self.input_widget.count())]:
            self.input_widget.addItem(value)

        index = self.input_widget.findText(str(value))
        if index != -1:
            self.input_widget.setCurrentIndex(index)


from PyQt5.QtWidgets import QComboBox, QInputDialog

class CustomComboBox(QComboBox):
    def __init__(self, label_name:str, parent=None):
        super().__init__(parent)
        self.labelname = label_name 
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertAtCurrent)

        # Connect the signal for when the user has finished editing
        self.editTextChanged.connect(self.handleTextChanged)

    def handleTextChanged(self, text):
        # Check if the entered text is not empty and not already in the combobox
        if text and text not in [self.itemText(i) for i in range(self.count())]:
            reply = QInputDialog.getText(self, "Einfügen", "Wollen sie neuen Typ zu '{}' einfügen?".format(self.labelname),
                                         QLineEdit.Normal, text)
            if reply[1]:  # If the user confirms
                self.addItem(reply[0])  # Add the new item to the combobox
                self.setCurrentIndex(self.findText(reply[0]))

