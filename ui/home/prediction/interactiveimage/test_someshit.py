from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication

class ToastNotification(QWidget):
    def __init__(self, message, duration=3000, background_color='black', parent=None):
        super().__init__(parent)
        #self.setStyleSheet("font-size: 18px;")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.message = message
        self.duration = duration
        self.background_color = background_color
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.label = QLabel(self.message)
        self.label.setStyleSheet(f"""
            QLabel {{
                color: white;
                background-color: {self.background_color};
                padding: 10px;
                border-radius: 5px;
                font-size: 10px;
            }}
        """)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.adjustSize()
        
        # Position the toast at the top-right corner of the parent window if available
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.right() - self.width() - 20  # 20px margin from the right
            y = parent_geometry.top() + 20  # 20px margin from the top
            self.move(x, y)
        else:
            screen_geometry = QApplication.desktop().screenGeometry()
            x = screen_geometry.right() - self.width() - 20
            y = screen_geometry.top() + 20
            self.move(x, y)
        
        QTimer.singleShot(self.duration, self.close)

    def show_toast(self):
        self.show()
        QTimer.singleShot(self.duration, self.hide)

# def main():
#     import sys
#     app = QApplication(sys.argv)

#     main_layout = QVBoxLayout()

#     main_window = QWidget()
#     main_window.setGeometry(100, 100, 600, 400)

#     main_layout.addWidget(main_window)
    
#     toast = ToastNotification("This is a toast message!", 3000, 'blue', main_window)
#     toast2 = ToastNotification("This is a second toast message!", 3000, 'black')
#     toast.show_toast()
#     toast2.show_toast()

#     sys.exit(app.exec_())

# if __name__ == '__main__':
#     main()


# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow 
# from PyQt5 import QtWidgets, QtCore

# class MainWindowUi(QMainWindow):
#     def __init__(self):
#         QMainWindow.__init__(self)
#         self.scene = Scene(0, 0, 300, 300, self)
#         self.view = QtWidgets.QGraphicsView()
#         self.setCentralWidget(self.view)
#         self.view.setScene(self.scene)
#         self.scene.addItem(Square(0,0,50,50))

# class Scene(QtWidgets.QGraphicsScene):

#     def mousePressEvent(self, e):
#         print("Scene got mouse press event")
#         print("Event came to us accepted: %s"%(e.isAccepted(),))
#         QtWidgets.QGraphicsScene.mousePressEvent(self, e)

#     def mouseReleaseEvent(self, e):
#         print("Scene got mouse release event")
#         print("Event came to us accepted: %s"%(e.isAccepted(),))
#         QtWidgets.QGraphicsScene.mouseReleaseEvent(self, e)

#     def dragMoveEvent(self, e):
#         print('Scene got drag move event')

# class Square(QtWidgets.QGraphicsRectItem):
#     def __init__(self, *args):
#         QtWidgets.QGraphicsRectItem.__init__(self, *args)
#         self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
#         self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

#     def mousePressEvent(self, e):
#         print("Square got mouse press event")
#         print("Event came to us accepted: %s"%(e.isAccepted(),))
#         if e.button() == QtCore.Qt.LeftButton:
#             print("event has left button")
#             print(e.pos())
#             print(e.scenePos())
#         QtWidgets.QGraphicsRectItem.mousePressEvent(self, e)

#     def mouseReleaseEvent(self, e):
#         if e.button() == QtCore.Qt.LeftButton:
#             print("event pos when released")
#             print(e.scenePos())
#         print("Square got mouse release event")
#         print("Event came to us accepted: %s"%(e.isAccepted(),))
#         QtWidgets.QGraphicsRectItem.mouseReleaseEvent(self, e)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     win = MainWindowUi()
#     win.show()
#     sys.exit(app.exec_())







# # from PyQt5 import QtWidgets, QtGui, QtCore
# # import sys

# # class AnimatedRectItem(QtWidgets.QGraphicsRectItem):
# #     def __init__(self, rect, color):
# #         super().__init__(rect)
# #         self.setBrush(QtGui.QBrush(color))
# #         self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
# #         # Set the flag to inform the item to send geometry change notifications
# #         self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)

# #     def itemChange(self, change, value):
# #         if change == QtWidgets.QGraphicsItem.ItemPositionChange and self.scene():
# #             # value is the new position.
# #             new_pos = value
# #             scene_rect = self.scene().sceneRect()
# #             item_rect = self.boundingRect()
# #             # Adjust new position to keep the item inside the scene rect.
# #             new_x = min(scene_rect.right() - item_rect.width(), max(new_pos.x(), scene_rect.left()))
# #             new_y = min(scene_rect.bottom() - item_rect.height(), max(new_pos.y(), scene_rect.top()))
# #             new_pos = QtCore.QPointF(new_x, new_y)
# #             return new_pos
# #         return super().itemChange(change, value)


