import pygame

class Matrix:
    def __init__(self, width, height, default_value=0):
        self.width = width
        self.height = height
        self.data = [[default_value for _ in range(width)] for _ in range(height)]

    def set_pixel(self, x, y, value):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y][x] = value

    def get_pixel(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x]
        return None

    def load_from_file(self, file_path):
        with open(file_path, 'r') as file:
            for y, line in enumerate(file):
                pixels = line.strip().split(' ')
                for x, pixel in enumerate(pixels):
                    r, g, b = map(int, pixel.split(','))
                    self.set_pixel(x, y, (r, g, b))

class PixelAnimationGame:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Screen dimensions and scale
        self.original_width, self.original_height = 150, 100
        self.scale_factor = 8
        self.scaled_width = self.original_width * self.scale_factor
        self.scaled_height = self.original_height * self.scale_factor

        # Colors
        self.background_color = (0, 0, 0)  # Background color

        # Matrix
        self.matrix = Matrix(self.original_width, self.original_height)
        self.matrix2 = Matrix(self.original_width, self.original_height)
        self.matrix.load_from_file("data/matrix_data.txt")

        # Create the display
        self.screen = pygame.display.set_mode((self.scaled_width, self.scaled_height))
        self.game_surface = pygame.Surface((self.original_width, self.original_height))

        # Game variables
        self.running = True
        self.started = False

        # Frame rate control
        self.clock = pygame.time.Clock()
        self.fps = 120  # Frames per second

    def run(self):
        # Game loop
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Start the animation on mouse click
                    self.started = True

            # Update and render
            self.update()
            self.render()

            # Control the frame rate
            self.clock.tick(self.fps)

        # Quit Pygame
        pygame.quit()

    def update(self):
        # Update game logic here
        if self.started:
            self.matrix.load_from_file('data/matrix_data.txt')

    def render(self):
        # Fill the background
        self.game_surface.fill(self.background_color)

        # Draw the entire matrix
        for y in range(self.original_height):
            for x in range(self.original_width):
                pixel_value = self.matrix.get_pixel(x, y)
                if pixel_value is not None:
                    # Directly use the pixel value as a color
                    self.game_surface.set_at((x, y), pixel_value)

        # Scale and display
        scaled_surface = pygame.transform.scale(self.game_surface, (self.scaled_width, self.scaled_height))
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()



if __name__ == "__main__":
    game = PixelAnimationGame()
    game.run()
