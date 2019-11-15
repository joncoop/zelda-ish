# Imports
import pygame
from settings import *
from sprites import *

# Initialize game engine
pygame.init()

# Make the window
window = pygame.display.set_mode([WIDTH, HEIGHT + GRID_SIZE])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Panels
hud = pygame.Surface([WIDTH, GRID_SIZE])
game = pygame.Surface([WIDTH, HEIGHT])


# Utility classes
def load_image(path, size=None):
    img = pygame.image.load(path)
    img = img.convert_alpha()

    if size is not None:
        img = pygame.transform.scale(img, size)

    return img


# Load assets
small_font = pygame.font.Font(FONT_SM, 32)
medium_font = pygame.font.Font(FONT_MD, 64)
title_font = pygame.font.Font(FONT_TITLE, 112)

gem_snd = pygame.mixer.Sound(GEM_SND)
heal_snd = pygame.mixer.Sound(HEAL_SND)

hero_img = load_image('images/characters/elf.png')
big_elf = load_image('images/elf_originals/3_WALK_000.png', [128, 128])
stone_img = load_image('images/stone/Stone (6).png', [GRID_SIZE, GRID_SIZE])
grass_img = load_image('images/grass/Grass (5).png', [GRID_SIZE, GRID_SIZE])
gem_img = load_image('images/items/gem.png')
potion_img = load_image('images/items/potion4.png')
old_man_img = load_image('images/characters/old_man.png')
sandwich_img = load_image('images/items/sandwich.png')


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
                    self.walls.add(Tile(stone_img, x, y))
                elif character == 'G':
                    self.items.add(Gem(gem_img, x, y, GEM_VALUE, GEM_SND))
                elif character == 'H':
                    self.items.add(HealingPotion(potion_img, x, y, HEALING_POTION_STRENGTH, HEAL_SND))
                elif character == 'P':
                    self.player.add(Character(hero_img, x, y, P1_CTRLS))
                elif character == 'E':
                    self.old_men.add(Enemy(enemy_img, x, y))

                self.ground.add(Tile(grass_img, x, y))


# Helper functions
def intro_screen():
    window.fill(BLACK)

    title = title_font.render(TITLE, 1, DARK_GREEN)
    title_rect = title.get_rect()
    title_rect.centerx = WIDTH / 2
    title_rect.centery = 260

    sub_title = small_font.render(SUBTITLE, 1, WHITE)
    sub_title_rect = sub_title.get_rect()
    sub_title_rect.centerx = WIDTH / 2 + 100
    sub_title_rect.centery = 284

    start = small_font.render("Press SPACE to begin...", 1, WHITE)
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

transitioning = False
last_room_x = 0
last_room_y = 0

stage = START

# Game loop
running = True

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

        if -GRID_SIZE < x < WIDTH and -GRID_SIZE < y < HEIGHT:
            game.blit(s.image, [x, y])

    for s in all_sprites:
        x = s.rect.x - offset_x
        y = s.rect.y - offset_y

        if x < WIDTH and y < HEIGHT:
            game.blit(s.image, [x, y])

    if stage == START:
        intro_screen()
    else:
        show_stats(player.sprite)
        window.blit(hud, [0, 0])
        window.blit(game, [0, GRID_SIZE])



# The actual game
class MyGame():
    def __init__(self, start_scene):
        self.active_scene = start_scene

    def is_quit_event(self, event, pressed_keys):
        x_out = event.type == pygame.QUIT

        ctrl_q = (event.type == pygame.KEYDOWN and
                  event.key == pygame.K_q and (pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]))

        return x_out or ctrl_q

    def run(self):
        while self.active_scene != None:
            # poll input states
            pressed_keys = pygame.key.get_pressed()

            # get events
            filtered_events = []
            for event in pygame.event.get():
                if self.is_quit_event(event, pressed_keys):
                    self.active_scene.terminate()
                else:
                    filtered_events.append(event)

            # game logic
            self.active_scene.process_input(filtered_events, pressed_keys)
            self.active_scene.update()
            self.active_scene.render(screen)
            self.active_scene = self.active_scene.next_scene

            # update screen and wait a bit
            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    game = MyGame(TitleScene())
    game.run()
    pygame.quit()
