import os
import sys
import pygame
import neat
import random
from pygame import *

pygame.init()

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)

scr_size = (width,height) = (600,150)
FPS = 60
gravity = 0.6

white = (255,255,255)
background_col = (235,235,235)

high_score = 0

gen = 0 

screen = pygame.display.set_mode(scr_size)
clock = pygame.time.Clock()
pygame.display.set_caption("T-Rex Run")

jump_sound = pygame.mixer.Sound('sprites/jump.wav')
die_sound = pygame.mixer.Sound('sprites/die.wav')
checkPoint_sound = pygame.mixer.Sound('sprites/checkPoint.wav')



def load_image(
    name,
    sizex=-1,
    sizey=-1,
    colorkey=None,
    ):

    fullname = os.path.join('sprites', name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return (image, image.get_rect())

def load_sprite_sheet(
        sheetname,
        nx,
        ny,
        scalex = -1,
        scaley = -1,
        colorkey = None,
        ):
    fullname = os.path.join('sprites',sheetname)
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()

    sheet_rect = sheet.get_rect()

    sprites = []

    sizex = sheet_rect.width/nx
    sizey = sheet_rect.height/ny

    for i in range(0,ny):
        for j in range(0,nx):
            rect = pygame.Rect((j*sizex,i*sizey,sizex,sizey))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sheet,(0,0),rect)

            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey,RLEACCEL)

            if scalex != -1 or scaley != -1:
                image = pygame.transform.scale(image,(scalex,scaley))

            sprites.append(image)

    sprite_rect = sprites[0].get_rect()

    return sprites,sprite_rect


