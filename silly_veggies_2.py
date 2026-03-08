#!/usr/bin/env python3
"""
Silly Veggies 2 - A bigger, sillier vegetable-chopping adventure!
Made with love for Isabella.
"""

import pygame
import random
import sys
import math
import json
import os
import struct
import array

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Silly Veggies 2!")

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CREAM = (255, 253, 208)
DARK_BROWN = (74, 55, 40)
SOFT_GREEN = (144, 238, 144)
TOMATO_RED = (255, 99, 71)
CARROT_ORANGE = (255, 165, 0)
GOLDEN = (255, 215, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (0, 100, 0)
FOREST_GREEN = (34, 139, 34)
PURPLE = (128, 0, 128)
LIGHT_PURPLE = (180, 100, 220)
YELLOW = (255, 230, 0)
BROWN = (139, 90, 43)
LIGHT_GREEN = (144, 238, 144)
PINK = (255, 182, 193)
SKY_BLUE = (135, 206, 235)
DEEP_BLUE = (25, 25, 112)
STAR_WHITE = (240, 240, 255)
RED = (255, 0, 0)
DARK_RED = (180, 0, 0)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
HIGH_SCORE_FILE = os.path.join(DATA_DIR, "high_scores.json")
ACHIEVEMENTS_FILE = os.path.join(DATA_DIR, "achievements.json")

# ---------------------------------------------------------------------------
# Sound generator  (programmatic – no external files needed)
# ---------------------------------------------------------------------------
SAMPLE_RATE = 44100


def _make_sound(samples_list):
    """Create a pygame Sound from a list of 16-bit integer samples (mono)."""
    buf = array.array("h", samples_list)
    stereo = array.array("h")
    for s in buf:
        stereo.append(s)
        stereo.append(s)
    sound = pygame.mixer.Sound(buffer=bytes(stereo))
    return sound


def generate_chop_sound():
    duration = 0.12
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = max(0.0, 1.0 - t / duration)
        val = env * random.uniform(-0.6, 0.6)
        samples.append(int(val * 32767))
    return _make_sound(samples)


def generate_powerup_sound():
    duration = 0.4
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 400 + 800 * (t / duration)
        env = max(0.0, 1.0 - t / duration) * 0.5
        val = env * math.sin(2 * math.pi * freq * t)
        samples.append(int(val * 32767))
    return _make_sound(samples)


def generate_achievement_sound():
    duration = 0.6
    n = int(SAMPLE_RATE * duration)
    samples = []
    freqs = [523, 659, 784]  # C5, E5, G5 – major chord arpeggio
    for i in range(n):
        t = i / SAMPLE_RATE
        idx = min(int(t / duration * 3), 2)
        freq = freqs[idx]
        env = max(0.0, 1.0 - (t % (duration / 3)) / (duration / 3)) * 0.4
        val = env * math.sin(2 * math.pi * freq * t)
        samples.append(int(val * 32767))
    return _make_sound(samples)


def generate_click_sound():
    duration = 0.05
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = max(0.0, 1.0 - t / duration)
        val = env * math.sin(2 * math.pi * 800 * t) * 0.3
        samples.append(int(val * 32767))
    return _make_sound(samples)


def generate_freeze_sound():
    duration = 0.3
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = max(0.0, 1.0 - t / duration) * 0.4
        val = env * math.sin(2 * math.pi * 1200 * t) * math.sin(2 * math.pi * 5 * t)
        samples.append(int(val * 32767))
    return _make_sound(samples)


def generate_combo_sound(pitch_mult=1.0):
    duration = 0.15
    n = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = max(0.0, 1.0 - t / duration) * 0.35
        val = env * math.sin(2 * math.pi * 660 * pitch_mult * t)
        samples.append(int(val * 32767))
    return _make_sound(samples)


# Pre-generate sounds
SFX = {}


def init_sounds():
    SFX["chop"] = [generate_chop_sound() for _ in range(3)]
    SFX["powerup"] = generate_powerup_sound()
    SFX["achievement"] = generate_achievement_sound()
    SFX["click"] = generate_click_sound()
    SFX["freeze"] = generate_freeze_sound()
    SFX["combo"] = [generate_combo_sound(1.0 + 0.15 * i) for i in range(10)]


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------
def load_high_scores():
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"easy": 0, "medium": 0, "hard": 0, "silly": 0}


def save_high_scores(scores):
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump(scores, f)


def load_achievements():
    try:
        with open(ACHIEVEMENTS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"unlocked": [], "stats": {"total_chops": 0, "carrots": 0,
                "broccoli": 0, "tomatoes": 0, "golden": 0, "max_combo": 0}}


def save_achievements(data):
    with open(ACHIEVEMENTS_FILE, "w") as f:
        json.dump(data, f)


# ---------------------------------------------------------------------------
# Achievement definitions
# ---------------------------------------------------------------------------
ACHIEVEMENT_DEFS = [
    {"id": "first_chop", "name": "First Chop!", "desc": "Chop your first veggie", "icon": "knife"},
    {"id": "veggie_hunter", "name": "Veggie Hunter", "desc": "Chop 100 total veggies", "icon": "target"},
    {"id": "speed_chopper", "name": "Speed Chopper", "desc": "Get a 5x combo", "icon": "lightning"},
    {"id": "carrot_king", "name": "Carrot King", "desc": "Chop 50 carrots", "icon": "crown"},
    {"id": "broccoli_boss", "name": "Broccoli Boss", "desc": "Chop 50 broccoli", "icon": "tree"},
    {"id": "tomato_terror", "name": "Tomato Terror", "desc": "Chop 50 tomatoes", "icon": "splat"},
    {"id": "golden_touch", "name": "Golden Touch", "desc": "Catch 10 golden veggies", "icon": "star"},
    {"id": "combo_master", "name": "Combo Master", "desc": "Get a 10x combo", "icon": "fire"},
    {"id": "high_scorer", "name": "High Scorer", "desc": "Score 100+ in one game", "icon": "trophy"},
    {"id": "silly_champion", "name": "Silly Champion", "desc": "Beat Silly Mode", "icon": "medal"},
]

