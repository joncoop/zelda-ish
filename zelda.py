# Imports
import pygame

# Initialize game engine
pygame.init()

# Window settings
TILE_SIZE = 64
WIDTH = 15 * TILE_SIZE
HEIGHT = 10 * TILE_SIZE
TITLE = "Zelda"
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Make the window
window = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Assets and Settings
MAP_FILE = 'maps/map1.txt'

parrot_img = pygame.image.load('images/parrot.png').convert_alpha()
wall_img = pygame.image.load('images/block.png').convert_alpha()
gem_img = pygame.image.load('images/gem.png').convert_alpha()
potion_img = pygame.image.load('images/potion.png').convert_alpha()

GEM_VALUE = 1
GEM_SOUND = pygame.mixer.Sound('sounds/gem.ogg')

HEALING_POTION_STRENGTH = 5
HEAL_SOUND = pygame.mixer.Sound('sounds/heal.ogg')

PLAYER_SPEED = 4

P1_CTRLS = {'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT }

# Sprite classes
class Character(pygame.sprite.Sprite):
    def __init__(self, image, x, y, controls):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.controls = controls

        self.speed = PLAYER_SPEED
        self.vx = 0
        self.vy = 0
        self.score = 0
        self.health = 5

    def process_input(self, events, pressed):
        self.vx = 0
        self.vy = 0
        
        if pressed[self.controls['up']]:
            self.vy = -self.speed
        elif pressed[self.controls['down']]:
            self.vy = self.speed
        elif pressed[self.controls['left']]:
            self.vx = -self.speed
        elif pressed[self.controls['right']]:
            self.vx = self.speed
            
    def move(self):
        self.rect.x += self.vx
        
        hits = pygame.sprite.spritecollide(self, walls, False)

        for obstacle in hits:
            if self.rect.centerx < obstacle.rect.centerx:
                self.rect.right = obstacle.rect.left
            elif self.rect.centerx > obstacle.rect.centerx:
                self.rect.left = obstacle.rect.right
        
        self.rect.y += self.vy
        
        hits = pygame.sprite.spritecollide(self, walls, False)
        
        for obstacle in hits:
            if self.rect.centery < obstacle.rect.centery:
                self.rect.bottom = obstacle.rect.top
            elif self.rect.centery > obstacle.rect.centery:
                self.rect.top = obstacle.rect.bottom

    def check_edges(self):
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def process_items(self):
        hits = pygame.sprite.spritecollide(self, items, True)

        for item in hits:
            item.apply(self)

    def update(self, events, pressed):
        self.process_input(events, pressed)
        self.move()
        #self.check_edges()
        self.process_items()

class Wall(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
class gem(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.value = gem_VALUE
        self.sound = gem_SOUND

    def apply(self, character):
        character.score += self.value
        self.sound.play()
        
class HealingPotion(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.strength = HEALING_POTION_STRENGTH
        self.sound = HEAL_SOUND

    def apply(self, character):
        character.health += self.strength
        self.sound.play()

class Map():
    def __init__(self, file):
        self.file = file
        self.player = pygame.sprite.GroupSingle()
        self.walls = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        self.load()

    def load(self):
        with open(self.file, 'r') as f:
            data = f.read().splitlines()

        for i, line in enumerate(data):
            for j, character in enumerate(line):
                x = j * TILE_SIZE
                y = i * TILE_SIZE
                
                if character == 'W':
                    self.walls.add( Wall(wall_img, x, y) )
                elif character == 'C':
                    self.items.add( gem(gem_img, x, y) )
                elif character == 'H':
                    self.items.add( HealingPotion(potion_img, x, y) )
                elif character == '1':
                    self.player.add( Character(parrot_img, x, y, P1_CTRLS) )
                    
# Helper functions
def show_stats():
    pass

# Setup
world = Map(MAP_FILE)
player = world.player
walls = world.walls
items = world.items

all_sprites = pygame.sprite.Group()
all_sprites.add(player, walls, items)

# Game loop
running = True
transitioning = False

while running:
    # Input handling
    filtered_events = []
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            filtered_events.append(event)
            
    pressed = pygame.key.get_pressed()
    
    # Game logic
    player.update(filtered_events, pressed)
    offset_x = (player.sprite.rect.x // WIDTH) * WIDTH
    offset_y = (player.sprite.rect.y // HEIGHT) * HEIGHT

    # Drawing code
    window.fill(BLACK)

    for s in all_sprites:
        room_x = s.rect.x - offset_x
        room_y= s.rect.y - offset_y
        
        if room_x < WIDTH and room_y < HEIGHT:
            window.blit(s.image, [room_x, room_y])
        
    show_stats()

    # Update display
    pygame.display.update()
    clock.tick(FPS)

# Close window and quit
pygame.quit()
