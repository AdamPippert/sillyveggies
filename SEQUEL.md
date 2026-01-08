# Silly Veggies 2 - Development Plan

A bigger, more polished sequel to the original Silly Veggies game, designed for Isabella!

## Overview

Silly Veggies 2 takes the original vegetable-chopping fun and expands it with moving vegetables, sound effects, power-ups, multiple levels, achievements, and a polished UI experience.

---

## Feature List

### 1. Main Menu System
- Animated title screen with bouncing vegetables
- Play button with difficulty selection
- Options menu (sound toggle, controls info)
- Achievements viewer
- High scores display

### 2. Moving Vegetables (Priority Feature)
- Vegetables bounce around the screen with physics
- Different movement patterns per vegetable type:
  - **Bouncy**: Bounces off walls
  - **Floaty**: Slow, drifting movement
  - **Zippy**: Fast, unpredictable movement
  - **Spinner**: Rotates while moving
- Speed increases with difficulty level
- Vegetables wiggle when idle

### 3. Expanded Vegetable Roster (8+ Types)
| Vegetable | Color | Personality | Movement Style |
|-----------|-------|-------------|----------------|
| Carrot | Orange | Crunchy & silly | Bouncy |
| Broccoli | Green | Health-obsessed | Floaty |
| Tomato | Red | Juicy & dramatic | Bouncy |
| Corn | Yellow | Corny jokes | Spinner |
| Eggplant | Purple | Mysterious | Floaty |
| Bell Pepper | Multi-color | Energetic | Zippy |
| Onion | White/Brown | Makes you cry | Bouncy |
| Peas | Light Green | Works as a team (3 peas) | Zippy |

Each vegetable has unique:
- Appearance (drawn with Pygame shapes)
- Funny dialogue messages
- Point value (1-3 based on difficulty to catch)
- Movement behavior

### 4. Sound Effects System (Priority Feature)
- **Chop sounds**: Satisfying "chop!" for each vegetable
- **Vegetable voices**: Quick sound when veggie appears
- **Power-up sounds**: Special effects for power-ups
- **Background music**: Fun, upbeat loop
- **UI sounds**: Button clicks, menu transitions
- **Achievement unlock**: Celebration sound

*Note: Sounds generated programmatically using Pygame's audio synthesis*

### 5. Power-Up System
| Power-Up | Effect | Duration | Visual |
|----------|--------|----------|--------|
| Golden Veggie | 5x points | Instant | Glowing gold |
| Slow-Mo | Slows all veggies | 5 seconds | Blue tint |
| Double Points | 2x score multiplier | 10 seconds | Score turns gold |
| Freeze | Stops all veggies | 3 seconds | Ice crystals |
| Veggie Magnet | Veggies come to cursor | 5 seconds | Swirl effect |

Power-ups spawn randomly (10% chance when chopping)

### 6. Themed Levels/Backgrounds
1. **Garden** (Level 1): Outdoor garden with grass and sky
2. **Kitchen** (Level 2): Counter top with tiles
3. **Farm** (Level 3): Barn and fields
4. **Space** (Bonus): Vegetables in space!

Each level has:
- Unique background art
- Themed color palette
- Special vegetable variants

### 7. Difficulty Modes
| Mode | Veggie Speed | Spawn Rate | Time | Target Score |
|------|-------------|------------|------|--------------|
| Easy | Slow | 5 veggies | 120s | 30 |
| Medium | Medium | 7 veggies | 90s | 50 |
| Hard | Fast | 10 veggies | 60s | 75 |
| Silly Mode | Chaos! | 15 veggies | 45s | 100 |

### 8. Animation & Visual Effects
- **Veggie wiggle**: Idle animation
- **Chop explosion**: Particles burst when chopped
- **Score pop-up**: "+1" floats up from chopped veggie
- **Screen shake**: On power-up activation
- **Combo effects**: Visual feedback for quick chops
- **Trail effects**: Fast veggies leave trails

### 9. Achievements System
| Achievement | Requirement | Icon |
|-------------|-------------|------|
| First Chop | Chop your first veggie | Knife |
| Veggie Hunter | Chop 100 total veggies | Target |
| Speed Chopper | Chop 5 veggies in 3 seconds | Lightning |
| Carrot King | Chop 50 carrots | Crown |
| Broccoli Boss | Chop 50 broccoli | Tree |
| Tomato Terror | Chop 50 tomatoes | Splat |
| Golden Touch | Catch 10 golden veggies | Star |
| Combo Master | Get a 10x combo | Fire |
| High Scorer | Beat 100 points | Trophy |
| Silly Champion | Beat Silly Mode | Medal |

### 10. Polished UI Elements
- Custom color scheme with gradients
- Rounded buttons with hover effects
- Animated transitions between screens
- Score display with combo counter
- Timer with visual warnings (red when low)
- Pause menu
- Settings persistence

---

## Technical Architecture

### File Structure
```
sillyveggies/
├── silly_veggies_2.py      # Main game file
├── talking_veggies.py      # Original game (preserved)
├── requirements.txt        # Dependencies
├── SEQUEL.md              # This plan
├── README.md              # Updated documentation
└── data/
    ├── high_scores.json   # Scores and stats
    └── achievements.json  # Unlocked achievements
```

### Class Structure
```python
# Core Classes
Game                 # Main game controller
GameState            # Enum for game states
Settings             # User preferences

# Entities
Vegetable            # Base vegetable class
  ├── Carrot
  ├── Broccoli
  ├── Tomato
  ├── Corn
  ├── Eggplant
  ├── BellPepper
  ├── Onion
  └── Peas
PowerUp              # Power-up items

# Systems
SoundManager         # Audio handling
ParticleSystem       # Visual effects
AchievementManager   # Achievement tracking
LevelManager         # Background/theming

# UI
Button               # Clickable buttons
Menu                 # Menu screens
HUD                  # In-game display
```

### Game States
```
MENU → DIFFICULTY_SELECT → PLAYING → PAUSED → GAME_OVER
                              ↓
                         ACHIEVEMENTS
```

---

## Implementation Order

1. **Phase 1: Core Structure**
   - Game state machine
   - Menu system
   - Basic UI framework

2. **Phase 2: Enhanced Gameplay**
   - Moving vegetables with physics
   - All 8 vegetable types
   - Collision detection improvements

3. **Phase 3: Audio & Effects**
   - Sound effect generation
   - Particle system
   - Animations

4. **Phase 4: Content**
   - Power-ups
   - Themed backgrounds
   - Difficulty modes

5. **Phase 5: Progression**
   - Achievements
   - Stats tracking
   - High score improvements

6. **Phase 6: Polish**
   - UI refinements
   - Bug fixes
   - Balance tuning

---

## Controls

- **Mouse Click**: Chop vegetables
- **ESC**: Pause game
- **M**: Toggle music
- **S**: Toggle sound effects

---

## Color Palette

| Element | Color | Hex |
|---------|-------|-----|
| Background (Menu) | Soft Green | #90EE90 |
| Primary Button | Tomato Red | #FF6347 |
| Secondary Button | Carrot Orange | #FFA500 |
| Text | Dark Brown | #4A3728 |
| Accent | Golden | #FFD700 |
| UI Panel | Cream | #FFFDD0 |

---

## Success Metrics

- Fun factor: Does Isabella enjoy playing?
- Replayability: Multiple difficulty modes and achievements
- Polish: Smooth animations and satisfying feedback
- Performance: Stable 60 FPS

---

*Created with love for Isabella's gaming adventures!*