# ---------------------------------------------------------------------------
# Difficulty presets
# ---------------------------------------------------------------------------
DIFFICULTIES = {
    "easy":   {"speed_mult": 0.5, "spawn_count": 5,  "duration": 120, "target": 30,  "label": "Easy"},
    "medium": {"speed_mult": 1.0, "spawn_count": 7,  "duration": 90,  "target": 50,  "label": "Medium"},
    "hard":   {"speed_mult": 1.5, "spawn_count": 10, "duration": 60,  "target": 75,  "label": "Hard"},
    "silly":  {"speed_mult": 2.2, "spawn_count": 15, "duration": 45,  "target": 100, "label": "Silly!"},
}

# ---------------------------------------------------------------------------
# Vegetable definitions
# ---------------------------------------------------------------------------
VEGGIE_TYPES = {
    "carrot":      {"points": 1, "move": "bouncy",  "color": CARROT_ORANGE,
                    "messages": ["I'm crunchy!", "24 carrot gold!", "What's up, doc?",
                                 "Orange you glad?", "Root for me!"]},
    "broccoli":    {"points": 1, "move": "floaty",  "color": FOREST_GREEN,
                    "messages": ["I'm tree-rific!", "I'm super healthy!", "Broc and roll!",
                                 "I've got florets!", "Eat your greens!"]},
    "tomato":      {"points": 1, "move": "bouncy",  "color": TOMATO_RED,
                    "messages": ["I'm juicy!", "Catch me if you can!", "I'm berry special!",
                                 "Ketchup to me!", "I'm vine!"]},
    "corn":        {"points": 2, "move": "spinner", "color": YELLOW,
                    "messages": ["I'm a-maize-ing!", "Corny joke time!", "Pop pop pop!",
                                 "Ear ear!", "Shucks!"]},
    "eggplant":    {"points": 2, "move": "floaty",  "color": PURPLE,
                    "messages": ["I'm egg-cellent!", "So mysterious...", "Purple power!",
                                 "Auber-genius!", "I'm fancy!"]},
    "bell_pepper": {"points": 2, "move": "zippy",   "color": RED,
                    "messages": ["Ring ring!", "I'm bell-issimo!", "Pepper power!",
                                 "Can't catch me!", "So colourful!"]},
    "onion":       {"points": 1, "move": "bouncy",  "color": BROWN,
                    "messages": ["Don't cry!", "I've got layers!", "Peel the love!",
                                 "Tear-ific!", "I make you cry!"]},
    "peas":        {"points": 3, "move": "zippy",   "color": LIGHT_GREEN,
                    "messages": ["Peas out!", "Give peas a chance!", "We're a team!",
                                 "Peas and quiet!", "Unbe-pea-vable!"]},
}

# ---------------------------------------------------------------------------
# Particle system
# ---------------------------------------------------------------------------
class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size")

    def __init__(self, x, y, color, speed=3.0, life=0.5, size=4):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        spd = random.uniform(speed * 0.5, speed * 1.5)
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size

    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += 0.15 * dt * 60  # gravity
        self.life -= dt

    def draw(self, surface):
        alpha = max(0, self.life / self.max_life)
        r = max(1, int(self.size * alpha))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)


class FloatingText:
    __slots__ = ("x", "y", "text", "color", "life", "max_life", "font")

    def __init__(self, x, y, text, color=GOLDEN, life=0.8):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = life
        self.max_life = life
        self.font = pygame.font.Font(None, 32)

    def update(self, dt):
        self.y -= 60 * dt
        self.life -= dt

    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            txt = self.font.render(self.text, True, self.color)
            surface.blit(txt, (int(self.x), int(self.y)))


