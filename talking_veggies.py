import pygame
import random
import sys
from math import pi

# Initialize Pygame
pygame.init()

# Set up the display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Silly Veggies!")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
BUTTON_COLOR = (100, 200, 255)
BUTTON_HOVER_COLOR = (150, 220, 255)

# Game settings
GAME_DURATION = 90  # seconds
HIGH_SCORE_FILE = "high_scores.txt"

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'r') as file:
            return int(file.read().strip())
    except:
        return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, 'w') as file:
        file.write(str(score))

class Vegetable(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(['carrot', 'broccoli', 'tomato'])
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WINDOW_WIDTH - 60)
        self.rect.y = random.randint(0, WINDOW_HEIGHT - 60)
        self.draw_vegetable()
        self.messages = {
            'carrot': ["I'm crunchy!", "24 carrot gold!", "What's up, doc?"],
            'broccoli': ["I'm tree-rific!", "I'm super healthy!", "Broc and roll!"],
            'tomato': ["I'm juicy!", "Catch me if you can!", "I'm berry special!"]
        }
        self.message = random.choice(self.messages[self.type])
        self.font = pygame.font.Font(None, 24)

    def draw_vegetable(self):
        if self.type == 'carrot':
            # Draw carrot body (triangle pointing down)
            pygame.draw.polygon(self.image, ORANGE, [(30, 60), (10, 15), (50, 15)])
            # Draw carrot tops (multiple green leaves)
            for i in range(3):  # Draw 3 leaves
                leaf_x = 20 + i * 10
                # Draw wavy leaves
                points = [
                    (leaf_x, 15),  # base of leaf
                    (leaf_x - 5, 10),  # left curve
                    (leaf_x - 3, 5),   # left tip
                    (leaf_x, 0),       # middle tip
                    (leaf_x + 3, 5),   # right tip
                    (leaf_x + 5, 10),  # right curve
                ]
                pygame.draw.polygon(self.image, GREEN, points)
            
        elif self.type == 'broccoli':
            # Draw stem
            pygame.draw.rect(self.image, GREEN, (25, 30, 10, 30))
            # Draw broccoli top (circles for florets)
            for x in range(15, 45, 15):
                for y in range(0, 30, 15):
                    pygame.draw.circle(self.image, DARK_GREEN, (x, y), 12)
            
        else:  # tomato
            # Draw tomato body
            pygame.draw.circle(self.image, RED, (30, 30), 25)
            # Draw stem
            pygame.draw.rect(self.image, GREEN, (27, 0, 6, 10))

    def draw_message(self, screen):
        text = self.font.render(self.message, True, BLACK)
        screen.blit(text, (self.rect.x - 20, self.rect.y - 20))

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.is_hovered = False

    def draw(self, screen):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # border
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

def run_game():
    score = 0
    high_score = load_high_score()
    vegetables = pygame.sprite.Group()
    font = pygame.font.Font(None, 36)
    start_time = pygame.time.get_ticks()
    game_state = "playing"  # can be "playing" or "game_over"
    
    # Create start over button
    start_over_button = Button(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 + 100, 120, 40, "Start Over")

    # Create initial vegetables
    for _ in range(5):
        vegetables.add(Vegetable())

    # Game loop
    clock = pygame.time.Clock()
    running = True

    while running:
        if game_state == "playing":
            current_time = pygame.time.get_ticks()
            elapsed_seconds = (current_time - start_time) // 1000
            time_left = GAME_DURATION - elapsed_seconds

            if time_left <= 0:
                # Game over
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                game_state = "game_over"
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif game_state == "playing" and event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for veggie in vegetables:
                    if veggie.rect.collidepoint(pos):
                        veggie.kill()
                        score += 1
                        if len(vegetables) == 0:
                            vegetables.add(Vegetable())
            elif game_state == "game_over":
                if start_over_button.handle_event(event):
                    # Reset game
                    score = 0
                    vegetables.empty()
                    for _ in range(5):
                        vegetables.add(Vegetable())
                    start_time = pygame.time.get_ticks()
                    game_state = "playing"
                    continue

        # Draw everything
        screen.fill(WHITE)
        
        if game_state == "playing":
            # Draw score and timer
            score_text = font.render(f"Score: {score}", True, BLACK)
            high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
            timer_text = font.render(f"Time: {time_left}", True, BLACK)
            screen.blit(score_text, (10, 10))
            screen.blit(high_score_text, (10, 50))
            screen.blit(timer_text, (WINDOW_WIDTH - 150, 10))

            # Draw vegetables and their messages
            for veggie in vegetables:
                screen.blit(veggie.image, veggie.rect)
                veggie.draw_message(screen)
        else:  # game_over
            # Show final score
            game_over_text = font.render("Game Over!", True, BLACK)
            final_score_text = font.render(f"Final Score: {score}", True, BLACK)
            high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
            
            screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50))
            screen.blit(final_score_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2))
            screen.blit(high_score_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50))
            
            # Draw start over button
            start_over_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Start the game
if __name__ == "__main__":
    run_game()
