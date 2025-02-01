import pygame
import sys
import math
import random

# -------------------------------
# Global Settings and Maze Data
# -------------------------------

pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac‑Man")
clock = pygame.time.Clock()

# Maze definition (11 rows x 21 columns)
# In these strings, '#' represents a wall; any other character represents an open cell with a dot.
maze = [
    "#####################",
    "#........##.........#",
    "#.####...##...####..#",
    "#...................#",
    "#.####.####.####....#",
    "#...................#",
    "#.####.####.####....#",
    "#...................#",
    "#.####...##...####..#",
    "#........##.........#",
    "#####################"
]

ROWS = len(maze)
COLS = len(maze[0])
BLOCK_SIZE = 30  # Each cell is 30x30 pixels
MAZE_WIDTH = COLS * BLOCK_SIZE
MAZE_HEIGHT = ROWS * BLOCK_SIZE

# Center the maze on the screen.
TOP_LEFT_X = (SCREEN_WIDTH - MAZE_WIDTH) // 2
TOP_LEFT_Y = (SCREEN_HEIGHT - MAZE_HEIGHT) // 2

# -------------------------------
# Utility Functions
# -------------------------------

def can_move(row, col, direction):
    """
    Check if moving from cell (row, col) in the grid by 'direction' (dx, dy)
    is allowed (i.e. does not hit a wall).
    """
    dx, dy = direction
    new_row = row + dy
    new_col = col + dx
    if new_row < 0 or new_row >= ROWS or new_col < 0 or new_col >= COLS:
        return False
    return maze[new_row][new_col] != '#'

def create_dots():
    """Return a set of all (row, col) positions that are not walls (i.e. that get a dot)."""
    dots_set = set()
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] != '#':
                dots_set.add((r, c))
    return dots_set

# -------------------------------
# Drawing Functions for Retro Look
# -------------------------------

