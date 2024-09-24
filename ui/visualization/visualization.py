from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDateEdit, QPushButton
from PyQt5.QtCore import QDate

from database.operations.toolwear_damage.toolwear_damage_operation import ToolWearDamageOperation
from database.operations.userinput_toolwear.userinput_toolwear_operation import UserInputToolWearOperation
from ui.visualization.damage_plot_canvas import PlotCanvas

class VisualizationWidget(QtWidgets.QWidget):

    def __init__(self, userinput_toolwear_operation: UserInputToolWearOperation, 
                 toolwear_damage_operation: ToolWearDamageOperation) -> None:
        super(VisualizationWidget, self).__init__()

        # Set the font size for the widget
        self.setStyleSheet("font-size: 18px;")
        # Set the size policy to expanding
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.userinput_toolwear_operation = userinput_toolwear_operation
        self.toolwear_damage_operation = toolwear_damage_operation

        # Create the layout for the widget
        self.main_layout = QVBoxLayout(self)

        first_row_layout = QHBoxLayout()
        second_row_layout = QHBoxLayout()


        self.user_data_id_label = QLabel('Select ID:')
        self.user_data_id_combobox = QComboBox()
        self.user_data_id_combobox.addItems(self.get_user_data_ids())

        self.from_date_label = QLabel('From:')
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.from_date_edit.setCalendarPopup(True)

        self.to_date_label = QLabel('To:')
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setDate(QDate.currentDate())
        self.to_date_edit.setCalendarPopup(True)

        self.plot_button = QPushButton('Plot')
        self.plot_button.clicked.connect(self.plot_data)

        first_row_layout.addWidget(self.user_data_id_label)
        first_row_layout.addWidget(self.user_data_id_combobox)
        first_row_layout.addWidget(self.from_date_label)
        first_row_layout.addWidget(self.from_date_edit)
        first_row_layout.addWidget(self.to_date_label)
        first_row_layout.addWidget(self.to_date_edit)
        first_row_layout.addWidget(self.plot_button)

        # Second row layout for the plot
        self.plot_canvas = PlotCanvas(self)
        second_row_layout.addWidget(self.plot_canvas)

        # Add first row layout to the main layout
        self.main_layout.addLayout(first_row_layout)
        self.main_layout.addLayout(second_row_layout)
        self.setLayout(self.main_layout)


    def get_user_data_ids(self):
        return [str(el.id) for el in self.userinput_toolwear_operation.get_all_configs_ordered()]

    def plot_data(self):
        user_data_id = int(self.user_data_id_combobox.currentText())
        from_date = self.from_date_edit.date().toPyDate()
        to_date = self.to_date_edit.date().toPyDate()

        toolwear_damage_rows = self.toolwear_damage_operation.get_all_toolwear_damage_by_user_input_data_id_ordered(user_data_id)
        
        data = [{
            'created_at': result.created_at,
            'damage_area': result.damage_area,
            'damage_down': result.damage_down,
            'damage_up': result.damage_up
        } for result in toolwear_damage_rows if from_date <= result.created_at.date() <= to_date]

        self.plot_canvas.update_plot(data)
