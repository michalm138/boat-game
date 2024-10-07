import pygame
import random
from pathlib import Path

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
BOAT_SIZE = (64, 64)  # Fixed boat dimensions
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
boat_image = pygame.image.load(str(MEDIA_DIR / "boat.png"))

# Scale the boat image to the size defined by BOAT_SIZE
boat_image = pygame.transform.scale(boat_image, BOAT_SIZE)

# Load the heart image
heart_image = pygame.image.load(str(MEDIA_DIR / "heart.png"))
heart_image = pygame.transform.scale(heart_image, (32, 32))

# Set up the boat's starting position
boat_start_x = WIDTH // 2 - BOAT_SIZE[0] // 2
boat_start_y = HEIGHT // 2 - BOAT_SIZE[1] // 2
boat_x = boat_start_x
boat_y = boat_start_y

# Define the boat's directions
UP = 0
DOWN = 180
LEFT = 90
RIGHT = -90

# Initial direction is to the right
boat_direction = RIGHT

# Number of hearts (lives)
hearts = 3


# Function to rotate the boat image
def rotate_boat_image(image, angle):
    return pygame.transform.rotate(image, angle)


# Function to check for collisions
def check_collision(boat_rect, obstacles):
    for obstacle in obstacles:
        if not obstacle.warning_active and boat_rect.colliderect(obstacle.rect):
            return True
    return False


# Function to flash the screen with a semi-transparent red overlay
def flash_screen(screen, color, alpha, duration):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(alpha)
    overlay.fill(color)
    for _ in range(duration):
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(50)


# Function to display game over screen
def display_game_over(screen):
    font = pygame.font.Font(None, 74)
    text = font.render("Game Over", True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(2000)


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

    def update(self):
        if self.warning_active:
            self.warning_duration -= 1
            if self.warning_duration <= 0:
                self.warning_active = False

    def draw(self, screen):
        if self.warning_active:
            self.warning_image.set_alpha(self.warning_alpha)
            screen.blit(self.warning_image, (self.warning_x, self.warning_y))
        else:
            screen.blit(self.obstacle_image, (self.x, self.y))

    def is_expired(self):
        self.lifetime -= 1
        return self.lifetime <= 0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


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
        boat_direction = LEFT
        boat_x -= speed
    if keys[pygame.K_RIGHT] and boat_x < WIDTH - BOAT_SIZE[0]:
        boat_direction = RIGHT
        boat_x += speed
    if keys[pygame.K_UP] and boat_y > 0:
        boat_direction = UP
        boat_y -= speed
    if keys[pygame.K_DOWN] and boat_y < HEIGHT - BOAT_SIZE[1]:
        boat_direction = DOWN
        boat_y += speed

    # Rotate the boat image based on the current direction
    rotated_boat_image = rotate_boat_image(boat_image, boat_direction)

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

    # Draw the rotated boat image
    boat_rect = rotated_boat_image.get_rect(center=(boat_x + BOAT_SIZE[0] // 2, boat_y + BOAT_SIZE[1] // 2))
    screen.blit(rotated_boat_image, boat_rect.topleft)

    # Check for collisions
    if check_collision(boat_rect, obstacles):
        flash_screen(screen, (255, 0, 0), 20, 8)  # Flash the screen red for 10 frames
        boat_x = boat_start_x  # Reset boat position
        boat_y = boat_start_y
        hearts -= 1  # Decrease the number of hearts
        if hearts == 0:
            display_game_over(screen)  # Display game over screen
            running = False  # End the game loop

    # Draw hearts (lives)
    for i in range(hearts):
        screen.blit(heart_image, (10 + i * 40, 10))

    # Update the display
    pygame.display.flip()

pygame.quit()