# # class SimpleGraphicsView(QtWidgets.QGraphicsView):
# #     def __init__(self):
# #         super().__init__()
# #         self.scene = QtWidgets.QGraphicsScene()
# #         self.setScene(self.scene)
        
# #         self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
# #         self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
# #         # Set the scene rectangle
# #         self.scene.setSceneRect(0, 0, 500, 300)
        
# #         # Create the blue rectangle
# #         self.blue_rect = AnimatedRectItem(QtCore.QRectF(0, 10, 100, 100), QtCore.Qt.blue)
# #         self.scene.addItem(self.blue_rect)
        
# #         # Create the red rectangle
# #         self.red_rect = AnimatedRectItem(QtCore.QRectF(300, 10, 100, 100), QtCore.Qt.red)
# #         self.scene.addItem(self.red_rect)
        
# #         # Create the button
# #         self.button = QtWidgets.QPushButton('Click Me')
# #         self.button.clicked.connect(self.move_rectangles)
# #         self.proxy = self.scene.addWidget(self.button)
# #         self.proxy.setPos(150, 150)

# #     def move_rectangles(self):
# #         blue_pos = self.blue_rect.pos()
# #         red_pos = self.red_rect.pos()
        
# #         if self.blue_rect.collidesWithItem(self.red_rect):
# #             # Handle collision animation
# #             self.animate_collision()
# #         else:
# #             # Animation to move blue rectangle to the right
# #             self.blue_animation = QtCore.QPropertyAnimation(self.blue_rect, b'pos', None)
# #             self.blue_animation.setDuration(1000)
# #             self.blue_animation.setStartValue(blue_pos)
# #             self.blue_animation.setEndValue(QtCore.QPointF(blue_pos.x() + 150, blue_pos.y()))

# #             # Animation to move red rectangle to the left
# #             self.red_animation = QtCore.QPropertyAnimation(self.red_rect, b'pos', None)
# #             self.red_animation.setDuration(1000)
# #             self.red_animation.setStartValue(red_pos)
# #             self.red_animation.setEndValue(QtCore.QPointF(red_pos.x() - 150, red_pos.y()))

# #             # Start animations
# #             self.blue_animation.start()
# #             self.red_animation.start()

# #         def animate_collision(self):
# #             # Animation to move blue rectangle to the left
# #             self.blue_collision_animation = QtCore.QPropertyAnimation(self.blue_rect, b'pos')
# #             self.blue_collision_animation.setDuration(500)
# #             self.blue_collision_animation.setStartValue(self.blue_rect.pos())
# #             self.blue_collision_animation.setEndValue(QtCore.QPointF(self.blue_rect.pos().x() - 50, self.blue_rect.pos().y()))
# #             self.blue_collision_animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)

# #             # Animation to move red rectangle to the right
# #             self.red_collision_animation = QtCore.QPropertyAnimation(self.red_rect, b'pos')
# #             self.red_collision_animation.setDuration(500)
# #             self.red_collision_animation.setStartValue(self.red_rect.pos())
# #             self.red_collision_animation.setEndValue(QtCore.QPointF(self.red_rect.pos().x() + 50, self.red_rect.pos().y()))
# #             self.red_collision_animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)

# #             # Start animations
# #             self.blue_collision_animation.start()
# #             self.red_collision_animation.start()


# #     def merge_rectangles(self):
# #         # Remove the old rectangles
# #         self.scene.removeItem(self.blue_rect)
# #         self.scene.removeItem(self.red_rect)
        
# #         # Create a new combined rectangle
# #         combined_rect = QtWidgets.QGraphicsRectItem(QtCore.QRectF(150, 0, 100, 100))
# #         combined_color = QtGui.QColor(255, 0, 255)  # Combined color (magenta)
# #         combined_rect.setBrush(QtGui.QBrush(combined_color))
# #         self.scene.addItem(combined_rect)

# # if __name__ == '__main__':
# #     app = QtWidgets.QApplication(sys.argv)
# #     view = SimpleGraphicsView()
# #     view.setWindowTitle('Simple Graphics View')
# #     view.setGeometry(100, 100, 500, 300)
# #     view.show()
# #     sys.exit(app.exec_())
