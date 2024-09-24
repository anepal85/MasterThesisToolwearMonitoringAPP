from PyQt5 import QtWidgets, QtGui

class VBDisplayer(QtWidgets.QWidget):
    def __init__(self, threshold: float, label_name:str, parent=None):
        super(VBDisplayer, self).__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # Store the threshold value
        self.threshold = threshold
        self.label_name = label_name 
        # Create the layout for the widget
        layout = QtWidgets.QHBoxLayout(self)

        # Create a QLabel for displaying the prefix and value
        self.label = QtWidgets.QLabel(self.label_name, self)
        self.label.setFont(QtGui.QFont("Arial", 18))

        # Create a QLCDNumber widget for displaying numerical values
        self.display = QtWidgets.QLCDNumber(self)
        self.display.setDigitCount(5)  # Set the number of digits to be displayed
        #self.display.setStyleSheet("font-size: 18pt;")

        # Create a QLabel for displaying the prefix and value
        mm = QtWidgets.QLabel("mm", self)
        mm.setFont(QtGui.QFont("Arial", 16))

        layout.addWidget(self.label, 0)
        layout.addWidget(self.display, 1)
        layout.addWidget(mm, 0)
        # spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # layout.addItem(spacerItem)
        
        self.setMaximumHeight(70)  
        
    def update_value(self, value:float):
        # Round the value to two decimal places
        rounded_value = round(value, 2)
        self.display.display(rounded_value)

        # Update display color based on the new value
        self.update_display_color(rounded_value)

    def update_display_color(self, value:float):
        # Set display color based on whether the value exceeds the threshold
        if value > self.threshold:
            self.display.setStyleSheet("color: red;")
        else:
            self.display.setStyleSheet("color: green;")


class VBDisplayerPair(QtWidgets.QWidget):
    def __init__(self, threshold: float, parent=None):
        super(VBDisplayerPair, self).__init__(parent)

        # Create the layout for the widget
        layout = QtWidgets.QHBoxLayout(self)

        # Create instances of VBDisplayer
        self.vb_displayer_below = VBDisplayer(threshold, "VB\u2193 = ",parent=self)
        self.vb_displayer_up = VBDisplayer(threshold, "VB\u2191 = ", parent=self)

        # Add the VBDisplayers to the layout
        layout.addWidget(self.vb_displayer_below)
        layout.addWidget(self.vb_displayer_up)
        
        self.setMaximumHeight(90)  

    def update_values(self, value_below: float, value_up: float):
        # Update the values of both VBDisplayers
        self.vb_displayer_below.update_value(value_below)
        self.vb_displayer_up.update_value(value_up)




from PyQt5 import QtWidgets, QtGui

class VBDisplayer2(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(VBDisplayer2, self).__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Create the layout for the widget
        layout = QtWidgets.QHBoxLayout(self)

        # Create a QLabel for displaying the up arrow
        self.up_arrow_label = QtWidgets.QLabel("VB \u2191 = ", self)
        self.up_arrow_label.setFont(QtGui.QFont("Arial", 18))

        # Create a QLCDNumber widget for displaying the VB up value
        self.display_up = QtWidgets.QLCDNumber(self)
        self.display_up.setDigitCount(5)  # Set the number of digits to be displayed

        # Create a QLabel for displaying the down arrow
        self.down_arrow_label = QtWidgets.QLabel("VB \u2193 = ", self)
        self.down_arrow_label.setFont(QtGui.QFont("Arial", 18))

        # Create a QLCDNumber widget for displaying the VB down value
        self.display_down = QtWidgets.QLCDNumber(self)
        self.display_down.setDigitCount(6)  # Set the number of digits to be displayed

        layout.addWidget(self.up_arrow_label, 0)
        layout.addWidget(self.display_up, 1)
        layout.addWidget(self.down_arrow_label, 0)
        layout.addWidget(self.display_down, 1)

        self.setMaximumHeight(70)  
        
    def update_values(self, value_up: float, value_down: float, vb_max_threshold:float):
        # Round the values to two decimal places
        rounded_value_up = round(value_up, 5)
        rounded_value_down = round(value_down, 5)
        # Update display color based on the new values
        self.update_display_color(rounded_value_up, rounded_value_down, vb_max_threshold)
                
        self.display_up.display(rounded_value_up)
        self.display_down.display(rounded_value_down)


    def update_display_color(self, value_up: float, value_down: float, vb_max_threshold):
        # Set display color based on whether the values exceed the threshold
        if value_up > vb_max_threshold:
            self.display_up.setStyleSheet("color: red;")
        else:
            self.display_up.setStyleSheet("color: green;")
        
        if value_down > vb_max_threshold:
            self.display_down.setStyleSheet("color: red;")
        else:
            self.display_down.setStyleSheet("color: green;")
