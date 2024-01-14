import random
import time
import os
import sys
import math

class Pixel:
    def __init__(self, path=None, reset_to_black=False):
        self.name = "Pixel"
        self.width, self.height = 192, 108
        self.update_interval = 0.0001  # seconds
        self.file_path = path
        self.temp_file_path = self.file_path + ".tmp"
        self.bees = []
        if reset_to_black or not os.path.exists(self.file_path):
            self.pixel_matrix = [[(0, 0, 0) for _ in range(self.width)] for _ in range(self.height)]  # Initialize with black background
        else:
            self.pixel_matrix = self.read_matrix_from_file()

        self.flower_patterns = [
            [(0, -1), (1, -1), (-1, -1), (0, -2)],  
            [(0, -1), (1, -1), (-1, -1), (1, 0), (-1, 0)],  
            [(0, -1), (1, -1), (-1, -1), (0, -2), (1, 0), (-1, 0), (2, 0), (-2, 0)]  
        ]
        self.stem = [(0, 1), (0, 2)]

        self.tree_patterns = [
            [(0, -1), (0, -2), (0, -3)],
            [(0, -1), (-1, -2), (0, -2), (1, -2), (0, -3)],
            [(0, -1), (-1, -1), (1, -1), (-1, -2), (1, -2), (0, -3)]
        ]

    def read_matrix_from_file(self):
        matrix = []
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    row = []
                    pixels = line.strip().split(' ')
                    for pixel in pixels:
                        r, g, b = map(int, pixel.split(','))
                        row.append((r, g, b))
                    matrix.append(row)
            return matrix
        except IOError as e:
            print(f"Error reading from file {self.file_path}: {e}")
            sys.exit(1)

    def new_flower(self):
        flower_color = (random.randint(100, 255), random.randint(0, 100), random.randint(0, 100))
        center_color = (255, 255, random.randint(0, 100))  # Yellowish center

        flower_x = random.randint(0, self.width - 1)
        flower_y = random.randint(0, self.height - 3)  # Ensure space for petals

        num_petals = random.randint(5, 8)
        for _ in range(num_petals):
            angle = random.uniform(0, 2 * math.pi)
            dx = int(math.cos(angle) * 2)
            dy = int(math.sin(angle) * 2)
            x, y = flower_x + dx, flower_y + dy
            if 0 <= x < self.width and 0 <= y < self.height:
                self.pixel_matrix[y][x] = flower_color

        # Draw the flower center
        self.pixel_matrix[flower_y][flower_x] = center_color

    def new_tree(self):
        tree_color = (random.randint(0, 100), random.randint(60, 100), random.randint(0, 40))
        trunk_color = (random.randint(50, 100), random.randint(30, 70), random.randint(0, 10))

        tree_x = random.randint(1, self.width - 2)
        tree_y = random.randint(3, self.height - 4)

        trunk_height = random.randint(2, 4)
        canopy_size = random.randint(3, 6)

        # Draw the tree canopy
        for _ in range(canopy_size):
            dx = random.randint(-2, 2)
            dy = random.randint(-3, 0)
            x, y = tree_x + dx, tree_y + dy
            if 0 <= x < self.width and 0 <= y < self.height:
                self.pixel_matrix[y][x] = tree_color

        # Draw the trunk
        for dy in range(trunk_height):
            for dx in range(-1, 2):  # Trunk width
                x, y = tree_x + dx, tree_y + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.pixel_matrix[y][x] = trunk_color


    def write_matrix_to_file(self):
        try:
            with open(self.temp_file_path, 'w') as file:
                for row in self.pixel_matrix:
                    line = ' '.join(','.join(map(str, pixel)) for pixel in row)
                    file.write(line + '\n')
            os.replace(self.temp_file_path, self.file_path)
        except IOError as e:
            print(f"Error writing to file {self.file_path}: {e}")
            sys.exit(1)

    def refresh(self):
        gen = random.randint(0, 10)
        if gen > 8:
            self.new_tree()
        else:
            self.new_flower()


        self.write_matrix_to_file()
        time.sleep(self.update_interval)

