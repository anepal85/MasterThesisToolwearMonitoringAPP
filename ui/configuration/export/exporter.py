import csv
from PyQt5.QtCore import QThread, pyqtSignal
from models.model import UserInputToolWearDB, ToolWearDamageDB
from datetime import datetime

class CSVWriterWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, user_input_data, tool_wear_damage_rows, output_file_path):
        super().__init__()
        self.user_input_data = user_input_data
        self.tool_wear_damage_rows = tool_wear_damage_rows
        self.output_file_path = output_file_path

    def format_datetime_fields(self, data_list):
        formatted_data = []
        for data in data_list:
            if isinstance(data, datetime):
                formatted_data.append(data.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                formatted_data.append(data)
        return formatted_data
    
    def format_data_as_string(self, data_list):
        return [str(data) for data in data_list]
    
    
    def run(self):
        try:
            with open(self.output_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Combine headers for both tables
                user_input_headers = [column.name for column in UserInputToolWearDB.__table__.columns]
                tool_wear_damage_headers = [column.name for column in ToolWearDamageDB.__table__.columns if column.name != 'user_data_id']
                combined_headers = user_input_headers + tool_wear_damage_headers
                writer.writerow(combined_headers)

                # Write combined data
                for tool_wear_damage_row in self.tool_wear_damage_rows:
                    user_input_data_list = [getattr(self.user_input_data, col) for col in user_input_headers]
                    tool_wear_damage_data_list = [getattr(tool_wear_damage_row, col) for col in tool_wear_damage_headers]
                    combined_data = user_input_data_list + tool_wear_damage_data_list
                    combined_data = self.format_datetime_fields(combined_data)
                    writer.writerow(combined_data)

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    # def run(self):
    #     try:
    #         with open(self.output_file_path, 'w', newline='') as csvfile:
    #             writer = csv.writer(csvfile)

    #             # Write UserInputToolWearDB headers and data
    #             user_input_headers = [column.name for column in UserInputToolWearDB.__table__.columns]
    #             writer.writerow(user_input_headers)
    #             user_input_data_list = [getattr(self.user_input_data, col) for col in user_input_headers]
    #             writer.writerow(self.format_datetime_fields(user_input_data_list))

    #             # Write a blank row for separation
    #             writer.writerow([])

    #             # Write ToolWearDamageDB headers and data
    #             tool_wear_damage_headers = [column.name for column in ToolWearDamageDB.__table__.columns]
    #             writer.writerow(tool_wear_damage_headers)
    #             for row in self.tool_wear_damage_rows:
    #                 row_data = [getattr(row, col) for col in tool_wear_damage_headers]
    #                 writer.writerow(self.format_datetime_fields(row_data))

    #         self.finished.emit()
    #     except Exception as e:
    #         self.error.emit(str(e))