def draw_ghost(surface, x, y, r, color):
    """
    Draw a ghost at pixel (x, y) (its center) with "radius" r.
    The ghost features a dome on top with scalloped (wavy) bottom and eyes.
    """
    points = []
    # Top corners (dome)
    points.append((x - r, y - r))
    points.append((x + r, y - r))
    # Create scalloped bottom (4 scallops)
    num_scallops = 4
    for i in range(num_scallops + 1):
        bottom_x = x + r - (2 * r * i / num_scallops)
        # Alternate the y-position to create a wave effect.
        if i % 2 == 0:
            bottom_y = y + r
        else:
            bottom_y = y + r - r/3
        points.append((bottom_x, bottom_y))
    pygame.draw.polygon(surface, color, points)
    
    # Draw eyes (white with small black pupils)
    eye_radius = r // 3
    eye_offset_x = r // 2
    eye_offset_y = r // 2
    left_eye_center = (int(x - eye_offset_x), int(y - r//2 + eye_offset_y//2))
    right_eye_center = (int(x + eye_offset_x), int(y - r//2 + eye_offset_y//2))
    pygame.draw.circle(surface, (255, 255, 255), left_eye_center, eye_radius)
    pygame.draw.circle(surface, (255, 255, 255), right_eye_center, eye_radius)
    pupil_radius = eye_radius // 2
    pygame.draw.circle(surface, (0, 0, 0), left_eye_center, pupil_radius)
    pygame.draw.circle(surface, (0, 0, 0), right_eye_center, pupil_radius)

# -------------------------------
# Pac‑Man Class
# -------------------------------

class Pacman:
    def __init__(self, x, y):
        self.x = x  # Pixel x-coordinate (center)
        self.y = y  # Pixel y-coordinate (center)
        self.dir = (0, 0)          # Current movement direction (grid vector: (dx, dy))
        self.desired_dir = (0, 0)  # Latest requested direction (from keyboard)
        self.speed = 3.0           # Movement speed (pixels per frame)
        self.radius = BLOCK_SIZE // 2 - 2

    def update(self):
        # Determine current cell.
        col = int((self.x - TOP_LEFT_X) // BLOCK_SIZE)
        row = int((self.y - TOP_LEFT_Y) // BLOCK_SIZE)
        # Compute cell center.
        cell_center_x = TOP_LEFT_X + (col + 0.5) * BLOCK_SIZE
        cell_center_y = TOP_LEFT_Y + (row + 0.5) * BLOCK_SIZE

        # When nearly centered, try to update direction.
        if abs(self.x - cell_center_x) < 3 and abs(self.y - cell_center_y) < 3:
            if can_move(row, col, self.desired_dir):
                self.dir = self.desired_dir

        # Calculate new position.
        new_x = self.x + self.dir[0] * self.speed
        new_y = self.y + self.dir[1] * self.speed

        # Check if the new cell is open.
        new_col = int((new_x - TOP_LEFT_X) // BLOCK_SIZE)
        new_row = int((new_y - TOP_LEFT_Y) // BLOCK_SIZE)
        if maze[new_row][new_col] != '#':
            self.x = new_x
            self.y = new_y
        else:
            # If blocked, snap to the cell center.
            self.x = cell_center_x
            self.y = cell_center_y

    def draw(self, surface):
        # Draw Pac‑Man as a yellow circle with a black wedge for an open mouth.
        # Use a thicker black outline to mimic the arcade look.
        mouth_angle = math.radians(45)
        if self.dir != (0, 0):
            angle = math.atan2(-self.dir[1], self.dir[0])
        else:
            angle = 0  # Default facing right
        # Draw outer black circle (outline)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius)
        # Draw inner yellow circle
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x), int(self.y)), self.radius - 2)
        # Draw mouth wedge (black polygon)
        point1 = (self.x + self.radius * math.cos(angle + mouth_angle),
                  self.y - self.radius * math.sin(angle + mouth_angle))
        point2 = (self.x + self.radius * math.cos(angle - mouth_angle),
                  self.y - self.radius * math.sin(angle - mouth_angle))
        pygame.draw.polygon(surface, (0, 0, 0), [(self.x, self.y), point1, point2])

# -------------------------------
# Ghost Class
# -------------------------------

class Ghost:
    def __init__(self, x, y, color):
        self.x = x  # Pixel x-coordinate (center)
        self.y = y  # Pixel y-coordinate (center)
        self.dir = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.speed = 2.5
        self.radius = BLOCK_SIZE // 2 - 2
        self.color = color

    def update(self):
        # Determine current cell.
        col = int((self.x - TOP_LEFT_X) // BLOCK_SIZE)
        row = int((self.y - TOP_LEFT_Y) // BLOCK_SIZE)
        cell_center_x = TOP_LEFT_X + (col + 0.5) * BLOCK_SIZE
        cell_center_y = TOP_LEFT_Y + (row + 0.5) * BLOCK_SIZE

        # At intersections (nearly centered), choose a new direction (but don’t reverse).
        if abs(self.x - cell_center_x) < 3 and abs(self.y - cell_center_y) < 3:
            possible_dirs = []
            for d in [(1,0), (-1,0), (0,1), (0,-1)]:
                if (d[0] == -self.dir[0] and d[1] == -self.dir[1]):
                    continue
                if can_move(row, col, d):
                    possible_dirs.append(d)
            if possible_dirs:
                self.dir = random.choice(possible_dirs)

        self.x += self.dir[0] * self.speed
        self.y += self.dir[1] * self.speed

    def draw(self, surface):
        draw_ghost(surface, int(self.x), int(self.y), self.radius, self.color)

# -------------------------------
# Screen Functions: Start & Restart
# -------------------------------

def show_start_screen():
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 48)
    text = font.render("Press any key to start", True, (255, 255, 255))
    screen.blit(text, ((SCREEN_WIDTH - text.get_width()) // 2,
                       (SCREEN_HEIGHT - text.get_height()) // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def show_restart_screen(result):
    """
    Display a screen showing "You Win!" if result is True, or "Game Over" otherwise.
    Wait for the player to press R to restart or Q to quit.
    """
    screen.fill((0, 0, 0))
    large_font = pygame.font.SysFont(None, 72)
    small_font = pygame.font.SysFont(None, 48)
    if result == "win":
        title_text = large_font.render("You Win!", True, (255, 255, 0))
    else:
        title_text = large_font.render("Game Over", True, (255, 0, 0))
    restart_text = small_font.render("Press R to restart or Q to quit", True, (255, 255, 255))
    screen.blit(title_text, ((SCREEN_WIDTH - title_text.get_width()) // 2,
                             (SCREEN_HEIGHT - title_text.get_height()) // 2 - 50))
    screen.blit(restart_text, ((SCREEN_WIDTH - restart_text.get_width()) // 2,
                               (SCREEN_HEIGHT - restart_text.get_height()) // 2 + 20))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    return False
        clock.tick(60)

# -------------------------------
# Main Game Loop Function
# -------------------------------

def run_game():
    # Initialize dots, Pac‑Man, and ghosts.
    dots = create_dots()
    # Start Pac‑Man at cell (5,2)
    pac_start_row, pac_start_col = 5, 2
    pacman = Pacman(TOP_LEFT_X + (pac_start_col + 0.5) * BLOCK_SIZE,
                    TOP_LEFT_Y + (pac_start_row + 0.5) * BLOCK_SIZE)
    if (pac_start_row, pac_start_col) in dots:
        dots.discard((pac_start_row, pac_start_col))
        
    # Create two ghosts at fixed locations.
    ghosts = []
    ghost1_row, ghost1_col = 5, 18
    ghost2_row, ghost2_col = 3, 10
    ghosts.append(Ghost(TOP_LEFT_X + (ghost1_col + 0.5) * BLOCK_SIZE,
                        TOP_LEFT_Y + (ghost1_row + 0.5) * BLOCK_SIZE, (255, 0, 0)))       # Red ghost
    ghosts.append(Ghost(TOP_LEFT_X + (ghost2_col + 0.5) * BLOCK_SIZE,
                        TOP_LEFT_Y + (ghost2_row + 0.5) * BLOCK_SIZE, (255, 184, 255)))   # Pink ghost
    # Remove dots where ghosts start.
    dots.discard((ghost1_row, ghost1_col))
    dots.discard((ghost2_row, ghost2_col))
    
    score = 0
    running = True
    win = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Update Pac‑Man’s desired direction.
                if event.key == pygame.K_UP:
                    pacman.desired_dir = (0, -1)
                elif event.key == pygame.K_DOWN:
                    pacman.desired_dir = (0, 1)
                elif event.key == pygame.K_LEFT:
                    pacman.desired_dir = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    pacman.desired_dir = (1, 0)

        pacman.update()
        for ghost in ghosts:
            ghost.update()

        # Check if Pac‑Man collects a dot.
        pac_row = int((pacman.y - TOP_LEFT_Y) // BLOCK_SIZE)
        pac_col = int((pacman.x - TOP_LEFT_X) // BLOCK_SIZE)
        if (pac_row, pac_col) in dots:
            dots.discard((pac_row, pac_col))
            score += 10

        # Check collision between Pac‑Man and ghosts.
        for ghost in ghosts:
            distance = math.hypot(pacman.x - ghost.x, pacman.y - ghost.y)
            if distance < pacman.radius + ghost.radius:
                running = False
                win = False
                break

        # Win condition: all dots eaten.
        if not dots:
            running = False
            win = True

        # -------------
        # Drawing Code
        # -------------
        screen.fill((0, 0, 0))
        # Draw maze walls.
        for r in range(ROWS):
            for c in range(COLS):
                if maze[r][c] == '#':
                    rect = pygame.Rect(TOP_LEFT_X + c * BLOCK_SIZE,
                                       TOP_LEFT_Y + r * BLOCK_SIZE,
                                       BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(screen, (0, 0, 255), rect)
        # Draw dots.
        for (r, c) in dots:
            center = (int(TOP_LEFT_X + c * BLOCK_SIZE + BLOCK_SIZE / 2),
                      int(TOP_LEFT_Y + r * BLOCK_SIZE + BLOCK_SIZE / 2))
            pygame.draw.circle(screen, (255, 255, 255), center, 3)
        # Draw Pac‑Man.
        pacman.draw(screen)
        # Draw ghosts.
        for ghost in ghosts:
            ghost.draw(screen)
        # Draw the score.
        font = pygame.font.SysFont(None, 36)
        score_text = font.render("Score: " + str(score), True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
        
    return "win" if win else "loss"

# -------------------------------
# Main Program Loop
# -------------------------------

def main():
    show_start_screen()
    restart = True
    while restart:
        result = run_game()  # Run one game session.
        restart = show_restart_screen(result)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()