import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

screen_width = 1350
screen_height = 850
level = 1
max_levels = 3
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("FruitFrenzy")

# load images
bg_img = pygame.image.load('img/background.png')
restart_img = pygame.image.load("img/restart.png")
start_img = pygame.image.load("img/play.png")
exit_img = pygame.image.load("img/close.png")

# load sound effects
pygame.mixer.music.load('sound/background.wav')
pygame.mixer.music.play(-1,0.0, 4950)
coin_sound = pygame.mixer.Sound('sound/coin.wav')
coin_sound.set_volume(0.5)
jump_sound = pygame.mixer.Sound('sound/jump.wav')
jump_sound.set_volume(0.5)
gameover_sound = pygame.mixer.Sound('sound/gameover.wav')
gameover_sound.set_volume(0.5)

#define font
font = pygame.font.SysFont('Bauhaus 93', 80)
font_score = pygame.font.SysFont('Rodaja', 40)


# define game variables
tile_size = 50
game_over = 0
main_menu = True
score = 0 

#define colors
white = (255,255,255)
green = (34,139,34)

# draw grid function, was used to help genereate the terrain
def draw_grid():
    for line in range(0, 27):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))


#function to reset level
def reset_level(level):
    redApple.reset(100, screen_height - 130, 'img/redApple.png')
    worm_group.empty()
    lava_group.empty()
    found_group.empty()
    platform_group.empty()

    #load in level data and create world
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

class Button():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False 

    def draw(self):
        action = False 


        # get mouse position 
        pos = pygame.mouse.get_pos()
        # check mouseover and clicked conditions 
        if self.rect.collidepoint(pos): # the mouse is over the button 
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: # if pressed and looking for the left button so 0
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0: # the zero means that when you leave it and come pack
            self.clicked = False

        # draw button 
        screen.blit(self.image, self.rect) 

        return action

class Player():
    def __init__(self,x,y,img_path):
        self.reset(x, y, img_path)


    def update(self , game_over): 
        dx = 0
        dy = 0
        col_thresh = 20

        if game_over == 0:
            #calculate new player position 
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_sound.play()
                self.vertical_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False: 
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -=5
            if key[pygame.K_RIGHT]:
                dx +=5
        

            #add gravity
            self.vertical_y +=1
            if self .vertical_y > 10:
                self.vertical_y = 10
            dy += self.vertical_y

            #check collision at new position 
            self.in_air = True
            for tile in world.tile_list:
                #check for x direction collision
                if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                    dx=0
                #check for y direction collision 
                if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                    #check if below the ground (jumping)
                    if self.vertical_y < 0: 
                        dy = tile[1].bottom - self.rect.top #this makes sure the player jumps until the top of it bumps the bottom of a dirt block
                        self.vertical_y=0
                    #check if above the ground (falling)
                    elif self.vertical_y >0:
                        dy = tile[1].top - self.rect.bottom 
                        self.vertical_y=0
                        self.in_air = False

            #check for collision with plaforms 
            for platform in platform_group:
                #collision in the x direction 
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                #collision in the y direction 
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below plaform 
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vertical_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # check if above platfrom 
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    #move sideways with platform 
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction   

            #check for collision with enemies
            if pygame.sprite.spritecollide(self,worm_group, False):
                game_over = -1
                gameover_sound.play()
            #check for collision with enemies
            if pygame.sprite.spritecollide(self,lava_group, False):
                game_over = -1  
                gameover_sound.play()

             #check for collision with found child
            if pygame.sprite.spritecollide(self,found_group, False):
                game_over = 1  

            #adjust player position
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER', font, green, (screen_width//2) - 195, screen_height //2)
            if self.rect.y > 200:
                self.rect.y -= 5
        
        #draw player onto screen
        screen.blit(self.image,self.rect)

        return game_over
    def reset(self,x,y,img_path):
        img = pygame.image.load(img_path) #this loads the image
        self.image = pygame.transform.scale(img,(60,80)) 
        self.rect = self.image.get_rect()   #th8is gets the rect of the image
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vertical_y = 0
        self.jumped = False
        self.dead_image = pygame.image.load('img/ghost.png')
        self.in_air = True

