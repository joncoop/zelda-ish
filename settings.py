import pygame

# Window settings
GRID_SIZE = 64
WIDTH = 15 * GRID_SIZE
HEIGHT = 10 * GRID_SIZE
TITLE = "Zelda-ish"
SUBTITLE = "Link to the Legends of the Time of the Wild Past"
FPS = 60

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (225, 225, 225)
BLACK = (0, 0, 0)
DARK_GREEN = (0, 125, 0)

# Images


# Sounds
GEM_SND = 'sounds/gem.ogg'
HEAL_SND = 'sounds/heal.ogg'

# Fonts
FONT_SM = None
FONT_MD = None
FONT_TITLE = 'fonts/The Wild Breath of Zelda.otf'

# Data
MAP_FILE = 'maps/map1.txt'

# Game settings
GEM_VALUE = 1
HEALING_POTION_STRENGTH = 5

PLAYER_SPEED = 4
P1_CTRLS = {'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT }

# Effects
ROOM_TRANSITION_SPEED = GRID_SIZE / 4

START = 0
PLAYING = 1
END = 2
