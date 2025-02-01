import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()

# Define Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# -----------------------------
# Ship Class
# -----------------------------
class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0  # In degrees
        self.velocity = [0, 0]
        self.radius = 10

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        # Apply friction to gradually slow the ship down
        self.velocity[0] *= 0.99
        self.velocity[1] *= 0.99
        # Wrap around the screen edges
        if self.x < 0:
            self.x += screen_width
        elif self.x > screen_width:
            self.x -= screen_width
        if self.y < 0:
            self.y += screen_height
        elif self.y > screen_height:
            self.y -= screen_height

    def draw(self, surface):
        # Calculate the ship's tip and its two rear vertices for a triangle shape
        tip_x = self.x + math.cos(math.radians(self.angle)) * self.radius * 2
        tip_y = self.y - math.sin(math.radians(self.angle)) * self.radius * 2
        left_x = self.x + math.cos(math.radians(self.angle + 130)) * self.radius
        left_y = self.y - math.sin(math.radians(self.angle + 130)) * self.radius
        right_x = self.x + math.cos(math.radians(self.angle - 130)) * self.radius
        right_y = self.y - math.sin(math.radians(self.angle - 130)) * self.radius
        pygame.draw.polygon(surface, WHITE, [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)], 1)

# -----------------------------
# Bullet Class
# -----------------------------
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        speed = 10
        self.vx = math.cos(math.radians(angle)) * speed
        self.vy = -math.sin(math.radians(angle)) * speed
        self.life = 60  # Bullet exists for 60 frames

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        # Wrap around the screen edges
        if self.x < 0:
            self.x += screen_width
        elif self.x > screen_width:
            self.x -= screen_width
        if self.y < 0:
            self.y += screen_height
        elif self.y > screen_height:
            self.y -= screen_height

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 2)

# -----------------------------
# Asteroid Class
# -----------------------------
class Asteroid:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size  # 3 = large, 2 = medium, 1 = small
        angle = random.uniform(0, 360)
        speed = random.uniform(1, 3)
        self.vx = math.cos(math.radians(angle)) * speed
        self.vy = -math.sin(math.radians(angle)) * speed
        self.radius = size * 15  # Adjust radius based on size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # Wrap around the screen edges
        if self.x < 0:
            self.x += screen_width
        elif self.x > screen_width:
            self.x -= screen_width
        if self.y < 0:
            self.y += screen_height
        elif self.y > screen_height:
            self.y -= screen_height

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 1)

# -----------------------------
# Instruction Screen
# -----------------------------
def show_instructions():
    font = pygame.font.SysFont(None, 40)
    instructions = [
        "ASTEROIDS",
        "",
        "Controls:",
        "Left/Right Arrow: Rotate",
        "Up Arrow: Thrust",
        "Space: Fire",
        "",
        "Avoid asteroids and shoot them!",
        "",
        "Press any key to start..."
    ]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return
        screen.fill(BLACK)
        for i, line in enumerate(instructions):
            text = font.render(line, True, WHITE)
            screen.blit(text, (screen_width / 2 - text.get_width() / 2, 100 + i * 40))
        pygame.display.update()
        clock.tick(60)

# -----------------------------
# Game Over Screen with Restart Option
# -----------------------------
def game_over_screen():
    font_large = pygame.font.SysFont(None, 55)
    font_small = pygame.font.SysFont(None, 40)
    game_over_text = font_large.render("Game Over!", True, WHITE)
    restart_text = font_small.render("Press R to restart or Q to quit", True, WHITE)
    
    while True:
        screen.fill(BLACK)
        screen.blit(game_over_text, (screen_width / 2 - game_over_text.get_width() / 2,
                                     screen_height / 2 - game_over_text.get_height()))
        screen.blit(restart_text, (screen_width / 2 - restart_text.get_width() / 2,
                                   screen_height / 2 + 10))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Quit the game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True   # Restart the game
                elif event.key == pygame.K_q:
                    return False  # Quit the game
        clock.tick(60)

# -----------------------------
# Main Game Loop
# -----------------------------
def main():
    # Initialize game objects
    ship = Ship(screen_width / 2, screen_height / 2)
    bullets = []
    asteroids = []

    # Create initial asteroids coming from the screen edges
    for i in range(5):
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x = random.randint(0, screen_width)
            y = 0
        elif side == "bottom":
            x = random.randint(0, screen_width)
            y = screen_height
        elif side == "left":
            x = 0
            y = random.randint(0, screen_height)
        else:  # right
            x = screen_width
            y = random.randint(0, screen_height)
        asteroids.append(Asteroid(x, y, 3))

    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit the game loop
            # Fire a bullet when space is pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet_x = ship.x + math.cos(math.radians(ship.angle)) * ship.radius * 2
                    bullet_y = ship.y - math.sin(math.radians(ship.angle)) * ship.radius * 2
                    bullets.append(Bullet(bullet_x, bullet_y, ship.angle))

        # Handle continuous key presses for rotation and thrust
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            ship.angle += 5
        if keys[pygame.K_RIGHT]:
            ship.angle -= 5
        if keys[pygame.K_UP]:
            thrust = 0.2
            ship.velocity[0] += math.cos(math.radians(ship.angle)) * thrust
            ship.velocity[1] -= math.sin(math.radians(ship.angle)) * thrust

        # Update game objects
        ship.update()
        for bullet in bullets[:]:
            bullet.update()
            if bullet.life <= 0:
                bullets.remove(bullet)
        for asteroid in asteroids:
            asteroid.update()

        # Check for bullet-asteroid collisions
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                dist = math.hypot(bullet.x - asteroid.x, bullet.y - asteroid.y)
                if dist < asteroid.radius:
                    if bullet in bullets:
                        bullets.remove(bullet)
                    if asteroid in asteroids:
                        asteroids.remove(asteroid)
                    # If the asteroid is not the smallest, split it into two smaller ones
                    if asteroid.size > 1:
                        for _ in range(2):
                            asteroids.append(Asteroid(asteroid.x, asteroid.y, asteroid.size - 1))
                    break

        # Check for collisions between the ship and asteroids
        for asteroid in asteroids:
            dist = math.hypot(ship.x - asteroid.x, ship.y - asteroid.y)
            if dist < asteroid.radius + ship.radius:
                game_over = True
                break

        # Draw everything on the screen
        screen.fill(BLACK)
        ship.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for asteroid in asteroids:
            asteroid.draw(screen)

        pygame.display.update()
        clock.tick(60)

    # Show game over screen and ask to restart or quit
    return game_over_screen()

# -----------------------------
# Run the Game with Restart Option
# -----------------------------
if __name__ == "__main__":
    show_instructions()
    while True:
        restart = main()
        if not restart:
            break
    pygame.quit()
    sys.exit()
