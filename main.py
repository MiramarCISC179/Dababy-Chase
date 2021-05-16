import pygame
import os
import random
import sys
from pygame import mixer

# Initialization 
pygame.font.init()
pygame.init()

WIDTH, HEIGHT = 800, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dababy Chase")

# Load images
police = pygame.image.load(os.path.join("assets", "police.png"))
police_cruiser = pygame.image.load(os.path.join("assets", "police_cruiser.png"))

# Player player
dababy = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
bullet = pygame.image.load(os.path.join("assets", "bullet.png"))
shotshell = pygame.image.load(os.path.join("assets", "shotshell.png"))
money_bullet = pygame.image.load(os.path.join("assets", "money_bullet.png"))

#Start music
bgm = mixer.music.load(os.path.join("assets", ('bgm.wav')))

#Sound Effect
moneyshot = mixer.Sound(os.path.join("assets", "moneyshot.wav"))
hit = mixer.Sound(os.path.join("assets", "hit.wav")) 
gameover_sound = mixer.Sound(os.path.join("assets","gameover.wav"))

#Backgrounds
bkgd = pygame.image.load(os.path.join("assets","road.png"))
scary_bkgd = pygame.image.load(os.path.join("assets","scary_road.png"))
start_menu_bkgd = pygame.image.load(os.path.join("assets","not_scary.png"))
scary = pygame.image.load(os.path.join("assets", "scary.png"))


#Boolean sounds
gameover = False
moneyshot_sound = False


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Base:
    COOLDOWN = 16

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                hit.play()
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
            
            #Shoot sound effect
            moneyshot_sound = True
            if moneyshot_sound == True:
                moneyshot_sound = False
                moneyshot.play()
                pass

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Base):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = dababy
        self.laser_img = money_bullet
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        hit.play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Base):
    COLOR_MAP = {
                "police": (police, bullet),
                "police_cruiser": (police_cruiser, shotshell),
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# Main game 
def main():
    
    # Gui Properties
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)

    # Enemy Properties
    enemies = []
    wave_length = 5
    enemy_vel = 1

    # Player properties
    player_vel = 5
    laser_vel = 5
    player = Player(320, 800)
    lost = None
    lost_count = 0

    # Background properties
    y = 0

    clock = pygame.time.Clock()

    #Music properties
    mixer.music.play(-1)

    def redraw_window():

        # draw text
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)
                  
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        
        #Moving background
        rel_y = y % bkgd.get_rect().height
        WIN.blit(bkgd, (0, rel_y - bkgd.get_rect().height))
        if rel_y < HEIGHT:
            WIN.blit(bkgd, (0, rel_y))
            pass
        y += 7

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 10

        if lost:
            game_over()


        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["police","police_cruiser"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_o]:
            player.health -= 10


        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

# Game over scene
def game_over():
    
    #Function properties
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    
    # Background properties
    y = 0

    # Stop the music
    mixer.music.stop()
    
    # Fading effect
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill((0,0,0))
    for alpha in range(0, 300):
        fade.set_alpha(alpha)
        WIN.blit(fade, (0,0))
        pygame.display.update()
        pygame.time.delay(5)

    # Play this music after above statements
    mixer.music.load(os.path.join("assets", ('pilotredsun_scary.wav')))
    mixer.music.play()


    while run:
        pygame.display.update()

        #Moving background
        rel_y = y % bkgd.get_rect().height
        WIN.blit(scary_bkgd, (0, rel_y - bkgd.get_rect().height))
        if rel_y < HEIGHT:
            WIN.blit(scary_bkgd, (0, rel_y))
            pass
        y += 1
        
        WIN.blit(start_menu_bkgd, (0, 0))

        #Dialog layer 1
        layer1 = title_font.render("You died! Really now, you think this game is", 1, (255,255,255))
        WIN.blit(layer1, (50, 800))

        #Dialog layer 2
        layer2 = title_font.render("going to be easy... [Click to continue]", 1, (255,255,255))
        WIN.blit(layer2, (50, 850))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                #Start the game
                game_over_scene1()

                #Disable this.
                run = False

# VOID SCENE
def game_over_scene1():
        
    #Function properties
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    
    # Background properties
    y = 0

    # Stop the music
    mixer.music.stop()
    mixer.music.load(os.path.join("assets", ('end.wav')))
    mixer.music.play()

    time_end = 0

    while run:
        pygame.display.update()

        #Moving background
        rel_y = y % bkgd.get_rect().height
        WIN.blit(scary_bkgd, (0, rel_y - bkgd.get_rect().height))
        if rel_y < HEIGHT:
            WIN.blit(scary_bkgd, (0, rel_y))
            pass
        y += 1
        
        WIN.blit(scary, (0, 0))

        #layer 1
        layer1 = title_font.render("Y̸̧͔͇͉̻͈̝̳͇͎̫̘̊̓͗͐̓̉͑̃͊̐͑͘͘͝͝ͅŎ̷̡̨̯̹͕̼̬̹̪̻͆̌̈̐͐̓̉͜Û̸̘̟̩̪̼̦̥͆̀̾̆͐͑́", 1, (255,255,255))
        WIN.blit(layer1 , (50, 800))

        #layer 2
        layer2 = title_font.render("S̸̨̃̈́̉́̾̎U̶̱͚̖͚̳̭̩̙̗̪̖̘̣͖͐̈́̀̇̈́̀ͅC̷̩̹͚̞͖̲̳̺̖̼̗̤̍́̏̈́̾̈́̿̃͂̈͜K̸̳̣̝̺̭̻͊̓͛̂́̽͒̈́̕", 1, (255,255,255))
        WIN.blit(layer2 , (50, 850))

        time_end += 0.1

        if time_end > 20:
            pygame.quit()
                

#The main menu
def start_menu():
    
    #Function properties
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    
    # Background properties
    y = 0

    while run:
        
        WIN.blit(start_menu_bkgd, (0, 0))

        title_label = title_font.render("Click to start game!", 1, (255,255,255))
        WIN.blit(title_label, (50, 800))
        
        pygame.display.update()

        #Moving background
        rel_y = y % bkgd.get_rect().height
        WIN.blit(bkgd, (0, rel_y - bkgd.get_rect().height))
        if rel_y < HEIGHT:
            WIN.blit(bkgd, (0, rel_y))
            pass
        y += 7

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                #Fading Effect
                fade = pygame.Surface((WIDTH, HEIGHT))
                fade.fill((0,0,0))
                for alpha in range(0, 300):
                    fade.set_alpha(alpha)
                    WIN.blit(fade, (0,0))
                    pygame.display.update()
                    pygame.time.delay(5)
                
                #Start the game
                main()

                #Disable this.
                run = False

start_menu()