class Dino():
    """
    Dino class represents a dino
    """
    def __init__(self,sizex=-1,sizey=-1):
        """
        Initialize Dino Object
        :return: None
        """
        self.images,self.rect = load_sprite_sheet('dino.png',5,1,sizex,sizey,-1)
        self.images1,self.rect1 = load_sprite_sheet('dino_ducking.png',2,1,59,sizey,-1)
        self.rect.bottom = int(0.98*height)
        self.rect.left = width/15
        self.image = self.images[0]
        self.top = self.rect.bottom - self.image.get_height()
        self.index = 0
        self.counter = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isBlinking = False
        self.movement = [0,0]
        self.jumpSpeed = 11.5
        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    def draw(self):
        """
        draws dino to screen 
        :return: None
        """
        screen.blit(self.image,self.rect)

    def checkbounds(self):
        """
        check to make sure dino is in bounds
        :return: None
        """
        if self.rect.bottom > int(0.98*height):
            self.rect.bottom = int(0.98*height)
            self.isJumping = False
    
    def get_mask(self): 
        """
        gets mask for current image of dino 
        :return: mask
        """
        return pygame.mask.from_surface(self.image)
    
    def update(self):
        """
        update the picture of the dino on the screen 
        :return: None
        """
        if self.isJumping:
            self.movement[1] = self.movement[1] + gravity

        if self.isJumping:
            self.index = 0
        elif self.isBlinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1)%2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1)%2

        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2 + 2

        if self.isDead:
           self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[(self.index)%2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        if not self.isDead and self.counter % 7 == 6 and self.isBlinking == False:
            self.score += 1
            if self.score % 100 == 0 and self.score != 0:
                if pygame.mixer.get_init() != None:
                    checkPoint_sound.play()

        self.counter = (self.counter + 1)
    

cactus_images = [pygame.image.load(os.path.join("images","cacti" + str(x) + ".png")) for x in range(1,5)]
class Cactus(): 
    """
    Cactus class represents a cactus object
    """
    def __init__(self, x, speed=5): 
        """
        Intialize the cactus 
        :param x: x-coordinate
        :return: None
        """
        self.images = cactus_images
        self.image = self.images[random.randrange(0,4)]
        self.surf = pygame.Surface((self.image.get_width(), self.image.get_height()))
        self.rect = self.surf.get_rect()
        self.rect.bottom = int(0.98*height)
        self.rect.left = width + self.rect.width 
        self.movement = [-1*speed,0]
        self.x = x
    
    def draw(self, win):
        """
        draws cactus onto the screen 
        :param win: pygame screen/display
        :return: None
        """
        win.blit(self.image, self.rect)
    
    def update(self): 
        """
        update the image of the cactus on the screen 
        :return: None
        """
        self.rect = self.rect.move(self.movement)
        #if self.rect.right < 0:
        #    self.kill()
    
    def collide(self, dino): 
        """
        checks to see if the cactus collided with cactus 
        :param dino: dino object 
        :return: Boolean
        """
        dino_mask = dino.get_mask()
        catcus_mask = pygame.mask.from_surface(self.image)
        offset = (self.rect.left - dino.rect.left, self.rect.bottom - round(dino.rect.bottom))
        return dino_mask.overlap(catcus_mask, offset)

ptera_images = [pygame.image.load(os.path.join("images","ptera" + str(x) + ".png")) for x in range(1,3)]
class Ptera(): 
    """
    Ptera class represents ptera object
    """
    def __init__(self, x, speed=5): 
        """
        Initialize a Ptera object
        :return: None
        """
        self.images = ptera_images
        self.image = self.images[0]
        self.surf = pygame.Surface((self.image.get_width(), self.image.get_height()))
        self.rect = self.surf.get_rect()
        self.ptera_height = [height*0.98,height*0.65,height*0.30]
        self.rect.centery = self.ptera_height[random.randrange(0,3)]
        self.rect.bottom =  self.rect.centery
        self.rect.left = width + self.rect.width 
        self.movement = [-1*speed,0]
        self.index = 0
        self.counter = 0 
        self.x = x
    
    def draw(self, win):
        """
        draws Ptera to the screen 
        :param win: pygame screen/display
        :return: None 
        """
        win.blit(self.image, self.rect)
    
    def update(self):
        """
        update the image of the ptera on the screen 
        :return: None
        """
        if self.counter % 10 == 0:
            self.index = (self.index+1)%2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)

    def collide(self, dino):
        """
        checks to see if the dino collided with ptera 
        :param dino: dino object
        :return: Boolean 
        """
        dino_mask = dino.get_mask()
        ptera_mask = pygame.mask.from_surface(self.image)
        offset = (self.rect.left - dino.rect.left, self.rect.centery - round(dino.rect.bottom ))
        offset_t = (self.rect.left - dino.rect.left, self.rect.centery - round(dino.rect.top ))
        return dino_mask.overlap(ptera_mask, offset) or dino_mask.overlap(ptera_mask, offset_t)

