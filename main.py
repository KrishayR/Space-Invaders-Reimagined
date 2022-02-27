import os
import time
import random
import sys
import tkinter as tk
import pygame


### Initilizing font and music ###
pygame.init()
pygame.font.init()
pygame.mixer.init()

### Window Creation ###

WIDTH, HEIGHT = 1343, 768
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

### Loading Images and music ###

# Main Player
MAIN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "main_space_ship.png"))

# Enemies
ENEMY_1 = pygame.image.load(os.path.join("assets", "enemy_1.png")) # Will be average -- decent speed and health
ENEMY_2 = pygame.image.load(os.path.join("assets", "enemy_2.png")) # Will be fast -- High speed but low health
ENEMY_3 = pygame.image.load(os.path.join("assets", "enemy_3.png")) # Will be hard to hit -- decent speed and health but low visibility and size
ENEMY_4 = pygame.image.load(os.path.join("assets", "enemy_4.png")) # Will be high health -- high health but low speed

# Bullets
MAIN_SHIP_BULLET = pygame.image.load(os.path.join("assets", "main_ship_bullet.png"))

BULLET_1 = pygame.image.load(os.path.join("assets", "bullet_1.png"))
BULLET_2 = pygame.image.load(os.path.join("assets", "bullet_2.png"))
BULLET_3 = pygame.image.load(os.path.join("assets", "bullet_3.png"))
BULLET_4 = pygame.image.load(os.path.join("assets", "bullet_4.png"))

# Background

SPACE_BG = pygame.image.load(os.path.join("assets", "space-background.png"))


pygame.mixer.music.load("assets/music.mp3")
pygame.mixer.music.play(-1)
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.x -= vel

    def off_screen(self, width):
        return self.x <= 0 and self.x >= width+200 # Check if it laser is offscreen

    def collision(self, obj):
        return collide(self, obj)

### Main Player Abstract Class ###
class Ship:
    COOLDOWN = 20
    
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.player_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.player_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)
            
    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(WIDTH):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
        
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
    def get_width(self):
        return self.player_img.get_width()
    
    def get_height(self):
        return self.player_img.get_height()
        
        
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.player_img = MAIN_SPACE_SHIP
        self.laser_img = MAIN_SHIP_BULLET
        self.mask = pygame.mask.from_surface(self.player_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(WIDTH):
                self.lasers.remove(laser)
            else:
                for i in objs:
                    if laser.collision(i):
                        objs.remove(i)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
        
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x+100, self.y+70, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def healthbar(self, window):
        pygame.draw.rect(window, (235, 64, 52), (self.x + self.player_img.get_height(), self.y, 10, self.player_img.get_height()))
        pygame.draw.rect(window, (52, 235, 128), (self.x + self.player_img.get_height(), self.y, 10, self.player_img.get_height() * (self.health/self.max_health)))

    

class Enemy(Ship):
    COLOR_MAP = {"enemy_1": (ENEMY_1, BULLET_1), "enemy_2": (ENEMY_2, BULLET_2), "enemy_3": (ENEMY_3, BULLET_3), "enemy_4": (ENEMY_4, BULLET_4)}
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.player_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.player_img)

    def move(self, vel):
        self.x -= vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-5, self.y + 70, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


### Main Loop ###

def main():
    running = True
    FPS = 60
    level = 0
    lives = 5
    player_vel = 5
    enemy_vel = 2
    laser_vel = 30
    enemy_laser_vel = 10
    main_font = pygame.font.SysFont("ptmono", 25)
    lost_font = pygame.font.SysFont("ptmono", 50)

    enemies = []
    wave_length = 1
    
    player = Player(200, 384)
    
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0
    # Updating window and diplaying surfaces
    def redraw_window():
        WIN.blit(SPACE_BG, (0,0))
        
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255 ))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255 ))

        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        for enemy in enemies:
            enemy.draw(WIN)
            
        player.draw(WIN)
        
        if lost:
            lost_label = lost_font.render("The aliens got you. RIP", 1, (255, 48, 25))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

            
        pygame.display.update()

    while running:
        clock.tick(FPS)
        redraw_window()
    

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                running = False
                pygame.quit()
                sys.exit()
            else:
                continue
            
        if len(enemies) == 0:
            level += 1
            wave_length += 4
            for i in range(wave_length):
                enemy = Enemy(random.randrange(WIDTH+5, WIDTH+900), random.randrange(50, 600), random.choice(["enemy_1", "enemy_2", "enemy_3", "enemy_4"]))
                enemies.append(enemy)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    pygame.quit()
                    sys.exit()
                    
    
            
        keys = pygame.key.get_pressed()
        player.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_vel
        player.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * player_vel
        player.x = player.x % WIN.get_width()
        player.y = player.y % WIN.get_height()

        if keys[pygame.K_SPACE]:
            player.shoot()
            
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(enemy_laser_vel, player)

            if random.randrange(0, 2*60) == 1 and enemy.x < WIDTH:
                enemy.shoot()
                
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.x + enemy.get_width() < 0:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("ptmono", 50)
    running = True
    while running:
        WIN.blit(SPACE_BG, (0,0))
        title_label = title_font.render("Click to begin", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()
    sys.exit()

main_menu()
