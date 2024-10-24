import pygame
import random
from pathlib import Path

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1400, 800
FPS = 60
BOAT_SIZE = (90, 90)  # Fixed boat dimensions
INITIAL_OBSTACLE_SPAWN_RATE = 110  # Initial obstacle spawn rate (in frames)
MEDIA_DIR = Path(__file__).parent / "media"

# Load the background image
background_image = pygame.image.load(str(MEDIA_DIR / "background.jpg"))
background_image = pygame.transform.scale(
    background_image, (WIDTH, HEIGHT)
)  # Scale to match the screen size

# Colors
WHITE = (255, 255, 255)

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

# Load the bullet image
bullet_image = pygame.image.load(str(MEDIA_DIR / "bullet.png"))
bullet_image = pygame.transform.scale(
    bullet_image, (10, 10)
)  # Scale the bullet image if necessary

# Load the boom image
boom_image = pygame.image.load(str(MEDIA_DIR / "boom.png"))
boom_image = pygame.transform.scale(
    boom_image, (64, 64)
)  # Scale the boom image if necessary

# Load the pirate boat image
pirate_boat_image = pygame.image.load(str(MEDIA_DIR / "pirate-boat.png"))
pirate_boat_image = pygame.transform.scale(pirate_boat_image, BOAT_SIZE)

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
hearts = 5

# Points counter
points = 0


# Function to rotate the boat image
def rotate_boat_image(image, angle):
    return pygame.transform.rotate(image, angle)


# Function to check for collisions using masks
def check_collision(boat_rect, obstacles):
    boat_mask = pygame.mask.from_surface(rotated_boat_image)
    for obstacle in obstacles:
        if not obstacle.warning_active:
            offset = (obstacle.rect.x - boat_rect.x, obstacle.rect.y - boat_rect.y)
            if boat_mask.overlap(obstacle.mask, offset):
                return obstacle
    return None


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


