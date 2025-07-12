import tkinter as tk
from tkinter import ttk
import heapq
import time

class DijkstraComparisonVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Dijkstra's Algorithm Comparison")

        self.canvas_width = 600
        self.canvas_height = 400

        # Graph: adjacency list with weights
        self.graph = {
            'A': [('B', 2), ('C', 5)],
            'B': [('A', 2), ('C', 6), ('D', 1)],
            'C': [('A', 5), ('B', 6), ('E', 3)],
            'D': [('B', 1), ('E', 1), ('F', 4)],
            'E': [('C', 3), ('D', 1), ('G', 2)],
            'F': [('D', 4), ('G', 1)],
            'G': [('E', 2), ('F', 1)],
        }

        # Positions of nodes on canvas
        self.positions = {
            'A': (100, 100),
            'B': (200, 80),
            'C': (250, 150),
            'D': (300, 80),
            'E': (350, 170),
            'F': (400, 80),
            'G': (450, 150),
        }

        self.start_node = 'A'
        self.end_node = 'G'

        # Variables for both algorithms
        self.reset_state()

        # UI setup
        self.frame = ttk.Frame(root, padding=10)
        self.frame.grid(row=0, column=0, sticky="nw")

        ttk.Label(self.frame, text="Dijkstra's Algorithm Comparison", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=5)

        ttk.Label(self.frame, text="Choose Algorithm:", font=("Arial", 12)).grid(row=1, column=0, sticky="w")
        self.alg_var = tk.StringVar(value="heap")
        ttk.Radiobutton(self.frame, text="Min-Heap", variable=self.alg_var, value="heap").grid(row=2, column=0, sticky="w")
        ttk.Radiobutton(self.frame, text="Linear Search", variable=self.alg_var, value="linear").grid(row=3, column=0, sticky="w")

        self.start_button = ttk.Button(self.frame, text="Start Algorithm", command=self.start_algorithm)
        self.start_button.grid(row=4, column=0, pady=10)

        self.step_button = ttk.Button(self.frame, text="Next Step", command=self.next_step, state="disabled")
        self.step_button.grid(row=5, column=0, pady=5)

        self.reset_button = ttk.Button(self.frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=6, column=0, pady=5)

        self.status_label = ttk.Label(self.frame, text="Select algorithm and click Start.", font=("Arial", 12), wraplength=280)
        self.status_label.grid(row=7, column=0, pady=10)

        self.time_label = ttk.Label(self.frame, text="Elapsed time: 0.0 ms", font=("Arial", 12))
        self.time_label.grid(row=8, column=0, pady=5)

        self.winner_label = ttk.Label(self.frame, text="", font=("Arial", 14, "bold"), foreground="green")
        self.winner_label.grid(row=9, column=0, pady=10)

        # Canvas for graph visualization
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.grid(row=0, column=1, padx=10, pady=10)

        # Canvas for priority queue or linear search visualization
        self.queue_canvas = tk.Canvas(root, width=200, height=self.canvas_height, bg="#f0f0f0")
        self.queue_canvas.grid(row=0, column=2, padx=10, pady=10)

        self.draw_map()

    def reset_state(self):
        # Common state
        self.distances = {node: float('inf') for node in self.graph}
        self.distances[self.start_node] = 0
        self.prev = {node: None for node in self.graph}
        self.visited = set()

        # Heap-based
        self.pq = []

        # Linear search
        self.unvisited = set(self.graph.keys())

        # Timing
        self.start_time = None
        self.elapsed_time = 0.0

        # Step control
        self.algorithm_running = False
        self.finished = False

        # Current node being processed
        self.current_node = None

    def reset(self):
        self.reset_state()
        self.draw_map()
        self.queue_canvas.delete("all")
        self.status_label.config(text="Select algorithm and click Start.")
        self.time_label.config(text="Elapsed time: 0.0 ms")
        self.winner_label.config(text="")
        self.start_button.config(state="normal")
        self.step_button.config(state="disabled")

    def draw_map(self):
        self.canvas.delete("all")
        # Draw edges
        for node, neighbors in self.graph.items():
            x1, y1 = self.positions[node]
            for nbr, w in neighbors:
                x2, y2 = self.positions[nbr]
                self.canvas.create_line(x1, y1, x2, y2, fill="gray", width=2)
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                self.canvas.create_text(mid_x, mid_y - 10, text=str(w), font=("Arial", 10, "italic"))

        # Draw nodes
        radius = 20
        for node, (x, y) in self.positions.items():
            fill_color = "lightgreen" if node == self.start_node else "red" if node == self.end_node else "lightblue"
            outline_color = "black"
            if node in self.visited:
                fill_color = "lightgray"
            if node == self.current_node:
                fill_color = "yellow"
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill_color, outline=outline_color, width=2)
            self.canvas.create_text(x, y, text=node, font=("Arial", 14, "bold"))

            dist_text = "∞" if self.distances[node] == float('inf') else str(self.distances[node])
            self.canvas.create_text(x, y + radius + 15, text=f"Dist: {dist_text}", font=("Arial", 10))

        # If finished, highlight shortest path
        if self.finished:
            self.highlight_path()

    def update_queue_display(self):
        self.queue_canvas.delete("all")
        algo = self.alg_var.get()
        self.queue_canvas.create_text(100, 20, text="Queue State", font=("Arial", 14, "bold"))

        if algo == "heap":
            self.queue_canvas.create_text(100, 50, text="Min-Heap (priority queue)", font=("Arial", 12))
            start_y = 80
            gap = 30
            for i, (dist, node) in enumerate(self.pq):
                text = f"{node}: {dist}"
                self.queue_canvas.create_rectangle(20, start_y + i*gap - 15, 180, start_y + i*gap + 15, fill="lightyellow", outline="black")
                self.queue_canvas.create_text(100, start_y + i*gap, text=text, font=("Arial", 12))
        else:
            self.queue_canvas.create_text(100, 50, text="Unvisited nodes", font=("Arial", 12))
            start_y = 80
            gap = 25
            for i, node in enumerate(sorted(self.unvisited)):
                dist = self.distances[node]
                dist_text = "∞" if dist == float('inf') else str(dist)
                text = f"{node}: {dist_text}"
                self.queue_canvas.create_rectangle(20, start_y + i*gap - 12, 180, start_y + i*gap + 12, fill="lightyellow", outline="black")
                self.queue_canvas.create_text(100, start_y + i*gap, text=text, font=("Arial", 12))

    def start_algorithm(self):
        if self.algorithm_running:
            return

        self.reset_state()
        self.algorithm_running = True
        self.finished = False
        self.current_node = None

        algo = self.alg_var.get()

        if algo == "heap":
            self.pq = []
            heapq.heappush(self.pq, (0, self.start_node))
            self.status_label.config(text="Using Min-Heap priority queue. Click 'Next Step' to proceed.")
        else:
            self.unvisited = set(self.graph.keys())
            self.status_label.config(text="Using Linear Search. Click 'Next Step' to proceed.")

        self.start_time = time.perf_counter()
        self.step_button.config(state="normal")
        self.start_button.config(state="disabled")
        self.time_label.config(text="Elapsed time: 0.0 ms")
        self.winner_label.config(text="")
        self.draw_map()
        self.update_queue_display()

    def next_step(self):
        if not self.algorithm_running or self.finished:
            return

        algo = self.alg_var.get()

        if algo == "heap":
            self.next_step_heap()
        else:
            self.next_step_linear()

        self.draw_map()
        self.update_queue_display()

    def next_step_heap(self):
        if not self.pq:
            self.finish_algorithm()
            return

        dist, current = heapq.heappop(self.pq)
        while current in self.visited:
            if not self.pq:
                self.finish_algorithm()
                return
            dist, current = heapq.heappop(self.pq)

        self.current_node = current
        self.visited.add(current)
        self.status_label.config(text=f"Visiting node {current} with dist {dist}")

        if current == self.end_node:
            self.finish_algorithm()
            return

        for (nbr, w) in self.graph[current]:
            if nbr in self.visited:
                continue
            new_dist = dist + w
            if new_dist < self.distances[nbr]:
                self.distances[nbr] = new_dist
                self.prev[nbr] = current
                heapq.heappush(self.pq, (new_dist, nbr))

    def next_step_linear(self):
        # Pick unvisited node with smallest distance
        min_dist = float('inf')
        current = None
        for node in self.unvisited:
            if self.distances[node] < min_dist:
                min_dist = self.distances[node]
                current = node

        if current is None or min_dist == float('inf'):
            self.finish_algorithm()
            return

        self.current_node = current
        self.visited.add(current)
        self.unvisited.remove(current)
        self.status_label.config(text=f"Visiting node {current} with dist {min_dist}")

        if current == self.end_node:
            self.finish_algorithm()
            return

        for (nbr, w) in self.graph[current]:
            if nbr in self.visited:
                continue
            new_dist = self.distances[current] + w
            if new_dist < self.distances[nbr]:
                self.distances[nbr] = new_dist
                self.prev[nbr] = current

    def finish_algorithm(self):
        self.finished = True
        self.algorithm_running = False
        self.current_node = None
        end_time = time.perf_counter()
        self.elapsed_time = (end_time - self.start_time) * 1000  # ms
        self.status_label.config(text=f"Algorithm finished in {self.elapsed_time:.2f} ms.")

        self.draw_map()
        self.highlight_path()
        self.update_queue_display()
        self.step_button.config(state="disabled")
        self.start_button.config(state="normal")

        # Show winner label if possible (compare times)
        # For demo, just show current algo time; ideally you run both and compare
        algo_name = "Min-Heap" if self.alg_var.get() == "heap" else "Linear Search"
        self.winner_label.config(text=f"{algo_name} finished in {self.elapsed_time:.2f} ms")

    def highlight_path(self):
        self.canvas.delete("path")
        path_nodes = []
        current = self.end_node
        while current:
            path_nodes.append(current)
            current = self.prev[current]
        path_nodes.reverse()

        radius = 20
        for i in range(len(path_nodes) - 1):
            x1, y1 = self.positions[path_nodes[i]]
            x2, y2 = self.positions[path_nodes[i + 1]]
            self.canvas.create_line(x1, y1, x2, y2, fill="orange", width=4, tags="path")

        for node in path_nodes:
            x, y = self.positions[node]
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="orange", outline="black", width=2, tags="path")
            self.canvas.create_text(x, y, text=node, font=("Arial", 14, "bold"), tags="path")


if __name__ == "__main__":
    root = tk.Tk()
    app = DijkstraComparisonVisualizer(root)
    root.mainloop()
    

