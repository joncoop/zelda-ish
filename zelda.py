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
DARK_GREEN = (0, 125, 0)

# Make the window
window = pygame.display.set_mode([WIDTH, HEIGHT + GRID_SIZE])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Panels
hud = pygame.Surface([WIDTH, GRID_SIZE])
game = pygame.Surface([WIDTH, HEIGHT])

# Utility classes
def load_image(path, scale=None):
    img = pygame.image.load(path)
    img = img.convert_alpha()

    if scale != None:
        img = pygame.transform.scale(img, scale)

    return img

# Assets and Settings
FONT_SM = pygame.font.Font(None, 32)
FONT_MD = pygame.font.Font(None, 64)
FONT_LG = pygame.font.Font("fonts/The Wild Breath of Zelda.otf", 112)

MAP_FILE = 'maps/map1.txt'

hero_img = load_image('images/characters/elf.png')
big_elf = load_image('images/elf_originals/3_WALK_000.png', [128, 128])
stone_img = load_image('images/stone/Stone (6).png', [GRID_SIZE, GRID_SIZE])
grass_img = load_image('images/grass/Grass (5).png', [GRID_SIZE, GRID_SIZE])
gem_img = load_image('images/items/gem.png')
potion_img = load_image('images/items/potion4.png')
old_man_img = load_image('images/characters/old_man.png')
sandwich_img = load_image('images/items/sandwich.png')

BLUE_GEM_VALUE = 1
GEM_SOUND = pygame.mixer.Sound('sounds/gem.ogg')

HEALING_POTION_STRENGTH = 5
HEAL_SOUND = pygame.mixer.Sound('sounds/heal.ogg')

PLAYER_SPEED = 4

P1_CTRLS = {'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT }

ROOM_TRANSITION_SPEED = GRID_SIZE / 4

START = 0
PLAYING = 1
END = 2

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
        self.gems = 0
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

        self.value = BLUE_GEM_VALUE
        self.sound = GEM_SOUND

    def apply(self, character):
        character.gems += self.value
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
        self.old_men = pygame.sprite.Group()

        self.load()

    def load(self):
        with open(self.file, 'r') as f:
            data = f.read().splitlines()

        for i, line in enumerate(data):
            for j, character in enumerate(line):
                x = j * GRID_SIZE + GRID_SIZE / 2
                y = i * GRID_SIZE + GRID_SIZE / 2
                
                if character == 'W':
                    self.walls.add( Tile(stone_img, x, y) )
                elif character == 'G':
                    self.items.add( Gem(gem_img, x, y) )
                elif character == 'H':
                    self.items.add( HealingPotion(potion_img, x, y) )
                elif character == 'P':
                    self.player.add( Character(hero_img, x, y, P1_CTRLS) )
                elif character == 'O':
                    self.old_men.add( OldMan(old_man_img, x, y, "It's safe to go by yourself. Take this!") )
                elif character == 'E':
                    self.old_men.add( Enemy(enemy_img, x, y) )

                self.ground.add( Tile(grass_img, x, y) )
                                
class OldMan(pygame.sprite.Sprite):
    def __init__(self, image, x, y, message):
        super().__init__()
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.message = message
        self.speaking = False
        
    def speak(self):
        x = 3 * GRID_SIZE
        y = 3 * GRID_SIZE
        w = WIDTH - 6 * GRID_SIZE
        h = HEIGHT - 6 * GRID_SIZE
        
        pygame.draw.rect(game, BLACK, [x, y, w, h])
        pygame.draw.rect(game, WHITE, [x, y, w, h], 2)
        message = FONT_SM.render(self.message, 1, WHITE)
        message_rect = message.get_rect()
        message_rect.centerx = WIDTH / 2
        message_rect.centery = HEIGHT / 2 - GRID_SIZE
        game.blit(message, message_rect)

        rect = sandwich_img.get_rect()
        rect.centerx = WIDTH / 2
        rect.centery = HEIGHT / 2
        game.blit(sandwich_img, rect)

    def update(self):
        self.speaking = pygame.sprite.spritecollideany(self, player, False)
    
# Helper functions
def intro_screen():
    window.fill(BLACK)
    
    title = FONT_LG.render(TITLE, 1, DARK_GREEN)
    title_rect = title.get_rect()
    title_rect.centerx = WIDTH / 2
    title_rect.centery = 260

    sub_title = FONT_SM.render("Link to the Legends of the Wild Past", 1, WHITE)
    sub_title_rect = sub_title.get_rect()
    sub_title_rect.centerx = WIDTH / 2 + 40
    sub_title_rect.centery = 284
    
    start = FONT_SM.render("Press SPACE to begin...", 1, WHITE)
    start_rect = start.get_rect()
    start_rect.centerx = WIDTH / 2
    start_rect.centery = 500

    window.blit(title, title_rect)
    window.blit(sub_title, sub_title_rect)
    window.blit(start, start_rect)

    window.blit(big_elf, [WIDTH / 2 - 64, 320])
    pygame.draw.rect(window, DARK_GREEN, [64, 64, WIDTH - 128, HEIGHT - 64], 16)

def show_stats(character):
    health = FONT_SM.render("Health: " + str(character.health), 1, WHITE)
    gems = FONT_SM.render("Gems: " + str(character.gems), 1, WHITE)

    hud.fill(BLACK)
    hud.blit(health, [16, 16])
    hud.blit(gems, [WIDTH - 108, 16])  

    
# Setup
world = Map(MAP_FILE)
player = world.player
walls = world.walls
items = world.items
ground = world.ground
old_men = world.old_men

all_sprites = pygame.sprite.Group()
all_sprites.add(player, walls, items, old_men)

stage = START

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
            if stage == START:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        stage = PLAYING
            elif stage == PLAYING:
                filtered_events.append(event)
            
    pressed = pygame.key.get_pressed()
    
    # Game logic
    if stage == PLAYING and not transitioning:
        player.update(filtered_events, pressed)
        old_men.update()

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
            game.blit(s.image, [x, y])
        
    for s in all_sprites:
        x = s.rect.x - offset_x
        y = s.rect.y - offset_y
        
        if x < WIDTH and y < HEIGHT:
            game.blit(s.image, [x, y])

    for man in old_men:
        if man.speaking:
            man.speak()
    
    if stage == START:
        intro_screen()
    else:
        show_stats(player.sprite)
        window.blit(hud, [0, 0])
        window.blit(game, [0, GRID_SIZE])
    
    # Update display
    pygame.display.update()
    clock.tick(FPS)

# Close window and quit
pygame.quit()