# Function to display win screen
def display_win_screen(screen):
    font = pygame.font.Font(None, 74)
    text = font.render("You Win!", True, (0, 255, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(2000)


# Define obstacle class
class Obstacle:
    def __init__(self):
        while True:
            # Randomly position and size the obstacle
            self.width = random.randint(100, 150)
            self.height = random.randint(100, 150)
            self.x = random.randint(0, WIDTH - self.width)
            self.y = random.randint(0, HEIGHT - self.height)

            # Check for overlap with existing obstacles
            if not any(self.overlaps_with(obstacle) for obstacle in obstacles):
                break

        self.lifetime = 900  # Obstacles disappear after 900 frames (15 seconds)
        self.hit_count = 8  # Obstacles require 8 hits to be destroyed

        # Warning phase settings
        self.warning_duration = 100  # The warning lasts for 100 frames
        self.warning_active = True  # Start in warning mode
        self.warning_size = (
            self.width // 2,
            self.height // 2,
        )  # Smaller size for warning
        self.warning_image = pygame.transform.scale(MOUNTAIN_IMAGE, self.warning_size)
        self.warning_alpha = 128  # Transparency for the warning (0-255)

        # Full-size obstacle image
        self.obstacle_image = pygame.transform.scale(
            MOUNTAIN_IMAGE, (self.width, self.height)
        )

        # Create a mask for the obstacle image
        self._mask = pygame.mask.from_surface(self.obstacle_image)

        # Position the warning image at the center of where the full obstacle will be
        self.warning_x = self.x + self.width // 4  # Center the warning horizontally
        self.warning_y = self.y + self.height // 4  # Center the warning vertically

    def overlaps_with(self, other):
        return self.rect.colliderect(other.rect)

    def update(self):
        if self.warning_active:
            self.warning_duration -= 1
            if self.warning_duration <= 0:
                self.warning_active = False

    def draw(self, screen):
        if self.warning_active:
            # Add shaking effect
            shake_offset = random.randint(-5, 5)
            self.warning_image.set_alpha(self.warning_alpha)
            screen.blit(
                self.warning_image,
                (self.warning_x + shake_offset, self.warning_y + shake_offset),
            )
        else:
            screen.blit(self.obstacle_image, (self.x, self.y))

    def is_expired(self):
        self.lifetime -= 1
        return self.lifetime <= 0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def mask(self):
        return self._mask


# Define bullet class
class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 10
        self.image = bullet_image

    def update(self):
        if self.direction == UP:
            self.y -= self.speed
        elif self.direction == DOWN:
            self.y += self.speed
        elif self.direction == LEFT:
            self.x -= self.speed
        elif self.direction == RIGHT:
            self.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    @property
    def rect(self):
        return pygame.Rect(
            self.x, self.y, self.image.get_width(), self.image.get_height()
        )


# Define boom class
class Boom:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = boom_image
        self.lifetime = 30  # Boom effect lasts for 30 frames

    def update(self):
        self.lifetime -= 1

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def is_expired(self):
        return self.lifetime <= 0


# Define pirate bullet class
class PirateBullet:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = 5
        self.image = bullet_image

        # Calculate direction vector
        dx = target_x - x
        dy = target_y - y
        distance = (dx**2 + dy**2) ** 0.5
        self.direction_x = dx / distance
        self.direction_y = dy / distance

    def update(self):
        self.x += self.direction_x * self.speed
        self.y += self.direction_y * self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def check_collision_with_obstacles(self, obstacles):
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                return True
        return False

    @property
    def rect(self):
        return pygame.Rect(
            self.x, self.y, self.image.get_width(), self.image.get_height()
        )


# Define pirate boat class
class PirateBoat:
    def __init__(self):
        self.width = BOAT_SIZE[0]
        self.height = BOAT_SIZE[1]
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(0, HEIGHT - self.height)
        self.lifetime = 420  # Pirate boat appears for 7 seconds (300 frames)
        self.hit_count = 3  # Pirate boat requires 3 hits to be destroyed
        self.fire_rate = 60  # Fire a bullet every 60 frames (1 second)
        self.fire_timer = 0

    def update(self):
        self.lifetime -= 1
        self.fire_timer += 1
        if self.fire_timer >= self.fire_rate:
            self.fire_timer = 0
            return self.fire_bullet()
        return None

    def fire_bullet(self):
        return PirateBullet(
            self.x + self.width // 2, self.y + self.height // 2, boat_x, boat_y
        )

    def draw(self, screen):
        screen.blit(pirate_boat_image, (self.x, self.y))

    def is_expired(self):
        return self.lifetime <= 0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# List to store obstacles
obstacles = []

# List to store bullets
bullets = []

# List to store boom effects
booms = []

# List to store pirate boats
pirate_boats = []

# List to store pirate bullets
pirate_bullets = []

# Timer for obstacle spawning
obstacle_timer = 0
obstacle_spawn_rate = INITIAL_OBSTACLE_SPAWN_RATE

# Timer for pirate boat spawning
pirate_boat_timer = 0
pirate_boat_spawn_interval = 600  # Pirate boat spawns every 10 seconds (600 frames)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(FPS)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Shoot a bullet
                bullet_x = boat_x + BOAT_SIZE[0] // 2 - bullet_image.get_width() // 2
                bullet_y = boat_y + BOAT_SIZE[1] // 2 - bullet_image.get_height() // 2
                bullets.append(Bullet(bullet_x, bullet_y, boat_direction))

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

    # Increment the pirate boat timer
    pirate_boat_timer += 1

    # Generate a pirate boat at regular intervals
    if pirate_boat_timer >= pirate_boat_spawn_interval:
        pirate_boats.append(PirateBoat())
        pirate_boat_timer = 0

    # Update and draw obstacles
    for obstacle in obstacles:
        obstacle.update()
        obstacle.draw(screen)

        # Remove obstacles once their lifetime has expired
        if obstacle.is_expired():
            obstacles.remove(obstacle)

    # Update and draw bullets
    for bullet in bullets:
        bullet.update()
        bullet.draw(screen)

        # Check for bullet collisions with obstacles
        for obstacle in obstacles:
            if bullet.rect.colliderect(obstacle.rect):
                obstacle.hit_count -= 1
                bullets.remove(bullet)
                if obstacle.hit_count <= 0:
                    # Calculate the center position of the obstacle for the boom effect
                    boom_x = (
                        obstacle.x + obstacle.width // 2 - boom_image.get_width() // 2
                    )
                    boom_y = (
                        obstacle.y + obstacle.height // 2 - boom_image.get_height() // 2
                    )
                    booms.append(Boom(boom_x, boom_y))
                    obstacles.remove(obstacle)
                break

        # Check for bullet collisions with pirate boats
        for pirate_boat in pirate_boats:
            if bullet.rect.colliderect(pirate_boat.rect):
                pirate_boat.hit_count -= 1
                bullets.remove(bullet)
                if pirate_boat.hit_count <= 0:
                    # Calculate the center position of the pirate boat for the boom effect
                    boom_x = (
                        pirate_boat.x
                        + pirate_boat.width // 2
                        - boom_image.get_width() // 2
                    )
                    boom_y = (
                        pirate_boat.y
                        + pirate_boat.height // 2
                        - boom_image.get_height() // 2
                    )
                    booms.append(Boom(boom_x, boom_y))
                    pirate_boats.remove(pirate_boat)
                    points += 1  # Increase points counter
                break

        # Remove bullets that go off-screen
        if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
            bullets.remove(bullet)

    # Update and draw boom effects
    for boom in booms:
        boom.update()
        boom.draw(screen)

        # Remove boom effects once their lifetime has expired
        if boom.is_expired():
            booms.remove(boom)

    # Update and draw pirate boats
    for pirate_boat in pirate_boats:
        new_bullet = pirate_boat.update()
        if new_bullet:
            pirate_bullets.append(new_bullet)
        pirate_boat.draw(screen)

        # Remove pirate boats once their lifetime has expired
        if pirate_boat.is_expired():
            pirate_boats.remove(pirate_boat)

    # Draw the rotated boat image
    boat_rect = rotated_boat_image.get_rect(
        center=(boat_x + BOAT_SIZE[0] // 2, boat_y + BOAT_SIZE[1] // 2)
    )
    screen.blit(rotated_boat_image, boat_rect.topleft)

    # Update and draw pirate bullets
    for pirate_bullet in pirate_bullets:
        pirate_bullet.update()
        pirate_bullet.draw(screen)

        # Check for collisions with obstacles
        if pirate_bullet.check_collision_with_obstacles(obstacles):
            pirate_bullets.remove(pirate_bullet)
            continue

        # Check for collisions with the player's boat
        if pirate_bullet.rect.colliderect(boat_rect):
            flash_screen(
                screen, (255, 0, 0), 20, 8
            )  # Flash the screen red for 10 frames
            boat_x = boat_start_x  # Reset boat position
            boat_y = boat_start_y
            hearts -= 1  # Decrease the number of hearts
            pirate_bullets.remove(pirate_bullet)
            if hearts == 0:
                display_game_over(screen)  # Display game over screen
                running = False  # End the game loop

        # Remove bullets that go off-screen
        if (
            pirate_bullet.x < 0
            or pirate_bullet.x > WIDTH
            or pirate_bullet.y < 0
            or pirate_bullet.y > HEIGHT
        ):
            pirate_bullets.remove(pirate_bullet)

    # Check for collisions
    colliding_obstacle = check_collision(boat_rect, obstacles)
    if colliding_obstacle:
        flash_screen(screen, (255, 0, 0), 20, 8)  # Flash the screen red for 10 frames
        boat_x = boat_start_x  # Reset boat position
        boat_y = boat_start_y
        hearts -= 1  # Decrease the number of hearts
        if colliding_obstacle.rect.colliderect(
            pygame.Rect(boat_start_x, boat_start_y, BOAT_SIZE[0], BOAT_SIZE[1])
        ):
            obstacles.remove(
                colliding_obstacle
            )  # Remove the colliding obstacle if in spawn location
        if hearts == 0:
            display_game_over(screen)  # Display game over screen
            running = False  # End the game loop

    # Draw hearts (lives)
    for i in range(hearts):
        screen.blit(heart_image, (10 + i * 40, 10))

    # Draw points counter
    font = pygame.font.Font(None, 36)
    points_text = font.render(f"Points: {points}", True, WHITE)
    screen.blit(points_text, (WIDTH - 150, 10))

    # Check for win condition
    if points >= 10:
        display_win_screen(screen)
        running = False  # End the game loop

    # Update the display
    pygame.display.flip()

pygame.quit()