class Ground():
    """
    Ground class represents a ground object
    """
    def __init__(self,speed=-5):
        """
        Initalize the ground object
        :return: None
        """
        self.image,self.rect = load_image('ground.png',-1,-1,-1)
        self.image1,self.rect1 = load_image('ground.png',-1,-1,-1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        """ 
        draw the ground onto the screen 
        :return: None
        """
        screen.blit(self.image,self.rect)
        screen.blit(self.image1,self.rect1)

    def update(self):
        """
        update the image of the ground on the screen
        :return: None
        """
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right


cloud_image = pygame.image.load(os.path.join("images","cloud.png"))
class Cloud(): 
    """
    Cloud class represents a cloud
    """
    def __init__(self, x, y): 
        """
        Initialize a cloud object 
        :param x: x-coordinate 
        :param y: y-coordinate 
        :return: None
        """
        self.image = cloud_image
        self.surf = pygame.Surface((self.image.get_width(), self.image.get_height()))
        self.rect = self.surf.get_rect()
        self.speed = 1  
        self.rect.left = x
        self.rect.top = y
        self.movement = [-1*self.speed,0]
    
    def draw(self, win): 
        """
        draws cloud onto the screen 
        :param win: pygame screen/display
        :return: None
        """
        win.blit(self.image, self.rect)
    
    def update(self): 
        """ 
        updates the image of the cloud on the screen
        :return: None
        """
        self.rect = self.rect.move(self.movement)


def draw_window(screen, dinos, obstacles, base,score, gen):
    """
    draws window for main game loop
    :param screen: screen of pygame 
    :param dinos: list of dino objects 
    :param obstacles: list of obstacles
    :param base: a ground object 
    :param score: the current score 
    :param gen: the current generation
    :return: None
    """
  
    screen.fill(background_col)

    for obstacle in obstacles: 
        obstacle.draw(screen)

    for dino in dinos: 
        dino.draw()
    base.draw()

    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    screen.blit(score_label, (600 - score_label.get_width() - 15, 10))
    
    score_label = STAT_FONT.render("Alive: " + str(len(dinos)),1,(255,255,255))
    screen.blit(score_label, (width/2 - 80, 10))

    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    screen.blit(score_label, (10, 10))
    
    pygame.display.update()

def eval_genomes(genomes, config): 
    """
    runs the simulation of the current population of
    dinos and sets their fitness based on the distance they
    reach in the game.
    """

    global gen 
    gen+=1

    nets = [] 
    ge = [] 
    dinos  = []

    for genome_id, genome in genomes: 
        genome.fitness = 0 
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        dinos.append(Dino(44, 47))
        ge.append(genome)


    gamespeed = 4
    new_ground = Ground(-1*gamespeed)
    obstacles = []
    obstacles.append(Cactus(100))
    
    running = True 
    score = 0 
    while running and len(dinos) > 0: 
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit() 
                sys.exit()
                break

        for x, dino in enumerate(dinos): 
            ge[x].fitness += 0.1  # give each dino a fitness of 0.1 for each frame it stays alive
            dino.update()

            #send the center x postion of dino, send the center y postion of dino, send the center x postion of obstacle, send the center y postion of obstacle, the difference in the x position of the dino and obstacle, and the difference in the y position of dino and obstacle
            output = nets[dinos.index(dino)].activate((dino.rect.centerx, dino.rect.centery, obstacles[0].rect.centerx, obstacles[0].rect.centery, abs(dino.rect.centerx - obstacles[0].rect.centerx), abs(dino.rect.centery - obstacles[0].rect.centery)))
            #we use tanh activation to decide what to do as the outputs will be between -1 and 1
            if output[0] > 0.5: #the AI first decides whether to make a move
                if output[1] > 0.5 and not dino.isDucking: #the AI then decides wether to jump 
                    dino.isJumping = True 
                    dino.movement[1] = -1*dino.jumpSpeed

                elif output[2] > 0.5 and not dino.isJumping:  #the AI also decides wether to duck 
                    dino.isDucking = True 
           
            else: #if no action is taken we want the dino to just run
                dino.isDucking = False 
                dino.isJumping = False 

    
        new_ground.update()
        
        add_obstacle = False 
        rem = [] 
        # check for collision
        for obstacle in obstacles: 
            obstacle.update()
            for dino in dinos: 

                if obstacle.collide(dino) or dino.rect.top <= 0: 
                    dino.isDead = True #to weed out the losers
                    ge[dinos.index(dino)].fitness -= 1 
                    nets.pop(dinos.index(dino))
                    ge.pop(dinos.index(dino))
                    dinos.pop(dinos.index(dino))

            if obstacle.rect.left < -obstacle.image.get_width():
                add_obstacle = True 
                rem.append(obstacle)
        
        #add a new obstacle on the screen and update score 
        if add_obstacle: 
            score += 1
            for genome in ge: 
                genome.fitness+=5 
    
            r = random.randrange(0,4)
            if r == 0: 
                obstacles.append(Cactus(100))
            else: 
                obstacles.append(Ptera(100))

        #remove obstacles not seen on screen
        for r in rem: 
            obstacles.remove(r)


        #remove dead dinos
        for dino in dinos: 
            if dino.isDead: 
                nets.pop(dinos.index(dino))
                ge.pop(dinos.index(dino))
                dinos.pop(dinos.index(dino))
        
    
        draw_window(screen, dinos, obstacles, new_ground, score, gen)



def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.population.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 100)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)

