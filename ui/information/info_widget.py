import sys
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea
)

class BulletPointsWidget(QWidget):
    def __init__(self, points, margin_left=20):
        super().__init__()

        layout = QVBoxLayout()
        for point in points:
            bullet_label = QLabel(f"• {point}")
            bullet_label.setStyleSheet(f"font-size: 16px; margin-left: {margin_left}px;")
            layout.addWidget(bullet_label)

        self.setLayout(layout)


class HeaderWithOverviewWidget(QWidget):
    def __init__(self, header, overview=None, bullet_points=None, nested_widgets=None, margin_left=0):
        super().__init__()

        layout = QVBoxLayout()

        # Header
        header_label = QLabel(header)
        header_label.setStyleSheet(f"font-size: 20px; font-weight: bold; margin-left: {margin_left}px;")
        layout.addWidget(header_label)

        # Overview
        if overview:
            overview_label = QLabel(overview)
            overview_label.setStyleSheet(f"font-size: 16px; margin-top: 10px; margin-bottom: 10px; margin-left: {margin_left}px;")
            layout.addWidget(overview_label)

        # Bullet Points
        if bullet_points:
            bullet_widget = BulletPointsWidget(bullet_points, margin_left=margin_left + 20)
            layout.addWidget(bullet_widget)

        # Nested Widgets
        if nested_widgets:
            for widget in nested_widgets:
                widget.setContentsMargins(margin_left + 20, 0, 0, 0)
                layout.addWidget(widget)

        self.setLayout(layout)


class SoftwareInfoWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout
        main_layout = QVBoxLayout()
        
        # Scroll area setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Overview Section
        overview_text = "This section provides instructions on how to use Toolwear Cockpit. It contains three main pages:"
        overview_bullet_points = [
            "Live View - Toolwear live visualization and measurement",
            "Configuration Input - User-defined configuration data related to tools and machine specifications",
            "Annotation - For continuous improvement of the ML model."
        ]
        overview_widget = HeaderWithOverviewWidget("Overview", overview_text, bullet_points=overview_bullet_points)
        content_layout.addWidget(overview_widget)

        # Home Page Section
        home_overview = "Toolwear Monitoring and Measurement"
        home_bullet_points = [
            "Live View - Real-time visualization of connected microscope",
            "Predicted Toolwear - Visualization of predicted results with a vertically moveable red horizontal line and calculated VB in both directions"
        ]
        home_widget = HeaderWithOverviewWidget("Live View", home_overview, bullet_points=home_bullet_points)

        # Live View Section (Sub-section of Home Page)
        live_view_widget = HeaderWithOverviewWidget(
            "Live Microscope View",
            bullet_points=[
                "Refer to the Configuration Input section before snapping or uploading images!",
                "The microscope can be turned on and off via the 'ON' button. After the camera is successfully turned on, the button changes to 'OFF'.",
                "Available ML models can be selected via the dropdown from the 'Select Model' section.",
                "Apply selected changes by clicking the 'Change Model' button.",
                "The 'Snap' button captures the current frame of the camera.",
                "'Upload' allows uploading the captured image.",
                "For local upload tasks, please turn off the live camera."
            ],
            margin_left=20  # Adding left margin to distinguish it as a sub-section
        )

        # Predicted Toolwear View (Sub-section of Home Page)
        predicted_display_view_widget = HeaderWithOverviewWidget(
            "Predicted Toolwear View",
            bullet_points=[
                "The closed green contour line describes toolwear detected by the ML model.",
                "The red horizontal line is movable in the Y-direction.",
                "The red line is calculated to differentiate between two types of toolwear damage.",
                "VB \u2193 is the maximum height of the toolwear in mm from the red line to the green contour downwards.",
                "VB \u2191 is the maximum height of toolwear in mm from the red line to the green contour upwards.",
                "Click 'Needs Correction' if the prediction is incorrect and needs adjustment.",
                "The 'Save' button stores the current snapped frame and its measurement.",
                "Click 'Process Complete' to finish the current process and start with a new configuration and measurement."
            ],
            margin_left=20  # Adding left margin to distinguish it as a sub-section
        )
        
        # Add sub-sections to the Home Page
        home_widget.layout().addWidget(live_view_widget)
        home_widget.layout().addWidget(predicted_display_view_widget)

        content_layout.addWidget(home_widget)

        # Config Input Section
        config_overview = "This section allows users to define and manage various parameters related to tool wear monitoring and system configurations. It is divided into two main sections to ensure effective setup and management of configurations."

        config_bullet_points = [
            "Tool Configuration - Allows users to define and manage tool-specific parameters.",
            "Export Toolwear with Configuration - Provides options to export and save configurations with its respective measurement from the database"
        ]

        config_input_widget = HeaderWithOverviewWidget("Config Input Page", config_overview, bullet_points=config_bullet_points)

        tool_config_widget = HeaderWithOverviewWidget(
            "Tool Configuration",
            bullet_points=[
                "At least one ID has to be selected to perform toolwear measurement in Live View.",
                "Select Configuration ID - Choose or create a configuration ID to save or retrieve specific tool settings.",
                "'Neue Erstellen' blanks all fields for user to provide input.",
                "When ID is selected any field could be changed but in unchanged case it remains same.",
                "'Löschen' - Can delete configurations by ID if currently logged user has admin rights.",
                "Ansehen - User can visualize all configurations from the database as a new popup table.",
                "Tool Parameters - Input essential tool information like tool type, size, and specifications.",
                "Filedialog - Defines a specific folder for storing images and respective toolwear predictions, created as SelectedFolder\images & SelectedFolder\masks",
                "'Abgabe' - Saves the current settings for consistent and repeatable tool wear monitoring."
            ],
            margin_left=20  # Adding left margin to distinguish it as a sub-section
        )

        export_config_widget = HeaderWithOverviewWidget(
            "Export Configuration",
            bullet_points=[
                "Select ID is compulsory for export.",
                "Export Measurements & Configurations - Export all the measurements stored in the database by current tool configurations to a .CSV file."
            ],
            margin_left=20  # Adding left margin to distinguish it as a sub-section
        )

        # Add features to Config Input section
        config_input_widget.layout().addWidget(tool_config_widget)
        config_input_widget.layout().addWidget(export_config_widget)

        content_layout.addWidget(config_input_widget)

        # Annotation Page Section
        annotation_overview = "This section guides users through the process of managing and annotating datasets using Label Studio. Follow these steps to ensure an effective annotation workflow for machine learning."

        annotation_bullet_points = [
            "Start Label Studio - Select the root folder where your images and corresponding masks are located. Ensure that the number of images and masks are the same.",
            "Create Account in Label Studio - Sign up for a Label Studio account if you haven't already.",
            "Copy API Key - Once logged in, navigate to your Label Studio settings, copy the API key, and paste it into the provided input field within this widget.",
            "Create a New Project - Assign a unique name to your project and click 'Create Project' to initialize the project in Label Studio.",
            "Select Existing Project - If a project already exists, select it from the dropdown menu to continue working on it.",
            "Upload Images and Masks - Click the 'Upload Images and Masks' button to upload your dataset into the selected project. This process may take some time, depending on the size of your dataset.",
            "Annotate in Label Studio - Open the created project from the Label Studio interface. Here, you can view, edit, create, or delete annotations as needed.",
            "Submit Annotations - After making changes, be sure to submit your updates within the Label Studio interface to save the annotations.",
            "Export Annotations - Once all annotations are complete, export the annotated data in .JSON format for further use in your machine learning projects."
        ]

        annotation_widget = HeaderWithOverviewWidget("Annotation Page", annotation_overview, bullet_points=annotation_bullet_points)
        content_layout.addWidget(annotation_widget)

        # Set content layout and scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = SoftwareInfoWidget()
    win.show()
    sys.exit(app.exec_())

