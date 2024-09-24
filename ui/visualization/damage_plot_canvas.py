from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax.set_title('Tool Wear Damage Over Time')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Damage')
        self.fig.autofmt_xdate()

    def update_plot(self, data):
        self.ax.clear()
        self.ax.set_title('Tool Wear Damage Over Time')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Damage')

        timestamps = [entry['created_at'] for entry in data]
        damage_area = [entry['damage_area'] for entry in data]
        damage_down = [entry['damage_down'] for entry in data]
        damage_up = [entry['damage_up'] for entry in data]

        self.ax.plot(timestamps, damage_area, label='Damage Area')
        self.ax.plot(timestamps, damage_down, label='Damage Down')
        self.ax.plot(timestamps, damage_up, label='Damage Up')

        self.ax.legend()
        self.ax.figure.autofmt_xdate()
        self.draw()
