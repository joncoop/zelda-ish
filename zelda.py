# Imports
import pygame

# Initialize game engine
pygame.init()


# Window settings
GRID_SIZE = 64
WIDTH = 15 * GRID_SIZE
HEIGHT = 10 * GRID_SIZE
TITLE = "Zelda-ish"
SUBTITLE = "Link to the Legends of the Time of the Wild Past"
FPS = 60

HUD_HEIGHT = 96

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
DARK_GREEN = (0, 125, 0)
LIME_GREEN = (150, 255, 100)
RED = (200, 0, 0)


# Game settings
MAP_FILE = 'maps/map1.txt'

PLAYER_HEALTH = 3
PLAYER_MAX_HEALTH = 5
PLAYER_SPEED = 4
CONTROLS = {'up': pygame.K_w,
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d,
            'sword': pygame.K_SPACE}

GEM_VALUE = 1
HEALING_POTION_STRENGTH = 1

ROOM_TRANSITION_SPEED = 16


# Make the window
screen = pygame.display.set_mode([WIDTH, HEIGHT + HUD_HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()


# Utility functions
def load_image(path, size=None):
    img = pygame.image.load(path)
    img = img.convert_alpha()

    if size is not None:
        img = pygame.transform.scale(img, size)

    return img

def load_sound(path, volume=1.0):
    snd = pygame.mixer.Sound(path)
    snd.set_volume(volume)

    return snd

def play_music(path, loops=-1, volume=1.0):
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loops)
    
def pause_music():
    busy = pygame.mixer.music.get_busy()

    if busy:
        pygame.mixer.music.pause()
        
def unpause_music():
    busy = pygame.mixer.music.get_busy()

    if busy:
        pygame.mixer.music.pause()
        
def stop_music(fadeout_time=0):
    pygame.mixer.music.fadeout(fadeout_time)

def draw_text(surface, text, font, color, loc, anchor='topleft', antialias=True):
    text = str(text)
    text = font.render(text, antialias, color)
    rect = text.get_rect()

    if   anchor == 'topleft'     : rect.topleft = loc
    elif anchor == 'bottomleft'  : rect.bottomleft = loc
    elif anchor == 'topright'    : rect.topright = loc
    elif anchor == 'bottomright' : rect.bottomright = loc
    elif anchor == 'midtop'      : rect.midtop = loc
    elif anchor == 'midleft'     : rect.midleft = loc
    elif anchor == 'midbottom'   : rect.midbottom = loc
    elif anchor == 'midright'    : rect.midleft = loc
    elif anchor == 'center'      : rect.center = loc
    
    surface.blit(text, rect)

   
# Load assets
FONT_XS = pygame.font.Font(None, 16)
FONT_SM = pygame.font.Font(None, 32)
FONT_MD = pygame.font.Font(None, 64)
FONT_LG = pygame.font.Font(None, 96)
FONT_TITLE = pygame.font.Font('fonts/The Wild Breath of Zelda.otf', 112)

GEM_SND = load_sound('sounds/gem.ogg')
HEAL_SND = load_sound('sounds/heal.ogg')

HERO_IMG = load_image('images/characters/elf.png')
BIG_ELF_IMG = load_image('images/elf_originals/3_WALK_000.png', [128, 128])
STONE_IMG = load_image('images/stone/Stone (6).png', [GRID_SIZE, GRID_SIZE])
GRASS_IMG = load_image('images/grass/Grass (5).png', [GRID_SIZE, GRID_SIZE])
GEM_IMG = load_image('images/items/gem.png')
POTION_IMG = load_image('images/items/potion4.png')
GEM_ICON = load_image('images/items/gem.png', [32, 32])
HEART_ICON = load_image('images/items/heart.png', [32, 32])

SWORD_IMG = load_image('images/items/woodSword.png', [32, 32])


# Characters
class Player(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.speed = PLAYER_SPEED
        self.vx = 0
        self.vy = 0
        self.gems = 0
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.weapon = None
        
    def go_up(self):
        self.vx = 0
        self.vy = -1 * self.speed
        
    def go_down(self):
        self.vx = 0
        self.vy = self.speed
        
    def go_left(self):
        self.vx = -1 * self.speed
        self.vy = 0
        
    def go_right(self):
        self.vx = self.speed
        self.vy = 0

    def stop(self):
        self.vx = 0
        self.vy = 0
        
    def move(self, walls):
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

    def use_sword(self):
        if self.weapon != None:
            print('Woosh')
    
    def check_items(self, items):
        hits = pygame.sprite.spritecollide(self, items, True)

        for item in hits:
            item.apply(self)

    def update(self, world):
        self.move(world.walls)
        self.check_items(world.items)

class Mob(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def update(self):
        pass


# Tiles
class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y


# Items
class Gem(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.value = GEM_VALUE
        self.sound = GEM_SND

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
        self.sound = HEAL_SND

    def apply(self, character):
        character.health += self.strength
        character.health = min(character.max_health, character.health)
        self.sound.play()


# Weapons
class Sword(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def apply(self, character):
        character.weapon = self

    
# Map
class Map():
    def __init__(self, file):
        self.file = file
        self.player = None
        self.walls = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.ground = pygame.sprite.Group()

        self.load()

    def load(self):
        with open(self.file, 'r') as f:
            data = f.read().splitlines()

        for i, line in enumerate(data):
            for j, symbol in enumerate(line):
                x = j * GRID_SIZE + GRID_SIZE / 2
                y = i * GRID_SIZE + GRID_SIZE / 2

                if symbol == 'P':
                    self.player = Player(HERO_IMG, x, y)
                elif symbol == 'W':
                    self.walls.add(Tile(STONE_IMG, x, y))
                elif symbol == 'G':
                    self.items.add(Gem(GEM_IMG, x, y))
                elif symbol == 'H':
                    self.items.add(HealingPotion(POTION_IMG, x, y))
                elif symbol == 'S':
                    self.items.add(Sword(SWORD_IMG, x, y))

                self.ground.add(Tile(GRASS_IMG, x, y))


# Scenes
class Scene():
    def __init__(self):
        self.next_scene = self

    def process_input(self, events, pressed_keys):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError

    def terminate(self):
        self.next_scene = None


class TitleScene(Scene):
    def __init__(self):
        super().__init__()

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.next_scene = PlayScene()

    def update(self):
        pass

    def render(self):
        screen.fill(BLACK)
        draw_text(screen, TITLE, FONT_TITLE, DARK_GREEN, [WIDTH // 2, HEIGHT // 2 - 40], 'center')
        draw_text(screen, SUBTITLE, FONT_SM, WHITE, [WIDTH // 2 - 140, HEIGHT // 2 - 22], 'topleft')
        draw_text(screen, 'Press SPACE to begin', FONT_SM, WHITE, [WIDTH // 2, HEIGHT - GRID_SIZE], 'midbottom')

        rect = BIG_ELF_IMG.get_rect()
        rect.center = [WIDTH //2, HEIGHT // 2 + 128]
        screen.blit(BIG_ELF_IMG, rect)
        
        pygame.draw.rect(screen, DARK_GREEN, [64, 64, WIDTH - 128, HEIGHT - 64], 16)
        
    def terminate(self):
        self.next_scene = None


class PlayScene(Scene):
    def __init__(self):
        super().__init__()
        
        self.world = Map(MAP_FILE)
        self.player = self.world.player
        self.walls = self.world.walls
        self.items = self.world.items
        self.ground = self.world.ground

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player, self.walls, self.items)

        self.set_start_offset()

        self.main = pygame.Surface([WIDTH, HEIGHT])
        self.hud = pygame.Surface([WIDTH, HUD_HEIGHT])
        
    def process_input(self, events, pressed):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.next_scene = EndScene()
                elif event.key == pygame.K_SPACE:
                    self.player.use_sword()

        if pressed[CONTROLS['up']]:
            self.player.go_up()
        elif pressed[CONTROLS['down']]:
            self.player.go_down()
        elif pressed[CONTROLS['left']]:
            self.player.go_left()
        elif pressed[CONTROLS['right']]:
            self.player.go_right()
        else:
            self.player.stop()

    def set_start_offset(self):
        self.transitioning = False
        self.last_room_x = self.player.rect.centerx // WIDTH
        self.last_room_y = self.player.rect.centery // HEIGHT
        self.step = 0

        self.offset_x = self.last_room_x * WIDTH
        self.offset_y = self.last_room_y * HEIGHT
            
    def calculate_offset(self):
        room_x = self.player.rect.centerx // WIDTH
        room_y = self.player.rect.centery // HEIGHT

        if not self.transitioning and (self.last_room_x != room_x or self.last_room_y != room_y):
            self.transitioning = True
            self.step = 0

        if self.transitioning:
            self.offset_x = self.last_room_x * WIDTH + self.step * (room_x - self.last_room_x)
            self.offset_y = self.last_room_y * HEIGHT + self.step * (room_y - self.last_room_y)
            self.step += ROOM_TRANSITION_SPEED

            if room_x != self.last_room_x and self.step >= WIDTH:
                self.last_room_x = room_x
                self.last_room_y = room_y
                self.transitioning = False
            elif room_y != self.last_room_y and self.step >= HEIGHT:
                self.last_room_x = room_x
                self.last_room_y = room_y
                self.transitioning = False
        else:
            self.offset_x = room_x * WIDTH
            self.offset_y = room_y * HEIGHT
            
    def update(self):
        self.calculate_offset()
        self.player.update(self.world)

    def render(self):
        screen.fill(BLACK)

        ''' hud '''
        self.hud.fill(BLACK)
        pygame.draw.rect(self.hud, LIGHT_GRAY, [16, 16, 128, 64])
        x = 16 + self.player.rect.centerx // WIDTH * 8
        y = 16 + self.player.rect.centery // HEIGHT * 8
        pygame.draw.rect(self.hud, LIME_GREEN, [x, y, 8, 8])
        
        self.hud.blit(GEM_ICON, [164, 16])
        draw_text(self.hud, f'x{self.player.gems}', FONT_SM, WHITE, [196, 16], anchor='topleft', antialias=True)

        draw_text(self.hud, '-- Life --', FONT_SM, RED, [WIDTH - 72, 16], anchor='topright', antialias=True)
        for n in range(self.player.health):
            self.hud.blit(HEART_ICON, [768 + 32 * n, 48])

        ''' world '''
        for s in self.ground:
            x = s.rect.x - self.offset_x
            y = s.rect.y - self.offset_y

            if -GRID_SIZE < x < WIDTH and -GRID_SIZE < y < HEIGHT:
                self.main.blit(s.image, [x, y])

        for s in self.all_sprites:
            x = s.rect.x - self.offset_x
            y = s.rect.y - self.offset_y

            if x < WIDTH and y < HEIGHT:
                self.main.blit(s.image, [x, y])

        screen.blit(self.hud, [0, 0])
        screen.blit(self.main, [0, HUD_HEIGHT])
        
    def terminate(self):
        self.next_scene = None


class EndScene(Scene):
    def __init__(self):
        super().__init__()

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.next_scene = TitleScene()

    def update(self):
        pass

    def render(self):
        screen.fill(BLACK)
        draw_text(screen, 'End Scene', FONT_LG, WHITE, [WIDTH // 2, HEIGHT // 2], 'center')


    def terminate(self):
        self.next_scene = None

# Game
class Game():
    def __init__(self):
        self.active_scene = TitleScene()

    def is_quit_event(self, event, pressed_keys):
        x_out = event.type == pygame.QUIT
        ctrl = pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]
        q = pressed_keys[pygame.K_q]

        return x_out or (ctrl and q)

    def run(self):
        while self.active_scene != None:
            # event handling
            pressed_keys = pygame.key.get_pressed()
            filtered_events = []

            for event in pygame.event.get():
                if self.is_quit_event(event, pressed_keys):
                    self.active_scene.terminate()
                else:
                    filtered_events.append(event)

            # game logic
            self.active_scene.process_input(filtered_events, pressed_keys)
            self.active_scene.update()
            self.active_scene.render()
            self.active_scene = self.active_scene.next_scene

            # update and tick
            pygame.display.update()
            clock.tick(FPS)

    def quit(self):
        pygame.quit()

if __name__ == "__main__":
    g = Game()
    g.run()
    g.quit()
