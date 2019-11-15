import pygame
from settings import *


# Characters
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

    def check_items(self):
        hits = pygame.sprite.spritecollide(self, items, True)

        for item in hits:
            item.apply(self)

    def update(self, events, pressed):
        self.process_input(events, pressed)
        self.move()
        self.check_items()

class OldMan(pygame.sprite.Sprite):
    def __init__(self, image, x, y, message):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

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
    def __init__(self, image, x, y, value, sound):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.value = value
        self.sound = sound

    def apply(self, character):
        character.gems += self.value
        self.sound.play()


class HealingPotion(pygame.sprite.Sprite):
    def __init__(self, image, x, y, strength, sound):
        super().__init__()

        self.image = image
        self.rect = image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.strength = strength
        self.sound = sound

    def apply(self, character):
        character.health += self.strength
        self.sound.play()
