import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


vol_size = 128  # Adjust resolution

# Define ellipsoids (x, y, z, rx, ry, rz, intensity)
ellipsoids = [
    (0, 0, 0, 40, 60, 50, 1),     # Large central ellipsoid
    (20, -20, -10, 15, 25, 30, 0.8), # Small ellipsoid in top left
    (-25, 10, 10, 20, 20, 20, 0.6),  # Medium ellipsoid bottom right
    (0, 0, 30, 10, 15, 10, 0.9)     # Small sphere in center top
]

def create_3d_ellipsoid(size, ellipsoids):
    phantom = np.zeros((size, size, size), dtype=np.float32)
    # Create coordinate grid
    x, y, z = np.indices((size, size, size)) - size // 2

    # Iterate over each ellipsoid
    for cx, cy, cz, rx, ry, rz, intensity in ellipsoids:
        mask = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2 <= 1
        phantom[mask] += intensity  # Add ellipsoid intensity

    return phantom



class ImageViewerApp:
    def __init__(self, root, data):
        self.root = root
        self.data = data
        self.current_slice = 80  # Start with the first slice

        # Create Matplotlib figure and axis
        self.fig, self.ax = plt.subplots()
        self.im = self.ax.imshow(self.data[self.current_slice], cmap='gray')

        # Embed Matplotlib figure into Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

        # Create scrollbar (Scale widget for selecting slices)
        self.slice_selector = ttk.Scale(
            root, from_=0, to=self.data.shape[0] - 1, 
            orient="horizontal", command=self.update_slice
        )
        self.slice_selector.pack(fill='x', padx=10, pady=5)
        self.slice_selector.set(self.current_slice)

    def update_slice(self, value):
        self.current_slice = int(float(value))  # Convert from Scale's float value
        self.im.set_array(self.data[self.current_slice])
        self.canvas.draw()

if __name__ == "__main__":
    # Generate the 3D phantom
    data = create_3d_ellipsoid(vol_size, ellipsoids)
    # Initialize the Tkinter application
    root = tk.Tk()
    root.title("3D NumPy Viewer")

    app = ImageViewerApp(root, data)

    root.mainloop()
