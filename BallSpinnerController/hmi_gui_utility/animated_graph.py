import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
from queue import Queue

class RealTimeGraph:
    def __init__(self, master, data_q, update_speed=100, xl_config=None):
        self.master = master
        self.queue = data_q
        #master.title("Real-time XYZ Graph")

        dpi = 50  # Adjust as needed
        figsize = (150 / dpi, 80 / dpi)  # (width_inches, height_inches)

        self.fig, self.ax = plt.subplots(figsize=figsize, dpi=dpi)
        if xl_config != None:
            pass 
            #set the y lim to be that of the XL Range Parameter
        self.ax.set_ylim(-2,2)
        self.x_data = []
        self.y_data = []
        self.z_data = []
        self.time_data = []

        self.ax.set_xlabel("Time", fontsize=5)
        self.ax.set_ylabel("Value", fontsize=5)
        self.ax.legend(loc="upper left", fontsize=4)  # Smaller legend
        self.ax.set_xticks([])

        # Create three line objects for x, y, z with circular markers
        self.line_x, = self.ax.plot([], [], label='X', color='red', marker='o', linestyle='-')
        self.line_y, = self.ax.plot([], [], label='Y', color='green', marker='o', linestyle='-')
        self.line_z, = self.ax.plot([], [], label='Z', color='blue', marker='o', linestyle='-')

        self.ax.legend(loc="upper left")

        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        #self.canvas_widget.pack()

        self.ani = FuncAnimation(self.fig, self.update_graph, interval=update_speed, blit=False)

    def update_graph(self, i):
        # Pull all items from the queue
        t = 0
        while not self.queue.empty():
            #print(f"Metamotion queue address {self.queue}")
            data = self.queue.get()
            print(f"data: {data}")
            t = data['timestamp']
            self.time_data.append(t)
            self.x_data.append(data['x'])
            self.y_data.append(data['y'])
            self.z_data.append(data['z'])
            print(f"Data received: {data}")
        # Keep only the last 5 seconds of data
        current_time = t
        while self.time_data and self.time_data[0] < current_time - 5:
            self.time_data.pop(0)
            self.x_data.pop(0)
            self.y_data.pop(0)
            self.z_data.pop(0)

        # Update plot lines
        self.line_x.set_data(self.time_data, self.x_data)
        self.line_y.set_data(self.time_data, self.y_data)
        self.line_z.set_data(self.time_data, self.z_data)

        self.ax.set_xlim(current_time - 5, current_time)
        self.ax.relim()
        self.ax.autoscale_view(scalex=False)

        return self.line_x, self.line_y, self.line_z


# Simulated data feed (can be run in another thread)
def simulate_data_feed(data_q):
    import threading

    def feed():
        while True:
            time.sleep(1)  # simulate 20Hz sensor
            data_q.put({
                'timestamp': time.time(),
                'x': random.uniform(-1, 1),
                'y': random.uniform(-1, 1),
                'z': random.uniform(-1, 1),
            })
            #print (f"Data added to queue: {data_q.queue[-1]}")

    threading.Thread(target=feed, daemon=True).start()


# Main
if __name__ == "__main__":
    root = tk.Tk()
    data_queue = Queue()
    simulate_data_feed(data_queue)
    rt_graph = RealTimeGraph(root, data_queue)
    root.mainloop()
