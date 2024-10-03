import pygame
import random
from pathlib import Path

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
BOAT_SIZE = (50, 100)  # Fixed boat dimensions
INITIAL_OBSTACLE_SPAWN_RATE = 120  # Initial obstacle spawn rate (in frames)
MEDIA_DIR = Path(__file__).parent / "media"

# Load the background image
background_image = pygame.image.load(str(MEDIA_DIR / "background.jpg"))
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Scale to match the screen size

# Colors
WHITE = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0, 100)  # Semi-transparent black for shadows

# Objects
MOUNTAIN_IMAGE = pygame.image.load(str(MEDIA_DIR / "mountain.png"))

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boat Adventure")

# Load the boat image
boat_image = pygame.Surface(BOAT_SIZE)
boat_image.fill(WHITE)

# Set up the boat's starting position
boat_x = WIDTH // 2 - BOAT_SIZE[0] // 2
boat_y = HEIGHT // 2 - BOAT_SIZE[1] // 2


# Define obstacle class
class Obstacle:
    def __init__(self):
        # Randomly position and size the obstacle
        self.width = random.randint(50, 100)
        self.height = random.randint(50, 100)
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(0, HEIGHT - self.height)
        self.lifetime = 300  # Obstacles disappear after 300 frames (5 seconds)

        # Warning phase settings
        self.warning_duration = 100  # The warning lasts for 100 frames
        self.warning_active = True   # Start in warning mode
        self.warning_size = (self.width // 2, self.height // 2)  # Smaller size for warning
        self.warning_image = pygame.transform.scale(MOUNTAIN_IMAGE, self.warning_size)
        self.warning_alpha = 128  # Transparency for the warning (0-255)

        # Full-size obstacle image
        self.obstacle_image = pygame.transform.scale(MOUNTAIN_IMAGE, (self.width, self.height))

        # Position the warning image at the center of where the full obstacle will be
        self.warning_x = self.x + self.width // 4  # Center the warning horizontally
        self.warning_y = self.y + self.height // 4  # Center the warning vertically

    def draw(self, screen):
        if self.warning_active:
            # During warning phase: shaking, transparent, and smaller
            jitter_x = random.randint(-2, 2)  # Slight horizontal shaking
            jitter_y = random.randint(-2, 2)  # Slight vertical shaking
            self.warning_image.set_alpha(self.warning_alpha)  # Set transparency

            # Draw the shaking transparent warning image, centered
            screen.blit(self.warning_image, (self.warning_x + jitter_x, self.warning_y + jitter_y))
        else:
            # After warning: draw the normal full-size obstacle centered where the warning was
            screen.blit(self.obstacle_image, (self.x, self.y))

    def update(self):
        self.lifetime -= 1

        # Update the warning phase timer
        if self.warning_duration > 0:
            self.warning_duration -= 1
        else:
            self.warning_active = False  # End the warning phase after the duration

    def is_expired(self):
        return self.lifetime <= 0


# List to store obstacles
obstacles = []

# Timer for obstacle spawning
obstacle_timer = 0
obstacle_spawn_rate = INITIAL_OBSTACLE_SPAWN_RATE

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(FPS)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Boat movement
    keys = pygame.key.get_pressed()
    speed = 5
    if keys[pygame.K_LEFT] and boat_x > 0:
        boat_x -= speed
    if keys[pygame.K_RIGHT] and boat_x < WIDTH - BOAT_SIZE[0]:
        boat_x += speed
    if keys[pygame.K_UP] and boat_y > 0:
        boat_y -= speed
    if keys[pygame.K_DOWN] and boat_y < HEIGHT - BOAT_SIZE[1]:
        boat_y += speed

    # Draw the background image
    screen.blit(background_image, (0, 0))

    # Increment the obstacle timer
    obstacle_timer += 1

    # Generate an obstacle at regular intervals
    if obstacle_timer >= obstacle_spawn_rate:
        obstacles.append(Obstacle())
        obstacle_timer = 0

    # Update and draw obstacles
    for obstacle in obstacles:
        obstacle.update()
        obstacle.draw(screen)

        # Remove obstacles once their lifetime has expired
        if obstacle.is_expired():
            obstacles.remove(obstacle)

    # Draw shadow for the boat (optional)
    shadow_rect = pygame.Rect(boat_x, boat_y + BOAT_SIZE[1] // 2, BOAT_SIZE[0], 10)
    pygame.draw.ellipse(screen, SHADOW_COLOR, shadow_rect)

    # Draw the boat without scaling
    screen.blit(boat_image, (boat_x, boat_y))

    # Update the display
    pygame.display.flip()

pygame.quit()
