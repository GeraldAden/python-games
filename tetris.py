import pygame
import random
import sys

# Initialize pygame fonts
pygame.font.init()

# Global Variables for the game window and play area
s_width = 800
s_height = 700
play_width = 300  # 10 columns * 30 pixels per block
play_height = 600  # 20 rows * 30 pixels per block
block_size = 30

# Top-left position of the play area
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

# Define the 7 tetromino shapes and their rotations.
# Each shape is represented by a list of strings.
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# List of shapes and their colors (RGB)
shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (0, 255, 0),    # S - Green
    (255, 0, 0),    # Z - Red
    (0, 255, 255),  # I - Cyan
    (255, 255, 0),  # O - Yellow
    (255, 165, 0),  # J - Orange
    (0, 0, 255),    # L - Blue
    (128, 0, 128)   # T - Purple
]

# Class to represent a tetromino piece.
class Piece:
    def __init__(self, x, y, shape):
        self.x = x  # grid column position
        self.y = y  # grid row position
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # current rotation state

# Create the Tetris grid: a 20x10 grid initialized to black.
def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid

# Convert the piece's shape format into grid positions.
def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]
    
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                # Adjust the position to align with the grid (offset by 2 columns and 4 rows)
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions

# Check if the current position of the piece is valid on the grid.
def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [pos for sub in accepted_positions for pos in sub]
    
    formatted = convert_shape_format(piece)
    
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

# Check if any locked positions are above the top of the grid.
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

# Get a random new tetromino piece.
def get_shape():
    return Piece(5, 0, random.choice(shapes))

# Draw text centered on the screen.
def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    
    surface.blit(label, (top_left_x + play_width/2 - label.get_width()/2,
                         top_left_y + play_height/2 - label.get_height()/2))

# Draw grid lines on the play area.
def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y
    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * block_size),
                         (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j * block_size, sy),
                             (sx + j * block_size, sy + play_height))

# Clear completed rows and shift the remaining blocks downward.
def clear_rows(grid, locked):
    cleared = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            cleared += 1
            index = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if cleared > 0:
        # Shift every row above down by the number of cleared rows.
        for key in sorted(list(locked), key=lambda x: x[1], reverse=True):
            x, y = key
            if y < index:
                newKey = (x, y + cleared)
                locked[newKey] = locked.pop(key)
    return cleared

# Draw the "next" tetromino in a preview box.
def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', True, (255, 255, 255))
    
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = piece.shape[piece.rotation % len(piece.shape)]
    
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, piece.color, 
                                 (sx + j * block_size, sy + i * block_size, block_size, block_size), 0)
    surface.blit(label, (sx + 10, sy - 30))

# Draw the main game window including the grid, title, and score.
def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))
    # Title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', True, (255, 255, 255))
    
    surface.blit(label, (top_left_x + play_width/2 - label.get_width()/2, 30))
    
    # Score display
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), True, (255, 255, 255))
    
    sx = top_left_x - 200
    sy = top_left_y + 200
    surface.blit(label, (sx + 20, sy + 160))
    
    # Draw the grid blocks
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)
    
    draw_grid(surface, grid)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

# Main game loop.
def main():
    locked_positions = {}
    grid = create_grid(locked_positions)
    
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    score = 0
    
    run = True
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()
        
        # Handle automatic piece falling.
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                # Lock the piece and spawn a new one.
                for pos in convert_shape_format(current_piece):
                    locked_positions[(pos[0], pos[1])] = current_piece.color
                current_piece = next_piece
                next_piece = get_shape()
                cleared = clear_rows(grid, locked_positions)
                score += cleared * 10
        
        # Process user inputs.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                elif event.key == pygame.K_SPACE:  # Hard drop
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
        
                    for pos in convert_shape_format(current_piece):
                        locked_positions[(pos[0], pos[1])] = current_piece.color
                    current_piece = next_piece
                    next_piece = get_shape()
                    cleared = clear_rows(grid, locked_positions)
                    score += cleared * 10
        
        # Draw the current piece on the grid.
        for pos in convert_shape_format(current_piece):
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color
        
        draw_window(screen, grid, score)
        draw_next_shape(next_piece, screen)
        pygame.display.update()
        
        if check_lost(locked_positions):
            draw_text_middle(screen, "YOU LOST", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

# Main menu screen before the game starts.
def main_menu():
    run = True
    while run:
        screen.fill((0, 0, 0))
        draw_text_middle(screen, "Press Any Key To Play", 60, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

# Set up the game window.
screen = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')

if __name__ == '__main__':
    main_menu()
