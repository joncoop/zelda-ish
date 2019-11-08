# Imports
import pygame

# Initialize game engine
pygame.init()

# Window settings
GRID_SIZE = 64
WIDTH = 15 * GRID_SIZE
HEIGHT = 10 * GRID_SIZE
TITLE = "Zelda-ish"
FPS = 60

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (225, 225, 225)
BLACK = (0, 0, 0)

# Make the window
window = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Assets and Settings
MAP_FILE = 'maps/map1.txt'

hero_img = pygame.image.load('images/character.png').convert_alpha()
wall_img = pygame.image.load('images/block.png').convert_alpha()
dirt_img = pygame.image.load('images/dirt.png').convert_alpha()
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

ROOM_TRANSITION_SPEED = GRID_SIZE / 4

# Sprite classes
class Character(pygame.sprite.Sprite):
    def __init__(self, image, x, y, controls):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
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

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        
class Gem(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.value = GEM_VALUE
        self.sound = GEM_SOUND

    def apply(self, character):
        character.score += self.value
        self.sound.play()
        
class HealingPotion(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

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
        self.ground = pygame.sprite.Group()

        self.load()

    def load(self):
        with open(self.file, 'r') as f:
            data = f.read().splitlines()

        for i, line in enumerate(data):
            for j, character in enumerate(line):
                x = j * GRID_SIZE + GRID_SIZE / 2
                y = i * GRID_SIZE + GRID_SIZE / 2
                
                if character == 'W':
                    self.walls.add( Tile(wall_img, x, y) )
                elif character == 'G':
                    self.items.add( Gem(gem_img, x, y) )
                elif character == 'H':
                    self.items.add( HealingPotion(potion_img, x, y) )
                elif character == 'P':
                    self.player.add( Character(hero_img, x, y, P1_CTRLS) )

                self.ground.add( Tile(dirt_img, x, y) )
                
                    
# Helper functions
def show_stats():
    pass

# Setup
world = Map(MAP_FILE)
player = world.player
walls = world.walls
items = world.items
ground = world.ground

all_sprites = pygame.sprite.Group()
all_sprites.add(player, walls, items)

# Game loop
running = True

transitioning = False
last_room_x = 0
last_room_y = 0

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
    if not transitioning:
        player.update(filtered_events, pressed)

    room_x = player.sprite.rect.centerx // WIDTH
    room_y = player.sprite.rect.centery // HEIGHT

    if not transitioning and (last_room_x != room_x or last_room_y != room_y):
        transitioning = True
        step = 0
        
    if transitioning:
        offset_x = last_room_x * WIDTH + step * (room_x - last_room_x)
        offset_y = last_room_y * HEIGHT + step * (room_y - last_room_y)
        step += ROOM_TRANSITION_SPEED

        if room_x != last_room_x and step >= WIDTH:
            last_room_x = room_x
            last_room_y = room_y
            transitioning = False
        elif room_y != last_room_y and step >= HEIGHT:
            last_room_x = room_x
            last_room_y = room_y
            transitioning = False
    else:
        offset_x = room_x * WIDTH
        offset_y = room_y * HEIGHT

    # Drawing code
    window.fill(BLACK)

    for s in ground:
        x = s.rect.x - offset_x
        y = s.rect.y - offset_y
        
        if x < WIDTH and y < HEIGHT:
            window.blit(s.image, [x, y])
        
    for s in all_sprites:
        x = s.rect.x - offset_x
        y = s.rect.y - offset_y
        
        if x < WIDTH and y < HEIGHT:
            window.blit(s.image, [x, y])
        
    show_stats()

    # Update display
    pygame.display.update()
    clock.tick(FPS)

# Close window and quit
pygame.quit()