# ---------------------------------------------------------------------------
# Vegetable sprite
# ---------------------------------------------------------------------------
class Vegetable(pygame.sprite.Sprite):
    BASE_SIZE = 60

    def __init__(self, vtype, speed_mult=1.0, is_golden=False):
        super().__init__()
        self.vtype = vtype
        self.info = VEGGIE_TYPES[vtype]
        self.is_golden = is_golden
        self.points = self.info["points"] * (5 if is_golden else 1)
        self.move_style = self.info["move"]
        self.size = self.BASE_SIZE
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        # Random spawn position (inside play area)
        margin = 80
        self.rect.x = random.randint(margin, WINDOW_WIDTH - self.size - margin)
        self.rect.y = random.randint(margin, WINDOW_HEIGHT - self.size - margin)
        self.float_x = float(self.rect.x)
        self.float_y = float(self.rect.y)

        # Movement
        base_speed = {"bouncy": 2.0, "floaty": 1.0, "zippy": 3.5, "spinner": 1.8}
        spd = base_speed[self.move_style] * speed_mult
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.rotation = 0
        self.rotation_speed = random.choice([-1, 1]) * random.uniform(1, 3) if self.move_style == "spinner" else 0
        self.wobble_phase = random.uniform(0, 2 * math.pi)
        self.wobble_speed = random.uniform(2, 4)

        # Message
        self.message = random.choice(self.info["messages"])
        self.msg_font = pygame.font.Font(None, 22)
        self.show_message_timer = 0
        self.message_visible = True

        # Frozen state
        self.frozen = False

        self._draw_veggie()

    def _draw_veggie(self):
        self.image.fill((0, 0, 0, 0))
        s = self.size
        c = self.info["color"]

        if self.is_golden:
            # Draw golden glow
            pygame.draw.circle(self.image, (*GOLDEN, 60), (s // 2, s // 2), s // 2)

        if self.vtype == "carrot":
            pygame.draw.polygon(self.image, c, [(s // 2, s - 2), (s // 5, s // 4), (4 * s // 5, s // 4)])
            for i in range(3):
                lx = s // 4 + i * s // 5
                pts = [(lx, s // 4), (lx - 4, s // 7), (lx - 2, 2), (lx, 0), (lx + 2, 2), (lx + 4, s // 7)]
                pygame.draw.polygon(self.image, FOREST_GREEN, pts)

        elif self.vtype == "broccoli":
            pygame.draw.rect(self.image, FOREST_GREEN, (s // 2 - 5, s // 2, 10, s // 2))
            for x in range(s // 5, 4 * s // 5, s // 5):
                for y in range(s // 8, s // 2, s // 5):
                    pygame.draw.circle(self.image, DARK_GREEN, (x, y), s // 7)

        elif self.vtype == "tomato":
            pygame.draw.circle(self.image, c, (s // 2, s // 2), s // 2 - 3)
            pygame.draw.circle(self.image, (255, 130, 100), (s // 2 - 5, s // 2 - 5), s // 5)
            pygame.draw.rect(self.image, FOREST_GREEN, (s // 2 - 3, 0, 6, s // 5))
            # Small leaf
            pygame.draw.ellipse(self.image, FOREST_GREEN, (s // 2 - 10, 2, 12, 6))

        elif self.vtype == "corn":
            # Cob body
            pygame.draw.ellipse(self.image, YELLOW, (s // 4, s // 6, s // 2, 2 * s // 3))
            # Kernels
            for row in range(4):
                for col in range(3):
                    kx = s // 4 + 6 + col * (s // 7)
                    ky = s // 5 + 4 + row * (s // 6)
                    pygame.draw.circle(self.image, (230, 200, 0), (kx, ky), 3)
            # Husk
            pygame.draw.polygon(self.image, FOREST_GREEN,
                                [(s // 3, 2 * s // 3), (s // 6, s), (s // 3 - 3, s)])
            pygame.draw.polygon(self.image, FOREST_GREEN,
                                [(2 * s // 3, 2 * s // 3), (5 * s // 6, s), (2 * s // 3 + 3, s)])

        elif self.vtype == "eggplant":
            pygame.draw.ellipse(self.image, PURPLE, (s // 5, s // 5, 3 * s // 5, 3 * s // 4))
            pygame.draw.ellipse(self.image, LIGHT_PURPLE, (s // 3, s // 3, s // 6, s // 4))
            # Stem cap
            pygame.draw.polygon(self.image, FOREST_GREEN,
                                [(s // 3, s // 5), (s // 2, 0), (2 * s // 3, s // 5)])

        elif self.vtype == "bell_pepper":
            # Body - wider at top
            pygame.draw.ellipse(self.image, c, (s // 6, s // 4, 2 * s // 3, 2 * s // 3))
            # Bumps at bottom
            for bx in [s // 3, s // 2, 2 * s // 3]:
                pygame.draw.circle(self.image, c, (bx, 5 * s // 6), s // 8)
            # Stem
            pygame.draw.rect(self.image, FOREST_GREEN, (s // 2 - 3, s // 10, 6, s // 5))
            # Highlight
            pygame.draw.ellipse(self.image, (255, 100, 100), (s // 3, s // 3, s // 8, s // 5))

        elif self.vtype == "onion":
            pygame.draw.circle(self.image, (210, 180, 140), (s // 2, s // 2 + 4), s // 2 - 5)
            pygame.draw.circle(self.image, (230, 210, 170), (s // 2, s // 2 + 4), s // 3)
            # Root tufts
            pygame.draw.line(self.image, BROWN, (s // 2 - 3, 5), (s // 2 - 6, 0), 2)
            pygame.draw.line(self.image, BROWN, (s // 2, 5), (s // 2, 0), 2)
            pygame.draw.line(self.image, BROWN, (s // 2 + 3, 5), (s // 2 + 6, 0), 2)

        elif self.vtype == "peas":
            # Pod
            pygame.draw.ellipse(self.image, FOREST_GREEN, (2, s // 4, s - 4, s // 2))
            # Peas inside
            for i in range(3):
                px = s // 4 + i * s // 4
                pygame.draw.circle(self.image, LIGHT_GREEN, (px, s // 2), s // 8)
                pygame.draw.circle(self.image, (170, 255, 170), (px - 2, s // 2 - 2), s // 16)

        if self.is_golden:
            # Golden overlay shimmer
            overlay = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.circle(overlay, (*GOLDEN, 40), (s // 2, s // 2), s // 2 - 2)
            self.image.blit(overlay, (0, 0))

    def update(self, dt):
        if self.frozen:
            self.wobble_phase += self.wobble_speed * dt
            return

        margin = 10
        # Movement
        self.float_x += self.vx * dt * 60
        self.float_y += self.vy * dt * 60

        # Bounce off walls
        if self.float_x < margin:
            self.float_x = margin
            self.vx = abs(self.vx)
        elif self.float_x > WINDOW_WIDTH - self.size - margin:
            self.float_x = WINDOW_WIDTH - self.size - margin
            self.vx = -abs(self.vx)
        if self.float_y < margin:
            self.float_y = margin
            self.vy = abs(self.vy)
        elif self.float_y > WINDOW_HEIGHT - self.size - margin:
            self.float_y = WINDOW_HEIGHT - self.size - margin
            self.vy = -abs(self.vy)

        # Style-specific updates
        if self.move_style == "floaty":
            self.wobble_phase += self.wobble_speed * dt
            self.float_y += math.sin(self.wobble_phase) * 0.5

        elif self.move_style == "zippy":
            if random.random() < 0.02:
                angle = random.uniform(0, 2 * math.pi)
                spd = math.hypot(self.vx, self.vy)
                self.vx = math.cos(angle) * spd
                self.vy = math.sin(angle) * spd

        elif self.move_style == "spinner":
            self.rotation += self.rotation_speed * dt * 60

        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)

        # Wobble animation (idle wiggle)
        self.wobble_phase += self.wobble_speed * dt

        # Message timer
        self.show_message_timer += dt
        if self.show_message_timer > 3:
            self.message = random.choice(self.info["messages"])
            self.show_message_timer = 0

    def draw(self, surface):
        # Wobble effect
        wobble = math.sin(self.wobble_phase * 3) * 2
        draw_x = self.rect.x + wobble
        draw_y = self.rect.y

        if self.move_style == "spinner" and abs(self.rotation) > 0.01:
            rotated = pygame.transform.rotate(self.image, self.rotation)
            r = rotated.get_rect(center=(draw_x + self.size // 2, draw_y + self.size // 2))
            surface.blit(rotated, r.topleft)
        else:
            surface.blit(self.image, (draw_x, draw_y))

        # Frozen overlay
        if self.frozen:
            ice = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(ice, (200, 230, 255, 100), (self.size // 2, self.size // 2), self.size // 2)
            surface.blit(ice, (draw_x, draw_y))

        # Message bubble
        txt_surf = self.msg_font.render(self.message, True, DARK_BROWN)
        tx = draw_x + self.size // 2 - txt_surf.get_width() // 2
        ty = draw_y - 22
        # Background for text readability
        bg = pygame.Surface((txt_surf.get_width() + 8, txt_surf.get_height() + 4), pygame.SRCALPHA)
        bg.fill((*CREAM, 180))
        surface.blit(bg, (tx - 4, ty - 2))
        surface.blit(txt_surf, (tx, ty))


# ---------------------------------------------------------------------------
# Power-up sprite
# ---------------------------------------------------------------------------
POWERUP_TYPES = {
    "double_points": {"color": GOLDEN, "symbol": "x2", "duration": 10, "desc": "Double Points!"},
    "slow_mo":       {"color": LIGHT_BLUE, "symbol": "SLO", "duration": 5, "desc": "Slow Motion!"},
    "freeze":        {"color": (200, 230, 255), "symbol": "ICE", "duration": 3, "desc": "Freeze!"},
    "magnet":        {"color": PINK, "symbol": "MAG", "duration": 5, "desc": "Veggie Magnet!"},
}


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.ptype = random.choice(list(POWERUP_TYPES.keys()))
        self.info = POWERUP_TYPES[self.ptype]
        self.size = 40
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.life = 5.0  # disappears after 5 seconds
        self.pulse = 0
        self._draw()

    def _draw(self):
        self.image.fill((0, 0, 0, 0))
        c = self.info["color"]
        pygame.draw.circle(self.image, (*c, 200), (self.size // 2, self.size // 2), self.size // 2 - 2)
        pygame.draw.circle(self.image, WHITE, (self.size // 2, self.size // 2), self.size // 2 - 2, 2)
        font = pygame.font.Font(None, 20)
        txt = font.render(self.info["symbol"], True, DARK_BROWN)
        self.image.blit(txt, txt.get_rect(center=(self.size // 2, self.size // 2)))

    def update(self, dt):
        self.life -= dt
        self.pulse += dt * 4
        if self.life <= 0:
            self.kill()

    def draw(self, surface):
        scale = 1.0 + 0.1 * math.sin(self.pulse)
        sz = int(self.size * scale)
        scaled = pygame.transform.scale(self.image, (sz, sz))
        r = scaled.get_rect(center=self.rect.center)
        surface.blit(scaled, r.topleft)


# ---------------------------------------------------------------------------
# Level backgrounds
# ---------------------------------------------------------------------------
def draw_garden_bg(surface):
    """Green garden with sky."""
    surface.fill(SKY_BLUE)
    # Grass
    pygame.draw.rect(surface, SOFT_GREEN, (0, WINDOW_HEIGHT * 2 // 3, WINDOW_WIDTH, WINDOW_HEIGHT // 3))
    pygame.draw.rect(surface, FOREST_GREEN, (0, WINDOW_HEIGHT * 2 // 3, WINDOW_WIDTH, 4))
    # Sun
    pygame.draw.circle(surface, YELLOW, (WINDOW_WIDTH - 80, 70), 45)
    # Clouds
    for cx, cy in [(150, 60), (400, 90), (650, 50)]:
        for dx in range(-20, 30, 15):
            pygame.draw.circle(surface, WHITE, (cx + dx, cy), 20)
    # Flowers
    for fx in range(50, WINDOW_WIDTH, 120):
        fy = WINDOW_HEIGHT - 60
        pygame.draw.line(surface, DARK_GREEN, (fx, fy + 40), (fx, fy), 2)
        for angle in range(0, 360, 72):
            px = fx + int(6 * math.cos(math.radians(angle)))
            py = fy + int(6 * math.sin(math.radians(angle)))
            pygame.draw.circle(surface, PINK, (px, py), 5)
        pygame.draw.circle(surface, YELLOW, (fx, fy), 4)


def draw_kitchen_bg(surface):
    """Kitchen counter-top."""
    surface.fill((240, 230, 210))
    # Counter
    pygame.draw.rect(surface, (180, 140, 100), (0, WINDOW_HEIGHT - 120, WINDOW_WIDTH, 120))
    pygame.draw.line(surface, DARK_BROWN, (0, WINDOW_HEIGHT - 120), (WINDOW_WIDTH, WINDOW_HEIGHT - 120), 3)
    # Tiles
    tile_size = 60
    for tx in range(0, WINDOW_WIDTH, tile_size):
        for ty in range(0, WINDOW_HEIGHT - 120, tile_size):
            color = (235, 225, 205) if (tx // tile_size + ty // tile_size) % 2 == 0 else (225, 215, 195)
            pygame.draw.rect(surface, color, (tx, ty, tile_size, tile_size))
            pygame.draw.rect(surface, (200, 190, 170), (tx, ty, tile_size, tile_size), 1)
    # Utensils on wall
    pygame.draw.circle(surface, (160, 160, 170), (WINDOW_WIDTH - 60, 40), 20, 3)
    pygame.draw.line(surface, (160, 160, 170), (WINDOW_WIDTH - 60, 60), (WINDOW_WIDTH - 60, 100), 3)


def draw_farm_bg(surface):
    """Barn and fields."""
    surface.fill(SKY_BLUE)
    # Rolling hills
    pts = [(0, WINDOW_HEIGHT)]
    for x in range(0, WINDOW_WIDTH + 20, 20):
        y = WINDOW_HEIGHT // 2 + int(30 * math.sin(x * 0.015)) + 80
        pts.append((x, y))
    pts.append((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.draw.polygon(surface, (100, 180, 80), pts)
    # Furrows
    for fy in range(WINDOW_HEIGHT // 2 + 80, WINDOW_HEIGHT, 30):
        pygame.draw.line(surface, (80, 150, 60), (0, fy), (WINDOW_WIDTH, fy), 1)
    # Barn
    bx, by = 60, WINDOW_HEIGHT // 2 + 20
    pygame.draw.rect(surface, (180, 50, 40), (bx, by, 100, 80))
    pygame.draw.polygon(surface, (140, 30, 20), [(bx - 10, by), (bx + 50, by - 50), (bx + 110, by)])
    pygame.draw.rect(surface, BROWN, (bx + 35, by + 30, 30, 50))
    # Sun
    pygame.draw.circle(surface, YELLOW, (WINDOW_WIDTH - 80, 60), 40)


def draw_space_bg(surface):
    """Vegetables in space!"""
    surface.fill((10, 5, 30))
    random.seed(42)  # consistent star field
    for _ in range(120):
        sx = random.randint(0, WINDOW_WIDTH)
        sy = random.randint(0, WINDOW_HEIGHT)
        brightness = random.randint(150, 255)
        pygame.draw.circle(surface, (brightness, brightness, brightness + 5), (sx, sy),
                           random.choice([1, 1, 1, 2]))
    random.seed()  # restore random state
    # Planet
    pygame.draw.circle(surface, (60, 80, 160), (WINDOW_WIDTH - 120, WINDOW_HEIGHT - 100), 70)
    pygame.draw.ellipse(surface, (100, 120, 200), (WINDOW_WIDTH - 220, WINDOW_HEIGHT - 115, 200, 30), 2)
    # Moon
    pygame.draw.circle(surface, (200, 200, 210), (100, 80), 30)
    pygame.draw.circle(surface, (180, 180, 190), (92, 75), 8)
    pygame.draw.circle(surface, (180, 180, 190), (112, 88), 5)


LEVELS = [
    {"name": "Garden", "draw_bg": draw_garden_bg, "text_color": DARK_BROWN},
    {"name": "Kitchen", "draw_bg": draw_kitchen_bg, "text_color": DARK_BROWN},
    {"name": "Farm", "draw_bg": draw_farm_bg, "text_color": DARK_BROWN},
    {"name": "Space", "draw_bg": draw_space_bg, "text_color": WHITE},
]

# ---------------------------------------------------------------------------
# UI Components
# ---------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, width, height, text, color=TOMATO_RED, hover_color=None, font_size=30, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color or tuple(min(c + 40, 255) for c in color)
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        self.visible = True

    def draw(self, surface):
        if not self.visible:
            return
        c = self.hover_color if self.is_hovered else self.color
        # Rounded rectangle via surface
        pygame.draw.rect(surface, c, self.rect, border_radius=12)
        pygame.draw.rect(surface, DARK_BROWN, self.rect, 2, border_radius=12)
        txt = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# ---------------------------------------------------------------------------
# Main Game class
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.state = "menu"  # menu, difficulty, playing, paused, game_over, achievements
        self.difficulty = "medium"
        self.score = 0
        self.high_scores = load_high_scores()
        self.ach_data = load_achievements()
        self.vegetables = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.particles = []
        self.floating_texts = []
        self.combo = 0
        self.combo_timer = 0
        self.last_chop_time = 0
        self.active_effects = {}  # effect_name: time_remaining
        self.level_index = 0
        self.session_score = 0
        self.session_chops = {k: 0 for k in VEGGIE_TYPES}
        self.new_achievements = []
        self.ach_display_timer = 0
        self.sound_enabled = True
        self.time_left = 0
        self.start_time = 0
        self.shake_timer = 0
        self.shake_intensity = 0
        self.title_wobble = 0

        # Fonts
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)
        self.font_tiny = pygame.font.Font(None, 22)

        # Menu buttons
        cx = WINDOW_WIDTH // 2
        self.btn_play = Button(cx - 100, 320, 200, 50, "Play!", TOMATO_RED)
        self.btn_achievements = Button(cx - 100, 390, 200, 50, "Achievements", CARROT_ORANGE)
        self.btn_sound = Button(cx - 100, 460, 200, 50, "Sound: ON", FOREST_GREEN)
        self.btn_quit = Button(cx - 100, 530, 200, 50, "Quit", (150, 150, 150))

        # Difficulty buttons
        self.diff_buttons = {}
        colors = {"easy": FOREST_GREEN, "medium": CARROT_ORANGE, "hard": TOMATO_RED, "silly": PURPLE}
        for i, (key, diff) in enumerate(DIFFICULTIES.items()):
            self.diff_buttons[key] = Button(cx - 120, 220 + i * 70, 240, 55,
                                            f"{diff['label']}  ({diff['duration']}s)", colors[key])
        self.btn_back = Button(cx - 80, 520, 160, 45, "Back", (150, 150, 150))

        # Game-over buttons
        self.btn_restart = Button(cx - 110, 460, 100, 45, "Retry", TOMATO_RED, font_size=26)
        self.btn_menu = Button(cx + 10, 460, 100, 45, "Menu", CARROT_ORANGE, font_size=26)

        # Pause buttons
        self.btn_resume = Button(cx - 100, 300, 200, 50, "Resume", FOREST_GREEN)
        self.btn_pause_menu = Button(cx - 100, 370, 200, 50, "Main Menu", CARROT_ORANGE)

        # Achievements back button
        self.btn_ach_back = Button(cx - 80, WINDOW_HEIGHT - 70, 160, 45, "Back", (150, 150, 150))

        # Title menu veggies (decorative)
        self.menu_veggies = []
        for _ in range(8):
            vtype = random.choice(list(VEGGIE_TYPES.keys()))
            v = Vegetable(vtype, speed_mult=0.4)
            self.menu_veggies.append(v)

    def play_sound(self, name, index=None):
        if not self.sound_enabled:
            return
        snd = SFX.get(name)
        if snd is None:
            return
        if isinstance(snd, list):
            if index is not None and index < len(snd):
                snd[index].play()
            else:
                random.choice(snd).play()
        else:
            snd.play()

    # --- State transitions ---
    def start_game(self):
        diff = DIFFICULTIES[self.difficulty]
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.active_effects = {}
        self.vegetables.empty()
        self.powerups.empty()
        self.particles.clear()
        self.floating_texts.clear()
        self.session_chops = {k: 0 for k in VEGGIE_TYPES}
        self.session_score = 0
        self.level_index = 0
        self.time_left = diff["duration"]
        self.start_time = pygame.time.get_ticks()
        self.new_achievements.clear()

        speed = diff["speed_mult"]
        for _ in range(diff["spawn_count"]):
            vtype = random.choice(list(VEGGIE_TYPES.keys()))
            is_golden = random.random() < 0.03
            self.vegetables.add(Vegetable(vtype, speed, is_golden))
        self.state = "playing"

    # --- Achievement checks ---
    def check_achievements(self):
        stats = self.ach_data["stats"]
        unlocked = self.ach_data["unlocked"]
        new = []

        checks = [
            ("first_chop", stats["total_chops"] >= 1),
            ("veggie_hunter", stats["total_chops"] >= 100),
            ("speed_chopper", stats["max_combo"] >= 5),
            ("carrot_king", stats["carrots"] >= 50),
            ("broccoli_boss", stats["broccoli"] >= 50),
            ("tomato_terror", stats["tomatoes"] >= 50),
            ("golden_touch", stats["golden"] >= 10),
            ("combo_master", stats["max_combo"] >= 10),
            ("high_scorer", self.session_score >= 100),
            ("silly_champion", self.difficulty == "silly" and self.session_score >= 100),
        ]
        for aid, condition in checks:
            if aid not in unlocked and condition:
                unlocked.append(aid)
                new.append(aid)

        if new:
            self.ach_data["unlocked"] = unlocked
            save_achievements(self.ach_data)
            for a in new:
                name = next(d["name"] for d in ACHIEVEMENT_DEFS if d["id"] == a)
                self.new_achievements.append(name)
                self.ach_display_timer = 3.0
            self.play_sound("achievement")

    # --- Chop a veggie ---
    def chop_veggie(self, veggie):
        cx = veggie.rect.centerx
        cy = veggie.rect.centery
        pts = veggie.points
        if "double_points" in self.active_effects:
            pts *= 2

        # Combo system
        now = pygame.time.get_ticks() / 1000.0
        if now - self.last_chop_time < 1.0:
            self.combo += 1
        else:
            self.combo = 1
        self.last_chop_time = now
        self.combo_timer = 1.5

        if self.combo >= 3:
            pts += self.combo
            combo_idx = min(self.combo - 1, len(SFX.get("combo", [])) - 1)
            self.play_sound("combo", combo_idx)

        self.score += pts
        self.session_score = self.score

        # Particles
        color = veggie.info["color"]
        for _ in range(12):
            self.particles.append(Particle(cx, cy, color, speed=4, life=0.6, size=5))
        if veggie.is_golden:
            for _ in range(8):
                self.particles.append(Particle(cx, cy, GOLDEN, speed=5, life=0.8, size=6))

        # Floating text
        txt = f"+{pts}"
        if self.combo >= 3:
            txt += f"  x{self.combo}!"
        self.floating_texts.append(FloatingText(cx - 10, cy - 20, txt))

        # Stats
        self.ach_data["stats"]["total_chops"] += 1
        vtype = veggie.vtype
        if vtype == "carrot":
            self.ach_data["stats"]["carrots"] += 1
        elif vtype == "broccoli":
            self.ach_data["stats"]["broccoli"] += 1
        elif vtype == "tomato":
            self.ach_data["stats"]["tomatoes"] += 1
        if veggie.is_golden:
            self.ach_data["stats"]["golden"] += 1
        self.ach_data["stats"]["max_combo"] = max(self.ach_data["stats"]["max_combo"], self.combo)
        self.session_chops[vtype] = self.session_chops.get(vtype, 0) + 1

        self.play_sound("chop")
        veggie.kill()

        # Maybe spawn power-up
        if random.random() < 0.10:
            self.powerups.add(PowerUp(cx, cy))

        # Respawn veggie
        diff = DIFFICULTIES[self.difficulty]
        new_type = random.choice(list(VEGGIE_TYPES.keys()))
        is_golden = random.random() < 0.04
        self.vegetables.add(Vegetable(new_type, diff["speed_mult"], is_golden))

        self.check_achievements()

    # --- Activate power-up ---
    def activate_powerup(self, pu):
        self.active_effects[pu.ptype] = pu.info["duration"]
        self.floating_texts.append(FloatingText(pu.rect.centerx - 40, pu.rect.centery - 30,
                                                pu.info["desc"], GOLDEN, life=1.5))
        self.shake_timer = 0.3
        self.shake_intensity = 5
        if pu.ptype == "freeze":
            for v in self.vegetables:
                v.frozen = True
            self.play_sound("freeze")
        elif pu.ptype == "slow_mo":
            for v in self.vegetables:
                v.vx *= 0.3
                v.vy *= 0.3
        else:
            self.play_sound("powerup")
        pu.kill()

    # --- Level progression based on score ---
    def update_level(self):
        if self.score >= 75:
            self.level_index = 3
        elif self.score >= 50:
            self.level_index = 2
        elif self.score >= 25:
            self.level_index = 1
        else:
            self.level_index = 0

    # --- Main update ---
    def update(self, dt):
        if self.state == "menu":
            self.title_wobble += dt * 2
            for v in self.menu_veggies:
                v.update(dt)

        elif self.state == "playing":
            # Timer
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
            self.time_left = max(0, DIFFICULTIES[self.difficulty]["duration"] - elapsed)
            if self.time_left <= 0:
                self.end_game()
                return

            # Effect timers
            expired = []
            for eff, remaining in self.active_effects.items():
                self.active_effects[eff] = remaining - dt
                if self.active_effects[eff] <= 0:
                    expired.append(eff)
            for eff in expired:
                del self.active_effects[eff]
                if eff == "freeze":
                    for v in self.vegetables:
                        v.frozen = False
                elif eff == "slow_mo":
                    for v in self.vegetables:
                        v.vx /= 0.3
                        v.vy /= 0.3

            # Magnet effect
            if "magnet" in self.active_effects:
                mx, my = pygame.mouse.get_pos()
                for v in self.vegetables:
                    dx = mx - v.float_x
                    dy = my - v.float_y
                    dist = max(1, math.hypot(dx, dy))
                    force = 3.0
                    v.float_x += (dx / dist) * force
                    v.float_y += (dy / dist) * force

            # Update entities
            for v in self.vegetables:
                v.update(dt)
            self.powerups.update(dt)

            # Particles
            for p in self.particles:
                p.update(dt)
            self.particles = [p for p in self.particles if p.life > 0]

            # Floating text
            for ft in self.floating_texts:
                ft.update(dt)
            self.floating_texts = [ft for ft in self.floating_texts if ft.life > 0]

            # Combo timer
            if self.combo_timer > 0:
                self.combo_timer -= dt
                if self.combo_timer <= 0:
                    self.combo = 0

            # Shake
            if self.shake_timer > 0:
                self.shake_timer -= dt

            # Level progression
            self.update_level()

        # Achievement display timer
        if self.ach_display_timer > 0:
            self.ach_display_timer -= dt
            if self.ach_display_timer <= 0:
                self.new_achievements.clear()

    def end_game(self):
        # Save high score
        key = self.difficulty
        if self.score > self.high_scores.get(key, 0):
            self.high_scores[key] = self.score
            save_high_scores(self.high_scores)
        save_achievements(self.ach_data)
        self.check_achievements()
        self.state = "game_over"

    # --- Event handling ---
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.state == "menu":
                if self.btn_play.handle_event(event):
                    self.play_sound("click")
                    self.state = "difficulty"
                elif self.btn_achievements.handle_event(event):
                    self.play_sound("click")
                    self.state = "achievements"
                elif self.btn_sound.handle_event(event):
                    self.sound_enabled = not self.sound_enabled
                    self.btn_sound.text = f"Sound: {'ON' if self.sound_enabled else 'OFF'}"
                    self.play_sound("click")
                elif self.btn_quit.handle_event(event):
                    return False

            elif self.state == "difficulty":
                for key, btn in self.diff_buttons.items():
                    if btn.handle_event(event):
                        self.play_sound("click")
                        self.difficulty = key
                        self.start_game()
                        break
                if self.btn_back.handle_event(event):
                    self.play_sound("click")
                    self.state = "menu"

            elif self.state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "paused"
                    elif event.key == pygame.K_m:
                        self.sound_enabled = not self.sound_enabled
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    # Check power-ups first
                    for pu in self.powerups:
                        if pu.rect.collidepoint(pos):
                            self.activate_powerup(pu)
                            break
                    else:
                        # Check veggies
                        for v in self.vegetables:
                            if v.rect.collidepoint(pos):
                                self.chop_veggie(v)
                                break

            elif self.state == "paused":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = "playing"
                if self.btn_resume.handle_event(event):
                    self.play_sound("click")
                    self.state = "playing"
                    # Adjust start time to account for pause
                elif self.btn_pause_menu.handle_event(event):
                    self.play_sound("click")
                    self.state = "menu"

            elif self.state == "game_over":
                if self.btn_restart.handle_event(event):
                    self.play_sound("click")
                    self.start_game()
                elif self.btn_menu.handle_event(event):
                    self.play_sound("click")
                    self.state = "menu"

            elif self.state == "achievements":
                if self.btn_ach_back.handle_event(event):
                    self.play_sound("click")
                    self.state = "menu"

        return True

    # --- Drawing ---
    def draw(self):
        # Screen shake offset
        ox, oy = 0, 0
        if self.shake_timer > 0:
            ox = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            oy = random.randint(-int(self.shake_intensity), int(self.shake_intensity))

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "difficulty":
            self.draw_difficulty()
        elif self.state == "playing":
            self.draw_playing(ox, oy)
        elif self.state == "paused":
            self.draw_playing(0, 0)
            self.draw_pause_overlay()
        elif self.state == "game_over":
            self.draw_game_over()
        elif self.state == "achievements":
            self.draw_achievements()

        # Achievement notification (overlays any state)
        if self.new_achievements and self.ach_display_timer > 0:
            self.draw_achievement_popup()

        pygame.display.flip()

    def draw_menu(self):
        draw_garden_bg(screen)

        # Decorative veggies
        for v in self.menu_veggies:
            v.draw(screen)

        # Title with wobble
        title_y = 100 + math.sin(self.title_wobble) * 8
        title = self.font_large.render("Silly Veggies 2!", True, DARK_BROWN)
        shadow = self.font_large.render("Silly Veggies 2!", True, (100, 70, 50))
        screen.blit(shadow, shadow.get_rect(center=(WINDOW_WIDTH // 2 + 3, title_y + 3)))
        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, title_y)))

        subtitle = self.font_small.render("A bigger, sillier adventure!", True, DARK_BROWN)
        screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, title_y + 50)))

        # High score
        best = max(self.high_scores.values()) if self.high_scores else 0
        if best > 0:
            hs_text = self.font_tiny.render(f"Best Score: {best}", True, DARK_BROWN)
            screen.blit(hs_text, hs_text.get_rect(center=(WINDOW_WIDTH // 2, 280)))

        self.btn_play.draw(screen)
        self.btn_achievements.draw(screen)
        self.btn_sound.draw(screen)
        self.btn_quit.draw(screen)

        # Credits
        credit = self.font_tiny.render("Made with love for Isabella!", True, DARK_BROWN)
        screen.blit(credit, credit.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)))

    def draw_difficulty(self):
        draw_garden_bg(screen)
        title = self.font_large.render("Choose Difficulty", True, DARK_BROWN)
        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 100)))

        desc = self.font_small.render("How silly do you want it?", True, DARK_BROWN)
        screen.blit(desc, desc.get_rect(center=(WINDOW_WIDTH // 2, 160)))

        for key, btn in self.diff_buttons.items():
            btn.draw(screen)
            # Show high score next to button
            hs = self.high_scores.get(key, 0)
            if hs > 0:
                hs_txt = self.font_tiny.render(f"Best: {hs}", True, DARK_BROWN)
                screen.blit(hs_txt, (btn.rect.right + 15, btn.rect.centery - 8))

        self.btn_back.draw(screen)

    def draw_playing(self, ox, oy):
        # Background
        level = LEVELS[self.level_index]
        level["draw_bg"](screen)
        text_color = level["text_color"]

        # Level name (subtle)
        ln = self.font_tiny.render(level["name"], True, text_color)
        screen.blit(ln, (WINDOW_WIDTH - ln.get_width() - 10, WINDOW_HEIGHT - 25))

        # Apply screen shake
        offset_surf = screen.copy()
        if ox != 0 or oy != 0:
            screen.fill(BLACK)
            screen.blit(offset_surf, (ox, oy))

        # Draw veggies
        for v in self.vegetables:
            v.draw(screen)

        # Draw power-ups
        for pu in self.powerups:
            pu.draw(screen)

        # Particles
        for p in self.particles:
            p.draw(screen)

        # Floating text
        for ft in self.floating_texts:
            ft.draw(screen)

        # HUD - top bar
        hud_bg = pygame.Surface((WINDOW_WIDTH, 55), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 80))
        screen.blit(hud_bg, (0, 0))

        # Score
        score_color = GOLDEN if "double_points" in self.active_effects else WHITE
        score_txt = self.font_medium.render(f"Score: {self.score}", True, score_color)
        screen.blit(score_txt, (15, 10))

        # Combo
        if self.combo >= 3:
            combo_txt = self.font_small.render(f"Combo x{self.combo}!", True, GOLDEN)
            screen.blit(combo_txt, (15, 42))

        # Timer
        time_color = RED if self.time_left <= 10 else WHITE
        time_str = f"Time: {int(self.time_left)}"
        timer_txt = self.font_medium.render(time_str, True, time_color)
        screen.blit(timer_txt, (WINDOW_WIDTH - timer_txt.get_width() - 15, 10))

        # Active effects
        eff_x = WINDOW_WIDTH // 2 - 80
        for eff_name, remaining in self.active_effects.items():
            info = POWERUP_TYPES.get(eff_name, {})
            c = info.get("color", WHITE)
            eff_txt = self.font_tiny.render(f"{info.get('desc', eff_name)} {remaining:.1f}s", True, c)
            screen.blit(eff_txt, (eff_x, 15))
            eff_x += eff_txt.get_width() + 15

        # High score
        hs = self.high_scores.get(self.difficulty, 0)
        if hs > 0:
            hs_txt = self.font_tiny.render(f"Best: {hs}", True, WHITE)
            screen.blit(hs_txt, (15, 55))

        # Pause hint
        hint = self.font_tiny.render("ESC = Pause", True, (*text_color[:3],))
        screen.blit(hint, (WINDOW_WIDTH - hint.get_width() - 10, 42))

    def draw_pause_overlay(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        title = self.font_large.render("Paused", True, WHITE)
        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 200)))
        self.btn_resume.draw(screen)
        self.btn_pause_menu.draw(screen)

    def draw_game_over(self):
        level = LEVELS[self.level_index]
        level["draw_bg"](screen)

        # Darken
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        # Panel
        panel = pygame.Rect(WINDOW_WIDTH // 2 - 200, 100, 400, 430)
        pygame.draw.rect(screen, (*CREAM, 230), panel, border_radius=20)
        pygame.draw.rect(screen, DARK_BROWN, panel, 3, border_radius=20)

        cx = WINDOW_WIDTH // 2

        title = self.font_large.render("Game Over!", True, DARK_BROWN)
        screen.blit(title, title.get_rect(center=(cx, 150)))

        # Score
        score_txt = self.font_medium.render(f"Score: {self.score}", True, DARK_BROWN)
        screen.blit(score_txt, score_txt.get_rect(center=(cx, 220)))

        hs = self.high_scores.get(self.difficulty, 0)
        hs_color = GOLDEN if self.score >= hs else DARK_BROWN
        hs_label = "New Best!" if self.score >= hs and self.score > 0 else f"Best: {hs}"
        hs_txt = self.font_medium.render(hs_label, True, hs_color)
        screen.blit(hs_txt, hs_txt.get_rect(center=(cx, 265)))

        # Stats
        target = DIFFICULTIES[self.difficulty]["target"]
        target_txt = self.font_small.render(f"Target: {target}", True, DARK_BROWN)
        screen.blit(target_txt, target_txt.get_rect(center=(cx, 310)))

        if self.score >= target:
            result = self.font_small.render("You did it!", True, FOREST_GREEN)
        else:
            result = self.font_small.render("Try again!", True, TOMATO_RED)
        screen.blit(result, result.get_rect(center=(cx, 345)))

        # Chop breakdown
        y = 380
        breakdown = self.font_tiny.render("Veggies chopped:", True, DARK_BROWN)
        screen.blit(breakdown, breakdown.get_rect(center=(cx, y)))
        y += 25
        items = [(k, v) for k, v in self.session_chops.items() if v > 0]
        items.sort(key=lambda x: -x[1])
        for vt, count in items[:4]:
            line = self.font_tiny.render(f"{vt}: {count}", True, DARK_BROWN)
            screen.blit(line, line.get_rect(center=(cx, y)))
            y += 20

        self.btn_restart.draw(screen)
        self.btn_menu.draw(screen)

    def draw_achievements(self):
        screen.fill(CREAM)
        title = self.font_large.render("Achievements", True, DARK_BROWN)
        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 50)))

        unlocked = self.ach_data.get("unlocked", [])
        y = 110
        for i, ach in enumerate(ACHIEVEMENT_DEFS):
            is_unlocked = ach["id"] in unlocked
            # Card
            card = pygame.Rect(WINDOW_WIDTH // 2 - 250, y, 500, 45)
            c = (*SOFT_GREEN, 200) if is_unlocked else (200, 200, 200, 150)
            pygame.draw.rect(screen, c, card, border_radius=8)
            pygame.draw.rect(screen, DARK_BROWN if is_unlocked else (180, 180, 180), card, 2, border_radius=8)

            icon = ">" if is_unlocked else "?"
            icon_txt = self.font_medium.render(icon, True, GOLDEN if is_unlocked else (150, 150, 150))
            screen.blit(icon_txt, (card.x + 15, card.y + 8))

            name_txt = self.font_small.render(ach["name"], True, DARK_BROWN if is_unlocked else (150, 150, 150))
            screen.blit(name_txt, (card.x + 55, card.y + 5))

            desc_txt = self.font_tiny.render(ach["desc"], True, DARK_BROWN if is_unlocked else (170, 170, 170))
            screen.blit(desc_txt, (card.x + 55, card.y + 27))

            y += 52

        # Stats
        stats = self.ach_data.get("stats", {})
        stat_y = WINDOW_HEIGHT - 110
        stats_txt = self.font_small.render(f"Total Chops: {stats.get('total_chops', 0)}   "
                                           f"Best Combo: {stats.get('max_combo', 0)}", True, DARK_BROWN)
        screen.blit(stats_txt, stats_txt.get_rect(center=(WINDOW_WIDTH // 2, stat_y)))

        self.btn_ach_back.draw(screen)

    def draw_achievement_popup(self):
        if not self.new_achievements:
            return
        name = self.new_achievements[0]
        w, h = 320, 60
        popup = pygame.Rect(WINDOW_WIDTH // 2 - w // 2, 80, w, h)
        pygame.draw.rect(screen, (*GOLDEN, 220), popup, border_radius=12)
        pygame.draw.rect(screen, DARK_BROWN, popup, 2, border_radius=12)
        label = self.font_small.render("Achievement Unlocked!", True, DARK_BROWN)
        screen.blit(label, label.get_rect(center=(popup.centerx, popup.y + 18)))
        name_txt = self.font_small.render(name, True, DARK_BROWN)
        screen.blit(name_txt, name_txt.get_rect(center=(popup.centerx, popup.y + 42)))

    # --- Main loop ---
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            dt = min(dt, 0.05)  # clamp to avoid physics explosions
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_sounds()
    game = Game()
    game.run()
