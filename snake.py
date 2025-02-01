import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game constants
CELL_SIZE = 20
COLS = 30
ROWS = 20
WIDTH = CELL_SIZE * COLS  # 600 pixels
HEIGHT = CELL_SIZE * ROWS  # 400 pixels

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)
BLUE  = (50, 153, 213)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()
SNAKE_SPEED = 10  # Frames per second

def game_loop():
    # Initial snake position (center of the screen)
    snake_x = WIDTH // 2
    snake_y = HEIGHT // 2
    x_change = 0
    y_change = 0

    snake_list = []
    snake_length = 1

    # Score counter
    score = 0

    # Place the first food item at a random location
    food_x = round(random.randrange(0, WIDTH - CELL_SIZE) / CELL_SIZE) * CELL_SIZE
    food_y = round(random.randrange(0, HEIGHT - CELL_SIZE) / CELL_SIZE) * CELL_SIZE

    # --- Start Screen ---
    start = True
    start_font = pygame.font.SysFont(None, 40)
    while start:
        screen.fill(BLUE)
        message = start_font.render("Press any arrow key to start", True, WHITE)
        screen.blit(message, (WIDTH / 6, HEIGHT / 2))
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Set the initial direction based on the key pressed.
                if event.key == pygame.K_LEFT:
                    x_change = -CELL_SIZE
                    y_change = 0
                elif event.key == pygame.K_RIGHT:
                    x_change = CELL_SIZE
                    y_change = 0
                elif event.key == pygame.K_UP:
                    y_change = -CELL_SIZE
                    x_change = 0
                elif event.key == pygame.K_DOWN:
                    y_change = CELL_SIZE
                    x_change = 0
                start = False

    # --- Main Game Loop ---
    game_over = False
    score_font = pygame.font.SysFont(None, 35)
    while not game_over:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Change direction, disallowing direct reversals.
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -CELL_SIZE
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = CELL_SIZE
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -CELL_SIZE
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = CELL_SIZE
                    x_change = 0

        # Update snake position
        snake_x += x_change
        snake_y += y_change

        # --- Screen Wrapping ---
        if snake_x < 0:
            snake_x = WIDTH - CELL_SIZE
        elif snake_x >= WIDTH:
            snake_x = 0
        if snake_y < 0:
            snake_y = HEIGHT - CELL_SIZE
        elif snake_y >= HEIGHT:
            snake_y = 0

        # Fill the screen with background color
        screen.fill(BLUE)

        # Draw the food
        pygame.draw.rect(screen, GREEN, [food_x, food_y, CELL_SIZE, CELL_SIZE])

        # Update the snake's segments
        snake_head = [snake_x, snake_y]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        # Check for collision with itself
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_over = True

        # Draw the snake
        for segment in snake_list:
            pygame.draw.rect(screen, WHITE, [segment[0], segment[1], CELL_SIZE, CELL_SIZE])

        # Display the score at the top left corner
        score_text = score_font.render("Score: " + str(score), True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.update()

        # Check if the snake has eaten the food
        if snake_x == food_x and snake_y == food_y:
            # Move food to a new random location
            food_x = round(random.randrange(0, WIDTH - CELL_SIZE) / CELL_SIZE) * CELL_SIZE
            food_y = round(random.randrange(0, HEIGHT - CELL_SIZE) / CELL_SIZE) * CELL_SIZE
            snake_length += 1
            score += 1  # Increase score

        clock.tick(SNAKE_SPEED)

    # --- Game Over Screen ---
    over_font = pygame.font.SysFont(None, 50)
    message = over_font.render("Game Over!", True, RED)
    screen.blit(message, (WIDTH / 3, HEIGHT / 3))
    pygame.display.update()
    pygame.time.wait(2000)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    game_loop()
