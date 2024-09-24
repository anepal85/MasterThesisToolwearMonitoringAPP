import os 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox
from database.operations.toolwear_damage.toolwear_damage_operation import ToolWearDamageOperation
from database.operations.userinput_toolwear.userinput_toolwear_operation import UserInputToolWearOperation
from ui.configuration.export.exporter import CSVWriterWorker

class ExportWidget(QtWidgets.QWidget):
    def __init__(self, userinput_toolwear_operation: UserInputToolWearOperation, toolwear_damage_operation: ToolWearDamageOperation):
        super(ExportWidget, self).__init__()

        self.userinput_toolwear_operation = userinput_toolwear_operation
        self.toolwear_damage_operation = toolwear_damage_operation

        main_layout = QVBoxLayout(self)

        self.process_number_label = QLabel("Wähle Confiuration ID:")
        self.process_number_input = QComboBox()
        self.load_user_input_data_ids()

        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_data)

        firs_row_layout = QHBoxLayout()
        firs_row_layout.addWidget(self.process_number_label, 0)
        firs_row_layout.addWidget(self.process_number_input, 1)
        firs_row_layout.addWidget(self.export_button, 1)

        main_layout.addLayout(firs_row_layout)

        self.writer_worker = None

    def load_user_input_data_ids(self):
        try:
            user_input_data_list = self.userinput_toolwear_operation.get_all_configs_ordered()
            for user_input_data in user_input_data_list:
                self.process_number_input.addItem(str(user_input_data.id))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user input data IDs: {e}")

    def export_data(self):
        user_input_data_id = int(self.process_number_input.currentText())
        user_input_data = self.userinput_toolwear_operation.get_user_input_data(user_input_data_id)
        tool_wear_damage_rows = self.toolwear_damage_operation.get_all_toolwear_damage_by_user_input_data_id_ordered(user_input_data_id)

        file_path = os.path.join(user_input_data.images_folder, f'config_id_{user_input_data_id}.csv')

        if file_path:
            self.writer_worker = CSVWriterWorker(user_input_data, tool_wear_damage_rows, file_path)
            self.writer_worker.finished.connect(self.on_export_finished)
            self.writer_worker.error.connect(self.on_export_error)
            self.writer_worker.finished.connect(self.writer_worker.deleteLater)
            self.writer_worker.start()

    def on_export_finished(self):
        QMessageBox.information(self, "Success", "CSV file written successfully.")

    def on_export_error(self, error_message):
        QMessageBox.critical(self, "Error", f"Failed to write CSV file: {error_message}")

    def closeEvent(self, event):
        if self.writer_worker and self.writer_worker.isRunning():
            self.writer_worker.quit()
            self.writer_worker.wait()
        event.accept()