class World():
    def __init__(self, data):

        self.tile_list = []

        dirt = pygame.image.load('img/dirt.jpg')
        grass = pygame.image.load('img/grass.png')
        line_counter = 0
        for line in data:
            columnn_counter = 0
            for tile in line:
                if tile == 1:
                    img = pygame.transform.scale(dirt, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = columnn_counter * tile_size
                    img_rect.y = line_counter * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile ==2:
                    img = pygame.transform.scale(grass, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = columnn_counter * tile_size
                    img_rect.y = line_counter * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    worm = Enemy(columnn_counter *  tile_size, line_counter * tile_size + 20)
                    worm_group.add(worm)
                if tile == 4:
                     lava = Lava(columnn_counter *  tile_size, line_counter * tile_size + (tile_size//2))
                     lava_group.add(lava)
                if tile == 5:
                     coin = Coin(columnn_counter *  tile_size + (tile_size // 2), line_counter * tile_size + (tile_size//2))
                     coin_group.add(coin)                        
                if tile == 6: 
                    #child = FoundChild(columnn_counter *  tile_size, line_counter * tile_size + (tile_size//2))
                    child = FoundChild(columnn_counter *  tile_size, line_counter * tile_size + (tile_size//2))
                    found_group.add(child)
                if tile == 7:
                    platform = Platform(columnn_counter *  tile_size, line_counter * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 8:
                    platform = Platform(columnn_counter *  tile_size, line_counter * tile_size, 0, 1)
                    platform_group.add(platform)
                columnn_counter += 1
            line_counter += 1

    def create(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            

class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/worm.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0
    def update(self):  
        self.rect.x += self.move_direction 
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *=  -1 
            self.move_counter = 0
            # self.move_counter *= -1  

#creating plaform
class Platform(pygame.sprite.Sprite):
    def __init__(self,x,y,move_x,move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/platform.png")
        self.image = pygame.transform.scale(img, (tile_size , tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):  
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *=  -1 
            self.move_counter = 0
            # self.move_counter *= -1  



#creating lava
class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/lava.png")
        self.image = pygame.transform.scale(img, (tile_size,tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/coin.png")
        self.image = pygame.transform.scale(img, (tile_size // 2,tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)


class FoundChild(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/babyApple.png")
        self.image = pygame.transform.scale(img, (tile_size//2,tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y




redApple = Player(100, screen_height - 150, 'img/redApple.png')

worm_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
found_group = pygame.sprite.Group()

#create coin for score
mini_coin = Coin(tile_size //2, tile_size //2)       
coin_group.add(mini_coin)

#loading the level terrian and creating the world based off of that
if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)         
world = World(world_data)
# create buttons 
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100 , restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

running = True
while running:

    screen.blit(bg_img, (0, 0))

    if main_menu == True:
        if start_button.draw():
            main_menu = False
        if exit_button.draw():
            running = False
    else:  

        world.create()

        if game_over == 0:
            worm_group.update()
            platform_group.update()
            #update score
            if pygame.sprite.spritecollide(redApple, coin_group, True):
                score += 1
                coin_sound.play()
            draw_text('X ' + str(score), font_score, white, tile_size - 15, 15)  
    

       #drawing all the differnt things on the screen
        worm_group.draw(screen)

        platform_group.draw(screen)

        lava_group.draw(screen)

        coin_group.draw(screen)

        found_group.draw(screen)

        game_over = redApple.update(game_over)

        # -1 when means when the player died
        if game_over == -1:
                if restart_button.draw():
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

            #if player has completed the level
        if game_over == 1:
            #reset game and go to next level
                level += 1
                if level <= max_levels:
                    #reset level
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                else:
                    draw_text("WINNER", font, green, (screen_width//2) - 145, screen_height //2)
                    if restart_button.draw():
                        level = 1
                        #reset level
                        world_data = []
                        world = reset_level(level)
                        game_over = 0
                        score = 0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()
