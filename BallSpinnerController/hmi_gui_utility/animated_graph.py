import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
import math
from queue import Queue

class RealTimeGraph:
    def __init__(self, master, data_q, update_speed=100, xl_config=None, ymin=-2, ymax=2, changey=True):
        self.master = master
        self.queue = data_q
        self.m = 0
        self.changey = changey
        self.fullscreen = False
        #master.title("Real-time XYZ Graph")

        self.dpi = 50  # Adjust as needed
        figsize = (150 / self.dpi, 80 / self.dpi)  # (width_inches, height_inches)

        self.fig, self.ax = plt.subplots(figsize=figsize, dpi=self.dpi)
        if xl_config != None:
            pass 
            #set the y lim to be that of the XL Range Parameter
        self.ax.set_ylim(ymin,ymax)
        self.x_data = []
        self.y_data = []
        self.z_data = []
        self.time_data = []

        self.ax.set_xlabel("Time", fontsize=5)
        self.ax.set_ylabel("Value", fontsize=5)
        self.ax.legend(loc="upper left", fontsize=4)  # Smaller legend
        #self.ax.set_xticks([])

        # Create three line objects for x, y, z with circular markers
        self.line_x, = self.ax.plot([], [], label='X', color='red', marker='o', linestyle='-')
        self.line_y, = self.ax.plot([], [], label='Y', color='green', marker='o', linestyle='-')
        self.line_z, = self.ax.plot([], [], label='Z', color='blue', marker='o', linestyle='-')

        self.ax.legend(loc="upper left")

        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        
        #ensure geometry info is available
        self.canvas_widget.update_idletasks()

        #self.canvas_widget.pack()

        self.ani = FuncAnimation(self.fig, self.update_graph, interval=update_speed, blit=False)

    def update_graph(self, i):
        # Pull all items from the queue
        t = 0
        while not self.queue.empty():
            data = self.queue.get()
            
            t = data['timestamp']
            if not math.isinf(data['x']) and not math.isinf(data['y']) and not math.isinf(data['z']):
                self.time_data.append(t)
                self.x_data.append(data['x'])
                self.y_data.append(data['y'])
                self.z_data.append(data['z'])
                self.m = max(abs(data['x']), abs(data['y']), abs(data['z']))

            #print(f"Data received: {data}")

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
        if self.changey:
            self.ax.set_ylim(-self.m - self.m/5, self.m + self.m/5)
        self.ax.relim()
        self.ax.autoscale_view(scalex=False)

        return self.line_x, self.line_y, self.line_z

    # Toggle fullscreen mode for the graph display
    def toggle_fullscreen(self):
        print(f"Previous Graph Size: ({self.canvas_widget.winfo_width()}, {self.canvas_widget.winfo_height()})")

        if self.fullscreen:
            self.canvas_widget.config(width=150,height = 80)
        else:
           self.canvas_widget.config(width=600,height = 300)
        self.fullscreen = not self.fullscreen
        self.canvas_widget.update_idletasks()
    def increase_font_size(self, increment=2):
        # Update axis label font sizes
        current_xlabel_size = self.ax.xaxis.label.get_size()
        current_ylabel_size = self.ax.yaxis.label.get_size()

        self.ax.set_xlabel(self.ax.get_xlabel(), fontsize=current_xlabel_size + increment)
        self.ax.set_ylabel(self.ax.get_ylabel(), fontsize=current_ylabel_size + increment)

        # Update tick font sizes
        for tick in self.ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(tick.label.get_size() + increment)
        for tick in self.ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(tick.label.get_size() + increment)

        # Update legend text font sizes
        legend = self.ax.get_legend()
        if legend:
            for text in legend.get_texts():
                text.set_fontsize(text.get_fontsize() + increment)

        self.canvas.draw_idle()

# Simulated data feed (can be run in another thread)
def simulate_data_feed(data_q):
    import threading

    def feed():
        start_time = time.time()
        while True:
            t = time.time() - start_time  # elapsed time
            time.sleep(.2)  # simulate 20Hz sensor (50 ms interval)

            data_q.put({
                'timestamp': time.time(),
                'x': math.sin(t) + random.random(),
                'y': math.cos(t) + random.random(),
                'z': math.sin(t) * math.cos(t) + random.random(),  # combined wave for fun
            })

    threading.Thread(target=feed, daemon=True).start()


# Main
if __name__ == "__main__":
    root = tk.Tk()
    data_queue = Queue()
    simulate_data_feed(data_queue)
    rt_graph = RealTimeGraph(root, data_queue)
    root.mainloop()
